"""Machine-to-machine POS ingestion endpoint.

The ingest road is authenticated by ``X-API-Key`` (not a session) because the
caller is the Formint POS sync client, not a browser. CSRF does not apply to an
API-keyed server-to-server POST, and the target workspace is resolved from the
payload's ``external_ref`` rather than from a session user.
"""
from __future__ import annotations

import hmac
import json

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.core.realtime import safe_publish_workspace_event

from .services import ingest_sales, resolve_workspace


def _authorized(request) -> bool:
    expected = getattr(settings, "POS_INGEST_API_KEY", "")
    if not expected:
        return False
    supplied = request.headers.get("X-API-Key", "")
    return hmac.compare_digest(str(supplied), str(expected))


@csrf_exempt
@require_POST
def ingest_pos_sales(request):
    if not _authorized(request):
        return JsonResponse({"detail": "Invalid or missing API key."}, status=401)
    try:
        payload = json.loads(request.body or b"{}")
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    workspace = resolve_workspace(str(payload.get("external_ref") or "").strip())
    if workspace is None:
        return JsonResponse({"detail": "Unknown workspace reference."}, status=404)

    results = ingest_sales(workspace, payload)
    safe_publish_workspace_event(
        workspace.id,
        "pos.sales.ingested",
        {"count": len(results), "results": results},
    )
    return JsonResponse({"results": results, "count": len(results)})
