import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from deerflow.config.paths_multi_tenant import MultiTenantPaths
from packages.harness.deerflow.data.tenant_queries import TenantAwareStorage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/threads", tags=["threads"])


class ThreadCreateRequest(BaseModel):
    """Request model for creating a thread."""

    metadata: dict[str, Any] | None = None


class ThreadResponse(BaseModel):
    """Response model for thread data."""

    id: str
    tenant_id: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any]
    message_count: int
    status: str


class ThreadDeleteResponse(BaseModel):
    """Response model for thread cleanup."""

    success: bool
    message: str


def _get_tenant_storage(request: Request) -> TenantAwareStorage:
    """Get TenantAwareStorage for the current request's tenant."""
    tenant_id = getattr(request.state, "tenant_id", "default")
    paths = MultiTenantPaths(tenant_id=tenant_id)
    return TenantAwareStorage(paths)


@router.post("", response_model=ThreadResponse)
async def create_thread(request: Request, body: ThreadCreateRequest) -> ThreadResponse:
    """Create a new thread for the current tenant.

    The thread_id is auto-generated as a UUID.
    """
    import uuid

    tenant_storage = _get_tenant_storage(request)
    thread_id = str(uuid.uuid4())

    try:
        thread_info = tenant_storage.create_thread(thread_id, body.metadata)
        return ThreadResponse(**thread_info)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("", response_model=list[ThreadResponse])
async def list_threads(request: Request, limit: int = 100, offset: int = 0) -> list[ThreadResponse]:
    """List all threads for the current tenant."""
    tenant_storage = _get_tenant_storage(request)
    threads = tenant_storage.list_threads(limit=limit, offset=offset)
    return [ThreadResponse(**t) for t in threads]


@router.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread(request: Request, thread_id: str) -> ThreadResponse:
    """Get thread information for the current tenant."""
    tenant_storage = _get_tenant_storage(request)
    thread_info = tenant_storage.get_thread(thread_id)

    if not thread_info:
        raise HTTPException(status_code=404, detail="Thread not found")

    return ThreadResponse(**thread_info)


@router.delete("/{thread_id}", response_model=ThreadDeleteResponse)
async def delete_thread_data(request: Request, thread_id: str) -> ThreadDeleteResponse:
    """Delete local persisted filesystem data for a thread.

    This endpoint only cleans DeerFlow-managed thread directories. LangGraph
    thread state deletion remains handled by the LangGraph API.

    Only the owning tenant can delete their threads.
    """
    tenant_storage = _get_tenant_storage(request)
    deleted = tenant_storage.delete_thread(thread_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")

    logger.info("Deleted local thread data for tenant %s, thread %s", tenant_storage.tenant_id, thread_id)
    return ThreadDeleteResponse(success=True, message=f"Deleted thread {thread_id} for tenant {tenant_storage.tenant_id}")
