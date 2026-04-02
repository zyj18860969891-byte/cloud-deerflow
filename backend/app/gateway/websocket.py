"""WebSocket handler for real-time usage updates."""

import json
import asyncio
from typing import Set
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends
from sqlalchemy.orm import Session

from deerflow.services.database import get_session
from deerflow.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/ws", tags=["websocket"])


# Store active WebSocket connections per tenant
class ConnectionManager:
    """Manage WebSocket connections per tenant."""
    
    def __init__(self):
        self.active_connections: dict[str, Set[WebSocket]] = {}
    
    async def connect(self, tenant_id: str, websocket: WebSocket):
        """Add a new WebSocket connection."""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
    
    def disconnect(self, tenant_id: str, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
    
    async def broadcast(self, tenant_id: str, message: dict):
        """Send message to all connections for a tenant."""
        if tenant_id not in self.active_connections:
            return
        
        # Send to all connections, remove failed ones
        disconnected = set()
        for connection in self.active_connections[tenant_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Clean up failed connections
        for connection in disconnected:
            self.disconnect(tenant_id, connection)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/usage")
async def websocket_usage_endpoint(
    websocket: WebSocket,
    db: Session = Depends(get_session)
):
    """WebSocket endpoint for real-time usage updates."""
    
    # Get tenant ID from headers or query params
    tenant_id = None
    
    # Try to get from headers
    headers = dict(websocket.headers)
    tenant_id = headers.get("x-tenant-id")
    
    # Try to get from query params
    if not tenant_id:
        query_params = websocket.query_params
        tenant_id = query_params.get("tenant_id")
    
    if not tenant_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="tenant_id required")
        return
    
    # Connect
    await manager.connect(tenant_id, websocket)
    
    try:
        service = SubscriptionService(db)
        
        while True:
            # Receive message from client (keep connection alive)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle ping/pong or requests
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.startswith("get_usage"):
                    # Send current usage metrics
                    metrics = service.get_usage_metrics(tenant_id)
                    await websocket.send_json({
                        "type": "usage",
                        "data": metrics,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Send periodic update even if no client message
                metrics = service.get_usage_metrics(tenant_id)
                await websocket.send_json({
                    "type": "usage",
                    "data": metrics,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(tenant_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(tenant_id, websocket)
        await websocket.close(code=status.WS_1011_SERVER_ERROR)


async def broadcast_usage_update(tenant_id: str, metrics: dict):
    """Broadcast usage update to all connections of a tenant."""
    message = {
        "type": "usage",
        "data": metrics,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await manager.broadcast(tenant_id, message)
