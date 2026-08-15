"""Account/profile synchronization and workflow triggers for Loop-CRM.

The domain triggers below emit workflow runs through ``trigger_workflow``,
which is a no-op unless an active matching definition exists, and which marks
runs ``failed`` rather than raising when the Dramatiq broker is unavailable.
Each trigger is guarded so its own workflow actions cannot re-trigger it
(e.g. dunning only fires while an invoice is still ``issued``/``partially_paid``
and past due, so the workflow marking it ``overdue`` cannot loop).
"""
from __future__ import annotations

import logging

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.crm.models import Contact
from apps.finance.models import Invoice, Payment

from .models import UserProfile

logger = logging.getLogger(__name__)


def _trigger(slug: str, workspace_id, payload: dict) -> None:
    """Queue a workflow, swallowing broker outages (best-effort automation)."""
    if workspace_id is None:
        return
    from plugins.workers.tasks import trigger_workflow

    trigger_workflow(slug, workspace_id, payload)


@receiver(post_save, sender=get_user_model())
def ensure_user_profile(sender, instance, created, **kwargs):
    """Ensure allauth-created and admin-created accounts have a role record."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=Invoice)
def trigger_invoice_dunning(sender, instance, created, **kwargs):
    """Queue dunning when an issued/partially-paid invoice is past due."""
    if instance.status not in {"issued", "partially_paid"}:
        return
    if not instance.is_overdue:
        return
    _trigger(
        "invoice-dunning",
        instance.workspace_id,
        {"invoice_id": instance.pk, "deal_id": instance.deal_id, "source": "invoice.due_date_passed"},
    )


@receiver(post_save, sender=Payment)
def trigger_payment_received(sender, instance, created, **kwargs):
    """Queue the payment-received workflow on a new payment."""
    if not created:
        return
    invoice = getattr(instance, "invoice", None)
    _trigger(
        "payment-received",
        instance.workspace_id,
        {
            "payment_id": instance.pk,
            "invoice_id": instance.invoice_id,
            "deal_id": invoice.deal_id if invoice else None,
            "source": "payment.created",
        },
    )
    from apps.core.webhooks import dispatch_webhooks

    dispatch_webhooks(
        instance.workspace_id,
        "payment_received",
        {
            "payment_id": instance.pk,
            "invoice_id": instance.invoice_id,
            "amount": str(instance.amount),
        },
    )


@receiver(post_save, sender=Contact)
def trigger_contact_nurture(sender, instance, created, **kwargs):
    """Queue a welcome workflow for a newly created contact."""
    if not created:
        return
    _trigger(
        "contact-nurture",
        instance.workspace_id,
        {"contact_id": instance.pk, "email": instance.email, "source": "contact.created"},
    )


@receiver(user_signed_up)
def provision_start_free_workspace(sender, request, user, **kwargs):
    """Give every fresh signup (the landing's Start free flow) a demo workspace.

    The account signal fires for email signup right after the user is created;
    social signup routes through the same account flow. A user who already has
    a workspace (admin-created, re-invited, or reseeded) is left untouched.
    """
    profile = getattr(user, "profile", None)
    if profile is None or profile.workspace_id is not None:
        return
    from .demo import ensure_user_workspace

    try:
        ensure_user_workspace(user)
        logger.info("Provisioned demo workspace for new signup %s", user)
    except Exception:  # noqa: BLE001 - never break signup over demo seeding
        logger.exception("Demo workspace provisioning failed for %s", user)

