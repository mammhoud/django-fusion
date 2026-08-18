"""Billing roads — checkout, portal, Stripe webhook, and the plan catalog."""
from __future__ import annotations

import json

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.billing.gates import account_for_workspace, billing_configured
from apps.billing.models import Plan
from apps.billing.services import (
    account_payload,
    create_checkout_session,
    create_portal_session,
    ensure_account,
    handle_webhook,
    plan_catalog,
)
from apps.core.tenancy import current_workspace_id


@require_GET
def plans_api(request: HttpRequest) -> JsonResponse:
    """Public tier catalog for the Wagtail pricing page (``/apis/billing/plans/``)."""
    return JsonResponse(
        {
            "configured": billing_configured(),
            "plans": plan_catalog(),
        }
    )


@login_required
@require_GET
def account_api(request: HttpRequest) -> JsonResponse:
    """Authenticated billing account state for the webapp /settings/plan/ page."""
    workspace_id = current_workspace_id(request)
    if workspace_id is None:
        return JsonResponse({"configured": billing_configured(), "status": "none", "plan": None}, status=404)

    return JsonResponse(account_payload(account_for_workspace(workspace_id), workspace_id))


@login_required
@require_POST
def checkout(request: HttpRequest) -> JsonResponse:
    """Create a Stripe Checkout Session for the selected plan + period."""
    if not billing_configured():
        return JsonResponse({"detail": "Billing is not configured."}, status=503)
    workspace_id = current_workspace_id(request)
    if workspace_id is None:
        return JsonResponse({"detail": "A workspace is required to start checkout."}, status=400)
    try:
        body = json.loads(request.body or b"{}")
    except ValueError:
        return JsonResponse({"detail": "Request body must be valid JSON."}, status=400)
    plan_slug = (body.get("plan") or request.POST.get("plan") or "").strip()
    period = (body.get("period") or request.POST.get("period") or "monthly").strip()
    quantity = int(body.get("quantity") or request.POST.get("quantity") or 1)
    if not plan_slug:
        return JsonResponse({"detail": "A plan slug is required."}, status=400)
    plan = get_object_or_404(Plan, slug=plan_slug, is_active=True)
    account = ensure_account(workspace_id)
    result = create_checkout_session(account, plan, period, quantity=max(1, quantity))
    if not result.get("configured"):
        return JsonResponse({"detail": "Billing is not configured."}, status=503)
    if result.get("error"):
        return JsonResponse({"detail": result["error"]}, status=422)
    return JsonResponse(result)


@login_required
@require_GET
def portal(request: HttpRequest) -> HttpResponse:
    """Redirect to the Stripe Billing Portal for self-service management."""
    if not billing_configured():
        return JsonResponse({"detail": "Billing is not configured."}, status=503)
    workspace_id = current_workspace_id(request)
    if workspace_id is None:
        return JsonResponse({"detail": "A workspace is required."}, status=400)
    account = ensure_account(workspace_id)
    result = create_portal_session(account)
    if not result.get("configured"):
        return JsonResponse({"detail": "Billing is not configured."}, status=503)
    return redirect(result["url"])


@csrf_exempt
@require_POST
def webhook(request: HttpRequest) -> HttpResponse:
    """Stripe webhook — verify signature, then reconcile subscription state."""
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    ok, error = handle_webhook(request.body, signature)
    if not ok:
        return JsonResponse({"detail": error or "Webhook rejected."}, status=400)
    return JsonResponse({"received": True})
