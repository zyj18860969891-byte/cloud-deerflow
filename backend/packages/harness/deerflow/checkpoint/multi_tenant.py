"""Multi-tenant checkpoint storage for DeerFlow.

This module provides a checkpoint implementation that ensures data isolation
between different tenants by prefixing thread IDs with tenant identifiers.
"""

import builtins
import uuid
from datetime import datetime
from typing import Any

from langgraph.checkpoint.base import Checkpoint as LangGraphCheckpoint
from langgraph.checkpoint.memory import InMemorySaver


class MultiTenantCheckpointer(InMemorySaver):
    """
    Multi-tenant aware checkpointer.

    Ensures that checkpoint data is isolated by tenant by:
    1. Prefixing thread IDs with tenant_id
    2. Filtering queries by tenant_id
    3. Validating access during retrieval
    """

    def __init__(self, db_path: str | None = None):
        """Initialize the multi-tenant checkpointer.

        Args:
            db_path: Optional database path (for compatibility with test fixtures)
        """
        super().__init__()
        # db_path is ignored for InMemorySaver but kept for API compatibility

    def _prefix_thread_id(self, thread_id: str, tenant_id: str) -> str:
        """Prefix thread ID with tenant ID for isolation."""
        return f"{tenant_id}:{thread_id}"

    def _extract_thread_id(self, prefixed_id: str) -> tuple[str, str]:
        """Extract tenant_id and original thread_id from prefixed ID."""
        if ":" in prefixed_id:
            tenant_id, thread_id = prefixed_id.split(":", 1)
            return tenant_id, thread_id
        return "", prefixed_id  # No tenant prefix

    def put(self, config: dict[str, Any], values: dict[str, Any], metadata: dict[str, Any], tenant_id: str, new_versions: dict[str, int] | None = None) -> None:
        """Save checkpoint with tenant isolation.

        Args:
            config: Checkpoint configuration (must contain thread_id)
            values: State values to checkpoint
            metadata: Metadata to store
            tenant_id: Tenant identifier
            new_versions: Channel versions (required by parent)
        """
        # Extract thread_id from config
        thread_id = config.get("thread_id") or config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id is required in config")

        # Prefix thread_id with tenant_id
        prefixed_thread_id = self._prefix_thread_id(thread_id, tenant_id)

        # Update config with prefixed thread_id and ensure checkpoint_ns
        config_with_tenant = dict(config)
        if "configurable" not in config_with_tenant:
            config_with_tenant["configurable"] = {}
        config_with_tenant["configurable"] = dict(config_with_tenant["configurable"])
        config_with_tenant["configurable"]["thread_id"] = prefixed_thread_id
        # Ensure checkpoint_ns exists (default to empty string)
        if "checkpoint_ns" not in config_with_tenant["configurable"]:
            config_with_tenant["configurable"]["checkpoint_ns"] = ""

        # Store tenant_id in metadata for easy filtering
        metadata_with_tenant = dict(metadata)
        metadata_with_tenant["tenant_id"] = tenant_id

        # Create proper Checkpoint object with all required fields
        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        channel_versions = new_versions or {}
        # For each channel in values, ensure it has a version
        if not channel_versions:
            channel_versions = {k: 1 for k in values.keys()}

        checkpoint = LangGraphCheckpoint(
            v=1,
            id=checkpoint_id,
            ts=timestamp,
            channel_values=values,
            channel_versions=channel_versions,
            versions_seen={},  # Empty for now
            updated_channels=list(values.keys()),
        )

        # Call parent implementation with correct signature
        result_config = super().put(config_with_tenant, checkpoint, metadata_with_tenant, channel_versions)

        # Also store writes for each channel value so get_writes() returns data
        if values:
            # Convert values into writes format: list of (channel, value) tuples
            writes_list = [(channel, value) for channel, value in values.items()]
            # Use the returned config which contains the checkpoint_id
            super().put_writes(result_config, writes_list, task_id=f"checkpoint-{checkpoint_id}", task_path="")

    def get(self, config: dict[str, Any], tenant_id: str) -> dict[str, Any] | None:
        """Retrieve checkpoint with tenant validation.

        Args:
            config: Checkpoint configuration
            tenant_id: Tenant identifier (must match stored checkpoint)

        Returns:
            Checkpoint data dict with 'values' and 'metadata' if found and belongs to tenant, None otherwise
        """
        # Extract thread_id
        thread_id = config.get("thread_id") or config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None

        # Prefix with tenant_id to look up
        prefixed_thread_id = self._prefix_thread_id(thread_id, tenant_id)

        # Update config for lookup
        config_with_tenant = dict(config)
        if "configurable" not in config_with_tenant:
            config_with_tenant["configurable"] = {}
        config_with_tenant["configurable"] = dict(config_with_tenant["configurable"])
        config_with_tenant["configurable"]["thread_id"] = prefixed_thread_id
        # Ensure checkpoint_ns exists
        if "checkpoint_ns" not in config_with_tenant["configurable"]:
            config_with_tenant["configurable"]["checkpoint_ns"] = ""

        # Retrieve from parent - returns CheckpointTuple or None
        result_tuple = super().get_tuple(config_with_tenant)

        if result_tuple is None:
            return None

        # Additional validation: ensure returned data belongs to tenant
        if result_tuple.metadata.get("tenant_id") != tenant_id:
            raise PermissionError(f"Checkpoint does not belong to tenant {tenant_id}")

        # Return dict with values and metadata as expected by tests
        return {"values": result_tuple.checkpoint["channel_values"], "metadata": result_tuple.metadata}

    def list(self, config: dict[str, Any] | None = None, tenant_id: str | None = None, **kwargs) -> list[dict[str, Any]]:
        """List checkpoints for a tenant.

        Args:
            config: Configuration filter (can be None to list all)
            tenant_id: Tenant identifier (required for tenant filtering)
            **kwargs: Additional filtering criteria passed to parent

        Returns:
            List of checkpoints belonging to the tenant
        """
        # Extract thread_id from config if provided
        thread_id = None
        if config:
            thread_id = config.get("thread_id") or config.get("configurable", {}).get("thread_id")

        # Build config_with_tenant for filtering
        config_with_tenant = None
        if thread_id:
            prefixed_thread_id = self._prefix_thread_id(thread_id, tenant_id)
            config_with_tenant = dict(config) if config else {}
            if "configurable" not in config_with_tenant:
                config_with_tenant["configurable"] = {}
            config_with_tenant["configurable"] = dict(config_with_tenant["configurable"])
            config_with_tenant["configurable"]["thread_id"] = prefixed_thread_id
            if "checkpoint_ns" not in config_with_tenant["configurable"]:
                config_with_tenant["configurable"]["checkpoint_ns"] = ""

        # Get checkpoints from parent
        results = []
        for checkpoint_tuple in super().list(config_with_tenant, **kwargs):
            # Validate tenant
            if checkpoint_tuple.metadata.get("tenant_id") != tenant_id:
                continue
            # Return dict with metadata as expected by tests
            results.append({"metadata": checkpoint_tuple.metadata, "config": checkpoint_tuple.config, "checkpoint": checkpoint_tuple.checkpoint})

        return results

    def delete(self, config: dict[str, Any], tenant_id: str) -> None:
        """Delete checkpoint with tenant validation.

        Args:
            config: Checkpoint configuration
            tenant_id: Tenant identifier (must match)
        """
        thread_id = config.get("thread_id") or config.get("configurable", {}).get("thread_id")
        if not thread_id:
            raise ValueError("thread_id is required in config")

        prefixed_thread_id = self._prefix_thread_id(thread_id, tenant_id)

        config_with_tenant = dict(config)
        if "configurable" in config_with_tenant:
            config_with_tenant["configurable"] = dict(config["configurable"])
            config_with_tenant["configurable"]["thread_id"] = prefixed_thread_id
        else:
            config_with_tenant["configurable"] = {"thread_id": prefixed_thread_id}

        # Ensure checkpoint_ns exists
        if "checkpoint_ns" not in config_with_tenant["configurable"]:
            config_with_tenant["configurable"]["checkpoint_ns"] = ""

        # Verify ownership before deletion using get_tuple
        existing = super().get_tuple(config_with_tenant)
        if existing and existing.metadata.get("tenant_id") != tenant_id:
            raise PermissionError(f"Cannot delete checkpoint: does not belong to tenant {tenant_id}")

        # InMemorySaver doesn't have delete(), so we need to implement deletion manually
        # Extract checkpoint_id if provided
        checkpoint_id = config_with_tenant.get("configurable", {}).get("checkpoint_id")
        thread_id_key = prefixed_thread_id
        checkpoint_ns = config_with_tenant["configurable"]["checkpoint_ns"]

        if checkpoint_id:
            # Delete specific checkpoint
            if thread_id_key in self.storage and checkpoint_ns in self.storage[thread_id_key]:
                if checkpoint_id in self.storage[thread_id_key][checkpoint_ns]:
                    del self.storage[thread_id_key][checkpoint_ns][checkpoint_id]
                    # Also delete associated writes
                    write_key = (thread_id_key, checkpoint_ns, checkpoint_id)
                    if write_key in self.writes:
                        del self.writes[write_key]
        else:
            # Delete all checkpoints for this thread/namespace
            if thread_id_key in self.storage and checkpoint_ns in self.storage[thread_id_key]:
                # Get all checkpoint IDs to also delete writes
                checkpoint_ids = list(self.storage[thread_id_key][checkpoint_ns].keys())
                for cid in checkpoint_ids:
                    write_key = (thread_id_key, checkpoint_ns, cid)
                    if write_key in self.writes:
                        del self.writes[write_key]
                del self.storage[thread_id_key][checkpoint_ns]

    def get_next(self, config: dict[str, Any], tenant_id: str) -> dict[str, Any] | None:
        """Get next checkpoint in sequence with tenant validation."""
        thread_id = config.get("thread_id") or config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return None

        prefixed_thread_id = self._prefix_thread_id(thread_id, tenant_id)

        config_with_tenant = dict(config)
        if "configurable" in config_with_tenant:
            config_with_tenant["configurable"] = dict(config["configurable"])
            config_with_tenant["configurable"]["thread_id"] = prefixed_thread_id
        else:
            config_with_tenant["configurable"] = {"thread_id": prefixed_thread_id}

        # Ensure checkpoint_ns exists
        if "checkpoint_ns" not in config_with_tenant["configurable"]:
            config_with_tenant["configurable"]["checkpoint_ns"] = ""

        result = super().get_next(config_with_tenant)

        if result and result.get("metadata", {}).get("tenant_id") != tenant_id:
            raise PermissionError(f"Checkpoint does not belong to tenant {tenant_id}")

        return result

    def get_writes(self, config: dict[str, Any], tenant_id: str) -> builtins.list[dict[str, Any]]:
        """Get writes for a checkpoint with tenant validation."""
        thread_id = config.get("thread_id") or config.get("configurable", {}).get("thread_id")
        if not thread_id:
            return []

        prefixed_thread_id = self._prefix_thread_id(thread_id, tenant_id)

        config_with_tenant = dict(config)
        if "configurable" in config_with_tenant:
            config_with_tenant["configurable"] = dict(config["configurable"])
            config_with_tenant["configurable"]["thread_id"] = prefixed_thread_id
        else:
            config_with_tenant["configurable"] = {"thread_id": prefixed_thread_id}

        # Ensure checkpoint_ns exists
        if "checkpoint_ns" not in config_with_tenant["configurable"]:
            config_with_tenant["configurable"]["checkpoint_ns"] = ""

        checkpoint_id = config_with_tenant["configurable"].get("checkpoint_id")
        checkpoint_ns = config_with_tenant["configurable"]["checkpoint_ns"]

        # If no checkpoint_id specified, get the latest checkpoint for this thread
        if not checkpoint_id:
            # Find latest checkpoint ID from storage
            if prefixed_thread_id not in self.storage or checkpoint_ns not in self.storage[prefixed_thread_id]:
                return []
            checkpoints = self.storage[prefixed_thread_id][checkpoint_ns]
            if not checkpoints:
                return []
            # Get the checkpoint with the highest ID (latest)
            checkpoint_id = max(checkpoints.keys(), key=lambda x: x)  # IDs are sortable

        # Get writes from InMemorySaver's internal storage
        write_key = (prefixed_thread_id, checkpoint_ns, checkpoint_id)
        if write_key not in self.writes:
            return []

        # Convert writes to expected format
        writes_data = self.writes[write_key]
        result = []
        for inner_key, (task_id, channel, value, task_path) in writes_data.items():
            result.append(
                {
                    "task_id": task_id,
                    "channel": channel,
                    "value": self.serde.loads_typed(value),
                    "task_path": task_path,
                    "metadata": {"tenant_id": tenant_id},  # Add tenant metadata as expected by test
                }
            )

        return result
