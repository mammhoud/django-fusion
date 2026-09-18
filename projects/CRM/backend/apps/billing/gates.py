"""Billing feature gates — one module so every road shares the same rules.

Gates answer "may this workspace use this feature?" from the ``BillingAccount``
state and the workspace's ``Plan.feature_flags``. When billing is not configured
(no Stripe keys) or no account exists yet, gates stay permissive so local dev and
the seeded trial keep working — matching the plan's "empty values disable
checkout, not the product".
"""
from __future__ import annotations

from django.conf import settings

from apps.billing.models import BillingAccount


def billing_configured() -> bool:
    """True when Stripe keys are present (checkout/portal/webhook can run)."""
    return bool(settings.STRIPE_SECRET_KEY)


def account_for_workspace(workspace_id: int | None) -> BillingAccount | None:
    if workspace_id is None:
        return None
    try:
        return BillingAccount.objects.select_related("plan").filter(
            workspace_id=workspace_id
        ).first()
    except Exception:  # noqa: BLE001 - table may not exist during early checks
        return None


def feature_enabled(workspace_id: int | None, flag: str) -> bool:
    """Return whether a named feature flag is on for the workspace.

    ``flag`` maps to a key in ``Plan.feature_flags`` (e.g. ``attribution``,
    ``finance_ledger``, ``workflow_automation``). When no account exists the
    gate is permissive (unseeded workspaces are never silently broken).
    """
    account = account_for_workspace(workspace_id)
    if account is None:
        return True
    if not account.is_entitled:
        return False
    plan = account.plan
    if plan is None:
        return True
    return bool((plan.feature_flags or {}).get(flag, True))


def seat_count_ok(workspace_id: int | None, member_count: int) -> bool:
    """Return whether a workspace's member count fits its plan's seat limit."""
    account = account_for_workspace(workspace_id)
    if account is None or account.plan is None:
        return True
    limit = account.plan.seat_limit
    if limit <= 0:
        return True
    return member_count <= limit
