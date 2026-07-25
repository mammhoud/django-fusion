"""
POS Cloud — Branch Sync Dashboard API Endpoints.

Provides REST endpoints consumed by the analytics dashboard and Unfold
admin pages for:

- Branch health status (online/offline, connected terminals)
- Sync queue status (pending, delivering, failed counts)
- Pending conflict approvals (list, resolve, dismiss)
- Per-branch sync metrics
"""

from __future__ import annotations

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone as django_timezone
from django.views.decorators.http import require_GET, require_POST

from .models import (
    Branch, SyncConflict, SyncQueueItem, BranchSyncLog,
)
from .sync_broker import broker
from .sync_queue import sync_queue

logger = logging.getLogger("pos.sync_dashboard")


# ══════════════════════════════════════════════════════════════════════
# Health & Status
# ══════════════════════════════════════════════════════════════════════


@require_GET
def branch_health(request, branch_code: str):
    """GET /api/dashboard/branches/{branch_code}/health

    Returns WebSocket connection status and basic branch info.
    """
    branch = get_object_or_404(Branch, code=branch_code, is_active=True)
    ws_status = broker.branch_health_check(branch_code)
    return JsonResponse({
        "branch": {
            "id": branch.id,
            "name": branch.name,
            "code": branch.code,
            "node_id": branch.node_id,
            "pos_type": branch.pos_type,
            "is_active": branch.is_active,
            "sync_enabled": branch.sync_enabled,
            "sync_interval": branch.sync_interval,
        },
        "websocket": ws_status,
    })


@require_GET
def all_branches_health(request):
    """GET /api/dashboard/branches/health

    Returns health status for all active branches.
    """
    ws_status = broker.all_branch_health()
    branches = []
    for b in Branch.objects.filter(is_active=True).only(
        "id", "name", "code", "node_id", "pos_type", "sync_enabled"
    ):
        health = ws_status.get(b.code, {"online": False, "connected_terminals": 0})
        branches.append({
            "id": b.id,
            "name": b.name,
            "code": b.code,
            "node_id": b.node_id or "",
            "pos_type": b.pos_type,
            "sync_enabled": b.sync_enabled,
            "online": health["online"],
            "connected_terminals": health["connected_terminals"],
        })
    return JsonResponse({"branches": branches, "total": len(branches)})


# ══════════════════════════════════════════════════════════════════════
# Sync Queue Dashboard
# ══════════════════════════════════════════════════════════════════════


@require_GET
def queue_summary(request):
    """GET /api/dashboard/queue/summary

    Returns aggregate queue status counts.
    """
    return JsonResponse({
        "pending": sync_queue.pending_count(),
        "failed": sync_queue.failed_count(),
        "total": SyncQueueItem.objects.count(),
        "estimated_backlog_seconds": _estimate_backlog(),
    })


@require_GET
def queue_by_branch(request):
    """GET /api/dashboard/queue/by-branch

    Returns per-branch queue statistics.
    """
    items = []
    for branch in Branch.objects.filter(is_active=True):
        pending = sync_queue.pending_count(branch.code)
        failed = sync_queue.failed_count(branch.code)
        items.append({
            "branch": branch.name,
            "code": branch.code,
            "pending": pending,
            "failed": failed,
        })
    return JsonResponse({"branches": items})


@require_GET
def queue_list(request, status: str = "pending"):
    """GET /api/dashboard/queue/list/{status}

    Returns queue items filtered by status.
    """
    valid_statuses = dict(SyncQueueItem.QueueStatus.choices)
    if status not in valid_statuses:
        status = "pending"

    items = (
        SyncQueueItem.objects
        .filter(status=status)
        .select_related("branch")
        .order_by("-created_at")[:100]
    )

    return JsonResponse({
        "items": [
            {
                "id": item.pk,
                "branch": item.branch.name,
                "branch_code": item.branch.code,
                "entity_type": item.entity_type,
                "operation": item.operation,
                "status": item.status,
                "attempt_count": item.attempt_count,
                "max_attempts": item.max_attempts,
                "last_error": item.last_error,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "next_retry_at": item.next_retry_at.isoformat() if item.next_retry_at else None,
            }
            for item in items
        ],
        "count": len(items),
    })


@require_POST
@login_required
def queue_retry(request, item_id: int):
    """POST /api/dashboard/queue/retry/{item_id}

    Reset a failed queue item for retry.
    """
    item = sync_queue.retry_item(item_id)
    if item is None:
        return JsonResponse({"error": "Queue item not found"}, status=404)
    return JsonResponse({
        "status": "retry_scheduled",
        "item_id": item_id,
        "next_retry_at": item.next_retry_at.isoformat() if item.next_retry_at else None,
    })


@require_POST
@login_required
def queue_cancel(request, item_id: int):
    """POST /api/dashboard/queue/cancel/{item_id}

    Cancel a pending queue item.
    """
    cancelled = sync_queue.cancel_item(item_id)
    if not cancelled:
        return JsonResponse({"error": "Item not found or already processed"}, status=404)
    return JsonResponse({"status": "cancelled", "item_id": item_id})


