"""
Conflict Resolution Engine for POS Multi-Terminal Sync.

Provides pluggable conflict resolution strategies when two or more branches
modify the same entity between sync cycles.  Each resolver implements the
``ConflictResolver`` protocol and returns a ``Resolution`` decision.

Strategies
----------
1. **LastWriteWinsResolver** (default) — The version with the most recent
   ``updated_at`` timestamp wins.  Simple, predictable, suitable for most
   POS data (products, customers, employees).

2. **TimestampVectorResolver** — Uses Lamport-style timestamp vectors to
   detect true causal conflicts and merge non-conflicting fields.  Suitable
   for inventory and config where concurrent edits should be preserved.

3. **ManualResolver** — Flags conflicts for human review in the approval
   dashboard.  No automatic resolution — every conflict is persisted to
   the ``SyncConflict`` model for manual resolution.

Usage::

    from core.conflict_resolver import (
        LastWriteWinsResolver,
        TimestampVectorResolver,
        ConflictResolutionEngine,
    )

    engine = ConflictResolutionEngine(
        default_resolver=LastWriteWinsResolver(),
    )

    # Resolve a conflict between two versions of the same entity
    resolution = engine.resolve(entity_type="products", local=local, remote=remote)
    if resolution.action == "use_remote":
        # Accept the remote version
        apply_remote_changes(resolution.merged_data)

    # Or use the timestamp vector resolver for more complex cases
    engine = ConflictResolutionEngine(
        default_resolver=TimestampVectorResolver(),
    )
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger("pos.conflict_resolver")


# ══════════════════════════════════════════════════════════════════════
# Types
# ══════════════════════════════════════════════════════════════════════


class ResolutionAction(str, Enum):
    """What to do with the result of conflict resolution."""

    USE_LOCAL = "use_local"          # Keep the local version
    USE_REMOTE = "use_remote"        # Accept the remote version
    MERGE = "merge"                  # Merge non-conflicting fields
    FLAG_MANUAL = "flag_manual"      # Requires human review


@dataclass
class EntityVersion:
    """Represents one version of an entity from a specific node."""

    source_node_id: str
    entity_type: str
    entity_id: str
    data: dict[str, Any]
    updated_at: datetime | None = None
    timestamp_vector: dict[str, int] | None = None
    source_branch: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> "EntityVersion":
        """Create from a dict (e.g., from sync payload)."""
        updated_at = None
        if d.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(d["updated_at"])
            except (ValueError, TypeError):
                pass
        return cls(
            source_node_id=d.get("node_id", d.get("source_node_id", "unknown")),
            entity_type=d.get("entity_type", ""),
            entity_id=str(d.get("id", d.get("entity_id", ""))),
            data=d.get("data", d),
            updated_at=updated_at,
            timestamp_vector=d.get("timestamp_vector"),
            source_branch=d.get("branch_name", d.get("branch")),
        )


@dataclass
class Resolution:
    """The result of conflict resolution."""

    action: ResolutionAction
    merged_data: dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    conflicts: list[dict[str, Any]] = field(default_factory=list)


# ══════════════════════════════════════════════════════════════════════
# Abstract base
# ══════════════════════════════════════════════════════════════════════


class ConflictResolver(ABC):
    """Abstract conflict resolver.  All resolvers implement ``resolve()``."""

    name: str = "base"

    @abstractmethod
    def resolve(self, local: EntityVersion, remote: EntityVersion) -> Resolution:
        """Compare two versions and return a resolution."""
        ...


# ══════════════════════════════════════════════════════════════════════
# Strategy 1: Last-Write-Wins (default)
# ══════════════════════════════════════════════════════════════════════


class LastWriteWinsResolver(ConflictResolver):
    """The most recent ``updated_at`` wins.  Default strategy.

    When timestamps are equal or unavailable, prefers the remote version
    (cloud-authoritative for config, branch-authoritative for POS data).
    """

    name: str = "last_write_wins"

    def resolve(self, local: EntityVersion, remote: EntityVersion) -> Resolution:
        if local.updated_at and remote.updated_at:
            if remote.updated_at > local.updated_at:
                return Resolution(
                    action=ResolutionAction.USE_REMOTE,
                    merged_data=remote.data,
                    reason=f"Remote is newer: {remote.updated_at} > {local.updated_at}",
                )
            elif local.updated_at > remote.updated_at:
                return Resolution(
                    action=ResolutionAction.USE_LOCAL,
                    merged_data=local.data,
                    reason=f"Local is newer: {local.updated_at} > {remote.updated_at}",
                )
            else:
                # Same timestamp — prefer remote for cloud-authoritative entities
                return Resolution(
                    action=ResolutionAction.USE_REMOTE,
                    merged_data=remote.data,
                    reason="Same timestamp, prefer remote (cloud-authoritative)",
                )

        # No timestamps — prefer remote (most syncs are branch→cloud)
        return Resolution(
            action=ResolutionAction.USE_REMOTE,
            merged_data=remote.data,
            reason="No timestamp available, defaulting to remote",
        )


# ══════════════════════════════════════════════════════════════════════
# Strategy 2: Timestamp Vector (causal tracking)
# ══════════════════════════════════════════════════════════════════════


class TimestampVectorResolver(ConflictResolver):
    """Lamport-style timestamp vector conflict resolution.

    Each node maintains a monotonic counter.  The vector ``{node_id: counter}``
    is attached to every sync payload.  When comparing two versions:

    - If one vector dominates the other (all counters >=), the dominating
      version is strictly newer — use it.
    - If neither dominates (concurrent edits detected), attempt a field-level
      merge.  Fields that differ between the two versions are flagged.
    - A ``conflict_fields`` list is returned so the caller can decide whether
      to auto-merge or escalate.
    """

    name: str = "timestamp_vector"

    def resolve(self, local: EntityVersion, remote: EntityVersion) -> Resolution:
        local_vec = local.timestamp_vector or {}
        remote_vec = remote.timestamp_vector or {}

        if not local_vec and not remote_vec:
            # Fall back to Last-Write-Wins
            return LastWriteWinsResolver().resolve(local, remote)

        local_dominates = self._dominates(local_vec, remote_vec)
        remote_dominates = self._dominates(remote_vec, local_vec)

        if remote_dominates and not local_dominates:
            return Resolution(
                action=ResolutionAction.USE_REMOTE,
                merged_data=remote.data,
                reason="Remote timestamp vector dominates local",
            )

        if local_dominates and not remote_dominates:
            return Resolution(
                action=ResolutionAction.USE_LOCAL,
                merged_data=local.data,
                reason="Local timestamp vector dominates remote",
            )

        # Concurrent edits — attempt field-level merge
        merged, conflicts = self._merge_fields(local.data, remote.data)

        if conflicts:
            return Resolution(
                action=ResolutionAction.MERGE,
                merged_data=merged,
                reason=f"Concurrent edits detected, merged {len(merged)} fields, "
                       f"{len(conflicts)} conflicts remain",
                conflicts=[{
                    "field": c["field"],
                    "local_value": c["local_value"],
                    "remote_value": c["remote_value"],
                    "entity_type": local.entity_type,
                    "entity_id": local.entity_id,
                    "local_node": local.source_node_id,
                    "remote_node": remote.source_node_id,
                } for c in conflicts],
            )

        # No conflicts after merge — safe to use merged result
        return Resolution(
            action=ResolutionAction.MERGE,
            merged_data=merged,
            reason="Concurrent edits merged successfully, no field conflicts",
        )

    def _dominates(self, a: dict[str, int], b: dict[str, int]) -> bool:
        """Check if vector *a* dominates vector *b* (all counters >=)."""
        if not b:
            return True  # Empty vector is always dominated
        for key, val in b.items():
            if a.get(key, 0) < val:
                return False
        return True

    def _merge_fields(
        self, local: dict[str, Any], remote: dict[str, Any]
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Field-level merge with conflict detection.

        Returns (merged_data, conflict_list).
        For each field:
        - If identical, keep either.
        - If only one side changed it (compared to a common ancestor), keep it.
        - If both sides changed it differently, flag as a conflict.
        """
        merged = {}
        conflicts = []
        all_keys = set(local.keys()) | set(remote.keys())

        for key in all_keys:
            lv = local.get(key)
            rv = remote.get(key)

            if key in ("updated_at", "timestamp_vector", "last_synced_at"):
                # Skip metadata fields in field-level merge
                merged[key] = rv or lv
                continue

            if lv == rv:
                merged[key] = lv
            elif lv is None and rv is not None:
                merged[key] = rv  # Local doesn't have it — use remote
            elif rv is None and lv is not None:
                merged[key] = lv  # Remote doesn't have it — keep local
            else:
                # Both have values but they differ — flag as conflict
                # Use remote value by default (cloud-authoritative), but flag it
                merged[key] = rv
                conflicts.append({
                    "field": key,
                    "local_value": lv,
                    "remote_value": rv,
                })

        return merged, conflicts


