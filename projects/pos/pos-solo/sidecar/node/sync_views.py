"""
Sync views for Solo edition.
Provides status, trigger, config management for cloud CRM sync.

@tested pos-portal/solo - Sync views
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

import httpx

logger = logging.getLogger("solo.sync")

SYNC_STATE_FILE = Path(__file__).parent.parent.parent / "sync_state.json"


def _load_state() -> dict:
    if not SYNC_STATE_FILE.exists():
        return {
            "enabled": False,
            "cloud_url": getattr(settings, "CLOUD_CRM_URL", "http://localhost:8766"),
            "api_key": getattr(settings, "CLOUD_CRM_API_KEY", ""),
            "last_sync": None,
            "status": "idle",
            "items_synced": 0,
            "errors": 0,
        }
    try:
        with open(SYNC_STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_state(state: dict) -> None:
    with open(SYNC_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


@require_GET
def sync_status(request):
    """Get current sync status."""
    state = _load_state()
    return JsonResponse(state)


@csrf_exempt
@require_POST
def trigger_sync(request):
    """Trigger a manual sync to the cloud CRM server."""
    state = _load_state()
    cloud_url = state.get("cloud_url")

    if not cloud_url:
        return JsonResponse({"error": "cloud_url not configured"}, status=400)

    try:
        resp = httpx.get(f"{cloud_url}/health", timeout=10)
        resp.raise_for_status()
        health = resp.json()

        state["status"] = "syncing"
        _save_state(state)

        return JsonResponse({
            "status": "syncing",
            "cloud_health": health,
            "message": "Sync triggered.",
        })
    except httpx.RequestError as exc:
        state["status"] = "error"
        state["last_error"] = str(exc)
        _save_state(state)
        return JsonResponse({"error": str(exc)}, status=500)


@csrf_exempt
@require_POST
def update_sync_config(request):
    """Update sync configuration."""
    import json as json_module
    payload = json_module.loads(request.body)
    state = _load_state()

    if "cloud_url" in payload:
        state["cloud_url"] = payload["cloud_url"]
    if "api_key" in payload:
        state["api_key"] = payload["api_key"]
    if "enabled" in payload:
        state["enabled"] = bool(payload["enabled"])

    _save_state(state)
    return JsonResponse({"status": "ok", "config": state})


@require_GET
def sync_log(request):
    """Get sync history log."""
    state = _load_state()
    log_entries = [{
        "timestamp": state.get("last_sync"),
        "status": state.get("status"),
        "items_synced": state.get("items_synced", 0),
        "errors": state.get("errors", 0),
        "cloud_url": state.get("cloud_url"),
    }]
    return JsonResponse(log_entries, safe=False)