# ══════════════════════════════════════════════════════════════════════
# Conflict Approval Dashboard
# ══════════════════════════════════════════════════════════════════════


@require_GET
def conflict_list(request):
    """GET /api/dashboard/conflicts

    Returns all pending conflicts that require human review.
    """
    conflicts = (
        SyncConflict.objects
        .filter(status=SyncConflict.ResolutionStatus.PENDING)
        .select_related("branch", "resolved_by")
        .order_by("-created_at")
    )

    return JsonResponse({
        "conflicts": [
            {
                "id": c.pk,
                "branch": c.branch.name,
                "branch_code": c.branch.code,
                "node_id": c.node_id,
                "entity_type": c.entity_type,
                "entity_id": c.entity_id,
                "resolver_used": c.resolver_used,
                "reason": c.reason,
                "conflict_fields": c.conflict_fields,
                "local_data": c.local_data,
                "remote_data": c.remote_data,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in conflicts
        ],
        "count": conflicts.count(),
    })


@require_POST
@login_required
def conflict_resolve(request, conflict_id: int):
    """POST /api/dashboard/conflicts/{conflict_id}/resolve

    Resolve a conflict by choosing which version to keep.

    Request body::

        {
            "resolution": "use_local" | "use_remote" | "merge",
            "merged_data": { ... },
            "notes": "Optional notes"
        }
    """
    conflict = get_object_or_404(SyncConflict, pk=conflict_id)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    resolution = data.get("resolution", "use_local")
    notes = data.get("notes", "")

    status_map = {
        "use_local": SyncConflict.ResolutionStatus.RESOLVED_USE_LOCAL,
        "use_remote": SyncConflict.ResolutionStatus.RESOLVED_USE_REMOTE,
        "merge": SyncConflict.ResolutionStatus.RESOLVED_MERGE,
    }

    new_status = status_map.get(resolution)
    if new_status is None:
        return JsonResponse({
            "error": f"Invalid resolution: {resolution}. Use: use_local, use_remote, merge",
        }, status=400)

    conflict.status = new_status
    conflict.resolution_notes = notes
    if request.user.is_authenticated:
        conflict.resolved_by = request.user
    conflict.resolved_at = django_timezone.now()

    if resolution == "merge" and data.get("merged_data"):
        conflict.local_data = data["merged_data"]

    conflict.save(update_fields=[
        "status", "resolution_notes", "resolved_by", "resolved_at", "local_data",
    ])

    logger.info(
        "Conflict %d resolved as %s by %s",
        conflict_id, resolution, request.user or "anonymous",
    )

    return JsonResponse({
        "status": "resolved",
        "conflict_id": conflict_id,
        "resolution": resolution,
    })


@require_POST
@login_required
def conflict_dismiss(request, conflict_id: int):
    """POST /api/dashboard/conflicts/{conflict_id}/dismiss

    Dismiss a conflict without applying any changes.
    """
    conflict = get_object_or_404(SyncConflict, pk=conflict_id)
    conflict.status = SyncConflict.ResolutionStatus.DISMISSED
    if request.user.is_authenticated:
        conflict.resolved_by = request.user
    conflict.resolved_at = django_timezone.now()
    conflict.save(update_fields=["status", "resolved_by", "resolved_at"])

    return JsonResponse({"status": "dismissed", "conflict_id": conflict_id})


@require_GET
def conflict_stats(request):
    """GET /api/dashboard/conflicts/stats

    Returns aggregate conflict statistics.
    """
    return JsonResponse({
        "pending": SyncConflict.objects.filter(status="pending").count(),
        "resolved": SyncConflict.objects.exclude(
            status__in=["pending", "dismissed"],
        ).count(),
        "dismissed": SyncConflict.objects.filter(status="dismissed").count(),
        "total": SyncConflict.objects.count(),
        "by_entity_type": _conflict_by_entity(),
    })


# ══════════════════════════════════════════════════════════════════════
# Sync Activity Dashboard
# ══════════════════════════════════════════════════════════════════════


@require_GET
def recent_activity(request, limit: int = 20):
    """GET /api/dashboard/activity?limit=20

    Returns the most recent sync activity across all branches.
    """
    logs = (
        BranchSyncLog.objects
        .select_related("branch")
        .order_by("-received_at")[:limit]
    )

    return JsonResponse({
        "entries": [
            {
                "id": log.pk,
                "branch": log.branch.name,
                "branch_code": log.branch.code,
                "node_id": log.node_id,
                "entity_type": log.entity_type,
                "entity_count": log.entity_count,
                "status": log.status,
                "error_message": log.error_message,
                "received_at": log.received_at.isoformat() if log.received_at else None,
            }
            for log in logs
        ],
    })


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════


def _estimate_backlog() -> int:
    """Estimate backlog processing time in seconds based on pending items."""
    pending = SyncQueueItem.objects.filter(
        status=SyncQueueItem.QueueStatus.PENDING,
    ).count()
    return pending * 2


def _conflict_by_entity() -> dict:
    """Count pending conflicts grouped by entity type."""
    from django.db.models import Count
    qs = (
        SyncConflict.objects
        .filter(status="pending")
        .values("entity_type")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    return {item["entity_type"]: item["count"] for item in qs}