# ══════════════════════════════════════════════════════════════════════
# Strategy 3: Manual — always flag for human review
# ══════════════════════════════════════════════════════════════════════


class ManualResolver(ConflictResolver):
    """Never resolves automatically.  Every conflict is flagged for review.

    Suitable for high-value entities (pricing changes, employee data, config).
    Conflicts are persisted to the ``SyncConflict`` model and shown in the
    approval dashboard.
    """

    name: str = "manual"

    def resolve(self, local: EntityVersion, remote: EntityVersion) -> Resolution:
        return Resolution(
            action=ResolutionAction.FLAG_MANUAL,
            merged_data={},
            reason="Manual resolution required — all conflicts flagged for review",
            conflicts=[{
                "field": k,
                "local_value": local.data.get(k),
                "remote_value": remote.data.get(k),
                "entity_type": local.entity_type,
                "entity_id": local.entity_id,
                "local_node": local.source_node_id,
                "remote_node": remote.source_node_id,
            } for k in set(local.data) | set(remote.data)
              if local.data.get(k) != remote.data.get(k)],
        )


# ══════════════════════════════════════════════════════════════════════
# Conflict Resolution Engine
# ══════════════════════════════════════════════════════════════════════


class ConflictResolutionEngine:
    """Orchestrates conflict resolution across entity types.

    Supports per-entity-type resolver overrides so that products can use
    Last-Write-Wins while pricing uses Manual resolution::

        engine = ConflictResolutionEngine(
            default_resolver=LastWriteWinsResolver(),
            entity_resolvers={
                "products": LastWriteWinsResolver(),
                "prices": ManualResolver(),
                "inventory": TimestampVectorResolver(),
            },
        )
    """

    def __init__(
        self,
        default_resolver: ConflictResolver | None = None,
        entity_resolvers: dict[str, ConflictResolver] | None = None,
    ) -> None:
        self._default = default_resolver or LastWriteWinsResolver()
        self._entity_resolvers = entity_resolvers or {}

    def resolve(
        self,
        entity_type: str,
        local: EntityVersion,
        remote: EntityVersion,
    ) -> Resolution:
        """Resolve a conflict between two versions of an entity.

        Args:
            entity_type: Type discriminator (e.g. ``"products"``, ``"inventory"``).
            local: The version currently stored in the cloud.
            remote: The incoming version from a branch sync push.

        Returns:
            A ``Resolution`` with the action to take and merged data.
        """
        resolver = self._entity_resolvers.get(entity_type, self._default)
        logger.debug(
            "Resolving %s conflict using %s (local=%s, remote=%s)",
            entity_type, resolver.name,
            local.source_node_id, remote.source_node_id,
        )
        return resolver.resolve(local, remote)

    def set_entity_resolver(self, entity_type: str, resolver: ConflictResolver) -> None:
        """Override the resolver for a specific entity type."""
        self._entity_resolvers[entity_type] = resolver
        logger.info("Set %s resolver for %s", resolver.name, entity_type)


