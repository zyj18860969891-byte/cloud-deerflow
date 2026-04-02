"""Tenant-aware data query helpers for file-based storage.

Since DeerFlow uses filesystem for data persistence (not a traditional database),
this module provides query-like functions that respect tenant isolation.
"""

import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ..config.paths_multi_tenant import MultiTenantPaths

# Safe thread ID pattern (same as in paths.py)
_SAFE_THREAD_ID_RE = re.compile(r"^[A-Za-z0-9_\-]+$")


class TenantAwareStorage:
    """
    Tenant-aware storage operations.

    Provides methods for creating, reading, updating, and deleting thread data
    with automatic tenant isolation.
    """

    def __init__(self, paths: MultiTenantPaths):
        """Initialize with multi-tenant paths.

        Args:
            paths: MultiTenantPaths instance configured for a specific tenant
        """
        self.paths = paths
        self.tenant_id = paths.tenant_id

    def create_thread(self, thread_id: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Create a new thread for this tenant.

        Args:
            thread_id: Unique thread identifier (will be validated)
            metadata: Optional metadata to store with thread

        Returns:
            Thread info dictionary
        """
        thread_dir = self.paths.thread_dir(thread_id)

        if thread_dir.exists():
            raise ValueError(f"Thread {thread_id} already exists for tenant {self.tenant_id}")

        # Create thread directory structure
        self.paths.ensure_thread_dirs(thread_id)

        # Create thread metadata file
        thread_info = {"id": thread_id, "tenant_id": self.tenant_id, "created_at": datetime.now(UTC).isoformat() + "Z", "updated_at": datetime.now(UTC).isoformat() + "Z", "metadata": metadata or {}, "message_count": 0, "status": "idle"}

        metadata_file = thread_dir / "thread.json"
        with open(metadata_file, "w") as f:
            json.dump(thread_info, f, indent=2)

        return thread_info

    def get_thread(self, thread_id: str) -> dict[str, Any] | None:
        """Get thread information.

        Args:
            thread_id: Thread identifier

        Returns:
            Thread info dict if exists, None otherwise
        """
        thread_dir = self.paths.thread_dir(thread_id)
        metadata_file = thread_dir / "thread.json"

        if not metadata_file.exists():
            return None

        with open(metadata_file) as f:
            thread_info = json.load(f)

        # Verify tenant ownership
        if thread_info.get("tenant_id") != self.tenant_id:
            raise PermissionError(f"Thread {thread_id} does not belong to tenant {self.tenant_id}")

        return thread_info

    def list_threads(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        """List all threads for this tenant.

        Args:
            limit: Maximum number of threads to return
            offset: Number of threads to skip

        Returns:
            List of thread info dictionaries
        """
        tenant_threads_dir = self.paths.get_tenant_base_dir()
        if not tenant_threads_dir.exists():
            return []

        thread_dirs = [d for d in tenant_threads_dir.iterdir() if d.is_dir() and _SAFE_THREAD_ID_RE.match(d.name)]

        # Sort by creation time (directory mtime)
        thread_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)

        threads = []
        for thread_dir in thread_dirs[offset : offset + limit]:
            metadata_file = thread_dir / "thread.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    thread_info = json.load(f)
                threads.append(thread_info)

        return threads

    def delete_thread(self, thread_id: str) -> bool:
        """Delete a thread and all its data.

        Args:
            thread_id: Thread to delete

        Returns:
            True if deleted, False if not found
        """
        thread_dir = self.paths.thread_dir(thread_id)

        if not thread_dir.exists():
            return False

        # Verify tenant ownership before deletion
        metadata_file = thread_dir / "thread.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                thread_info = json.load(f)
            if thread_info.get("tenant_id") != self.tenant_id:
                raise PermissionError(f"Cannot delete thread {thread_id}: does not belong to tenant {self.tenant_id}")

        shutil.rmtree(thread_dir)
        return True

    def update_thread_metadata(self, thread_id: str, metadata: dict[str, Any]) -> dict[str, Any] | None:
        """Update thread metadata.

        Args:
            thread_id: Thread identifier
            metadata: New metadata dict (will be merged)

        Returns:
            Updated thread info, or None if thread not found
        """
        thread_info = self.get_thread(thread_id)
        if not thread_info:
            return None

        # Merge metadata
        thread_info["metadata"].update(metadata)
        thread_info["updated_at"] = datetime.now(UTC).isoformat() + "Z"

        # Save
        thread_dir = self.paths.thread_dir(thread_id)
        metadata_file = thread_dir / "thread.json"
        with open(metadata_file, "w") as f:
            json.dump(thread_info, f, indent=2)

        return thread_info

    def increment_message_count(self, thread_id: str) -> int | None:
        """Increment message count for a thread.

        Args:
            thread_id: Thread identifier

        Returns:
            New message count, or None if thread not found
        """
        thread_info = self.get_thread(thread_id)
        if not thread_info:
            return None

        thread_info["message_count"] += 1
        thread_info["updated_at"] = datetime.now(UTC).isoformat() + "Z"

        thread_dir = self.paths.thread_dir(thread_id)
        metadata_file = thread_dir / "thread.json"
        with open(metadata_file, "w") as f:
            json.dump(thread_info, f, indent=2)

        return thread_info["message_count"]

    def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics for this tenant.

        Returns:
            Dict with thread_count, total_size, etc.
        """
        tenant_threads_dir = self.paths.get_tenant_base_dir()
        if not tenant_threads_dir.exists():
            return {
                "tenant_id": self.tenant_id,
                "thread_count": 0,
                "total_size_bytes": 0,
                "oldest_thread": None,
                "newest_thread": None,
            }

        thread_dirs = [d for d in tenant_threads_dir.iterdir() if d.is_dir() and _SAFE_THREAD_ID_RE.match(d.name)]

        total_size = 0
        mtimes = []
        for thread_dir in thread_dirs:
            # Calculate directory size
            for file in thread_dir.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
            mtimes.append(thread_dir.stat().st_mtime)

        return {
            "tenant_id": self.tenant_id,
            "thread_count": len(thread_dirs),
            "total_size_bytes": total_size,
            "oldest_thread": min(mtimes) if mtimes else None,
            "newest_thread": max(mtimes) if mtimes else None,
        }


# Helper function to get storage for a tenant
def get_tenant_storage(tenant_id: str, base_dir: Path | None = None) -> TenantAwareStorage:
    """Get TenantAwareStorage instance for a tenant.

    Args:
        tenant_id: Tenant identifier
        base_dir: Optional base directory (defaults to DEER_FLOW_HOME or .deer-flow)

    Returns:
        TenantAwareStorage instance
    """
    paths = MultiTenantPaths(base_dir=base_dir, tenant_id=tenant_id)
    return TenantAwareStorage(paths)
