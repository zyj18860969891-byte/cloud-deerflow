"""Multi-tenant aware path configuration for DeerFlow.

Extends the standard Paths class to include tenant isolation in filesystem paths.
"""

from pathlib import Path

from .paths import _SAFE_THREAD_ID_RE
from .paths import Paths as BasePaths


class MultiTenantPaths(BasePaths):
    """
    Multi-tenant aware path configuration.

    Extends Paths to include tenant_id in all thread-related paths:
        {base_dir}/threads/{tenant_id}/{thread_id}/

    This ensures complete data isolation between tenants at the filesystem level.
    """

    def __init__(self, base_dir: str | Path | None = None, tenant_id: str = "default") -> None:
        """Initialize multi-tenant paths.

        Args:
            base_dir: Base directory for all data
            tenant_id: Tenant identifier (used in path construction)

        Raises:
            ValueError: If tenant_id contains invalid characters
        """
        super().__init__(base_dir)

        # Validate tenant_id
        if not _SAFE_THREAD_ID_RE.match(tenant_id):
            raise ValueError(f"Invalid tenant_id {tenant_id!r}: only alphanumeric characters, hyphens, and underscores are allowed.")
        self.tenant_id = tenant_id

    def thread_dir(self, thread_id: str) -> Path:
        """
        Host path for a thread's data directory.
        Host: `{base_dir}/threads/{tenant_id}/{thread_id}/`
        Sandbox: `/mnt/user-data/` (mounted from this directory)

        Overrides base class to include tenant_id in path.
        """
        if not _SAFE_THREAD_ID_RE.match(thread_id):
            raise ValueError(f"Invalid thread_id {thread_id!r}: only alphanumeric characters, hyphens, and underscores are allowed.")
        if not _SAFE_THREAD_ID_RE.match(self.tenant_id):
            raise ValueError(f"Invalid tenant_id {self.tenant_id!r}: only alphanumeric characters, hyphens, and underscores are allowed.")
        return self.base_dir / "threads" / self.tenant_id / thread_id

    def get_thread_paths(self, thread_id: str) -> dict[str, Path]:
        """
        Get all standard paths for a thread.

        Returns:
            Dictionary with keys: thread_dir, work_dir, uploads_dir, outputs_dir, acp_workspace, user_data_dir
        """
        return {
            "thread_dir": self.thread_dir(thread_id),
            "work_dir": self.sandbox_work_dir(thread_id),
            "uploads_dir": self.sandbox_uploads_dir(thread_id),
            "outputs_dir": self.sandbox_outputs_dir(thread_id),
            "acp_workspace": self.acp_workspace_dir(thread_id),
            "user_data_dir": self.sandbox_user_data_dir(thread_id),
        }

    def list_tenant_threads(self) -> list[str]:
        """
        List all thread IDs for the current tenant.

        Returns:
            List of thread directory names under the tenant's thread directory
        """
        tenant_threads_dir = self.base_dir / "threads" / self.tenant_id
        if not tenant_threads_dir.exists():
            return []

        return [d.name for d in tenant_threads_dir.iterdir() if d.is_dir() and _SAFE_THREAD_ID_RE.match(d.name)]

    def delete_tenant_thread(self, thread_id: str) -> None:
        """
        Delete a specific thread's data for this tenant.

        Args:
            thread_id: Thread ID to delete

        Raises:
            ValueError: If thread_id or tenant_id is invalid
            PermissionError: If trying to delete a thread outside tenant's scope
        """
        if not _SAFE_THREAD_ID_RE.match(thread_id):
            raise ValueError(f"Invalid thread_id: {thread_id}")

        thread_dir = self.thread_dir(thread_id)

        # Additional safety check: ensure the thread directory is actually under the tenant's directory
        expected_parent = self.base_dir / "threads" / self.tenant_id
        if not thread_dir.parent.resolve().samefile(expected_parent.resolve()):
            raise PermissionError(f"Thread {thread_id} does not belong to tenant {self.tenant_id}")

        if thread_dir.exists():
            import shutil

            shutil.rmtree(thread_dir)

    def get_tenant_base_dir(self) -> Path:
        """Get the base directory for this tenant's data."""
        return self.base_dir / "threads" / self.tenant_id

    def ensure_tenant_dirs(self) -> None:
        """Ensure tenant's base thread directory exists."""
        tenant_dir = self.get_tenant_base_dir()
        tenant_dir.mkdir(parents=True, exist_ok=True)
        tenant_dir.chmod(0o755)