# ══════════════════════════════════════════════════════════════════════
# Singleton instance
# ══════════════════════════════════════════════════════════════════════

# Per-entity-type resolver defaults for POS
# Products → LWW (most recent catalog update wins)
# Inventory → Timestamp Vector (preserve concurrent adjustments)
# Config → Manual (must be reviewed)
# Prices → Manual (must be reviewed)
# Sales → LWW (immutable once created, so last write is authoritative)

_resolution_engine = ConflictResolutionEngine(
    default_resolver=LastWriteWinsResolver(),
    entity_resolvers={
        "products": LastWriteWinsResolver(),
        "inventory": TimestampVectorResolver(),
        "config": ManualResolver(),
        "prices": ManualResolver(),
        "sales": LastWriteWinsResolver(),
        "customers": LastWriteWinsResolver(),
        "employees": LastWriteWinsResolver(),
        "categories": LastWriteWinsResolver(),
    },
)


def get_resolution_engine() -> ConflictResolutionEngine:
    """Return the shared conflict resolution engine singleton."""
    return _resolution_engine


def resolve_conflict(
    entity_type: str,
    local_data: dict,
    remote_data: dict,
    local_node: str = "cloud",
    remote_node: str = "branch",
    local_ts: str | None = None,
    remote_ts: str | None = None,
) -> Resolution:
    """Convenience function for resolving a single conflict.

    Usage::

        from core.conflict_resolver import resolve_conflict

        resolution = resolve_conflict(
            entity_type="products",
            local_data=existing_product_data,
            remote_data=incoming_product_data,
            remote_node=incoming_node_id,
        )
        if resolution.action == "use_remote":
            apply_update(resolution.merged_data)
    """
    engine = get_resolution_engine()
    local_version = EntityVersion(
        source_node_id=local_node,
        entity_type=entity_type,
        entity_id=str(local_data.get("id", "")),
        data=local_data,
        updated_at=datetime.fromisoformat(local_ts) if local_ts else None,
    )
    remote_version = EntityVersion(
        source_node_id=remote_node,
        entity_type=entity_type,
        entity_id=str(remote_data.get("id", "")),
        data=remote_data,
        updated_at=datetime.fromisoformat(remote_ts) if remote_ts else None,
    )
    return engine.resolve(entity_type, local_version, remote_version)
