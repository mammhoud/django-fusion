"""Ingest service — Formint POS sales → Loop-CRM finance bridge.

Each pushed sale is upserted idempotently (keyed on ``external_id``) and, when
completed, bridges a ``RevenueEvent(kind="pos_sale")`` into the finance trend.
A refund removes that recognized revenue and flips ``PosSale.status`` to
``refunded``; the refund is recorded in the POS ledger and ``AuditLog`` rather
than as a positive revenue event (netting ``pos_refund`` into the trend is a
follow-up in the integration plan).
"""
from __future__ import annotations

import datetime
from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from apps.core.models import AuditLog, Workspace
from apps.crm.models import Company, Contact
from apps.finance.models import RevenueEvent

from .models import PosPayment, PosSale, PosSaleItem

VALID_STATUS = {choice[0] for choice in PosSale.STATUS_CHOICES}
VALID_METHOD = {choice[0] for choice in PosSale.PAYMENT_METHODS}


def resolve_workspace(external_ref: str | None) -> Workspace | None:
    """Return the workspace correlated to a POS ``external_ref``, or ``None``."""
    if not external_ref:
        return None
    return Workspace.objects.filter(external_ref=external_ref).first()


def _dec(value) -> Decimal:
    if value in (None, ""):
        return Decimal("0.00")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")


def _int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _datetime(value):
    if not value:
        return timezone.now()
    if isinstance(value, datetime.datetime):
        return timezone.make_aware(value) if timezone.is_naive(value) else value
    try:
        parsed = datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return timezone.now()
    return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed


def _walk_in_company(workspace: Workspace) -> Company:
    """The per-workspace company that holds POS contacts (no company concept in POS)."""
    company, _ = Company.objects.get_or_create(workspace=workspace, name="Walk-in customers")
    return company


def _upsert_contact(workspace: Workspace, company: Company, customer: dict | None) -> Contact | None:
    """Map a POS customer to a Loop-CRM contact (by email). Anonymous sales skip."""
    if not customer:
        return None
    email = str(customer.get("email") or "").strip()
    if not email:
        return None
    return Contact.objects.update_or_create(
        workspace=workspace,
        email=email,
        defaults={
            "company": company,
            "first_name": str(customer.get("first_name") or "Walk-in").strip(),
            "last_name": str(customer.get("last_name") or "Customer").strip(),
            "phone": str(customer.get("phone") or "").strip(),
            "custom_attributes": {"pos_external_id": str(customer.get("external_id") or "").strip()},
        },
    )[0]


def _reconcile_revenue(pos_sale: PosSale) -> None:
    """Bridge POS money into the finance trend.

    Completed sales produce a ``pos_sale`` revenue event; a refund removes it so
    a refunded sale no longer contributes recognized revenue.
    """
    sale_ref = f"pos:{pos_sale.external_id}"
    if pos_sale.status == "refunded":
        RevenueEvent.objects.filter(workspace_id=pos_sale.workspace_id, external_ref=sale_ref).delete()
        return
    if pos_sale.status != "completed":
        return
    RevenueEvent.objects.update_or_create(
        workspace_id=pos_sale.workspace_id,
        external_ref=sale_ref,
        defaults={
            "deal": None,
            "kind": "pos_sale",
            "amount": pos_sale.total,
            "recognized_on": timezone.localdate(),
            "metadata": {"source": "pos", "pos_sale_id": pos_sale.pk, "external_id": pos_sale.external_id},
        },
    )


def reconcile_pos_sale(pos_sale: PosSale) -> dict:
    """Ensure a PosSale's finance bridge exists (idempotent workflow action).

    A completed sale produces a ``RevenueEvent(kind="pos_sale")``; a refunded
    sale removes it so it contributes zero recognized revenue. Returns a small
    summary for the workflow action ledger.
    """
    _reconcile_revenue(pos_sale)
    return {
        "pos_sale_id": pos_sale.pk,
        "external_id": pos_sale.external_id,
        "status": pos_sale.status,
        "total": str(pos_sale.total),
    }


def _ingest_sale(workspace: Workspace, sale: dict) -> dict:
    external_id = str(sale.get("external_id") or "").strip()
    if not external_id:
        return {"external_id": "", "status": "error", "error": "external_id is required."}

    status = str(sale.get("status") or "completed").lower()
    if status not in VALID_STATUS:
        status = "completed"
    payment_method = str(sale.get("payment_method") or "cash").lower()
    if payment_method not in VALID_METHOD:
        payment_method = "cash"

    total_value = sale.get("total")
    total = _dec(total_value) if total_value not in (None, "") else _dec(sale.get("subtotal"))

    contact = _upsert_contact(workspace, _walk_in_company(workspace), sale.get("customer"))
    pos_sale, created = PosSale.objects.update_or_create(
        workspace=workspace,
        external_id=external_id,
        defaults={
            "contact": contact,
            "sale_date": _datetime(sale.get("sale_date")),
            "subtotal": _dec(sale.get("subtotal")),
            "tax_amount": _dec(sale.get("tax_amount")),
            "discount_amount": _dec(sale.get("discount_amount")),
            "cashback_amount": _dec(sale.get("cashback_amount")),
            "total": total,
            "payment_method": payment_method,
            "status": status,
            "source": str(sale.get("source") or "formint-pro"),
            "metadata": sale.get("metadata") or {},
        },
    )

    for index, item in enumerate(sale.get("items") or []):
        item_ref = str(item.get("external_id") or f"{external_id}:{index}")
        unit_price = _dec(item.get("unit_price"))
        line_total_value = item.get("line_total")
        line_total = _dec(line_total_value) if line_total_value not in (None, "") else unit_price * _int(item.get("quantity"))
        PosSaleItem.objects.update_or_create(
            pos_sale=pos_sale,
            external_id=item_ref,
            defaults={
                "product_name": str(item.get("product_name") or item.get("name") or "Item"),
                "quantity": _int(item.get("quantity")),
                "unit_price": unit_price,
                "line_total": line_total,
            },
        )

    payments = sale.get("payments") or []
    if not payments:
        payments = [{"amount": pos_sale.total, "method": pos_sale.payment_method}]
    for index, payment in enumerate(payments):
        reference = str(payment.get("reference") or f"{external_id}:payment:{index}")
        amount_value = payment.get("amount")
        amount = _dec(amount_value) if amount_value not in (None, "") else pos_sale.total
        PosPayment.objects.update_or_create(
            pos_sale=pos_sale,
            reference=reference,
            defaults={
                "amount": amount,
                "method": payment.get("method") if payment.get("method") in VALID_METHOD else pos_sale.payment_method,
                "paid_on": timezone.localdate(),
            },
        )

    _reconcile_revenue(pos_sale)

    AuditLog.objects.create(
        user=None,
        workspace=workspace,
        action="create" if created else "update",
        model_name="pos.PosSale",
        object_id=external_id,
        changes={"external_id": external_id, "status": status, "total": str(pos_sale.total)},
    )

    # A newly ingested completed sale fires the POS-revenue workflow so extra
    # actions (RevOps notification, future attribution) run alongside the
    # immediate finance bridge above. Best-effort: the broker outage is handled
    # inside trigger_workflow.
    if created and status == "completed":
        from plugins.workers.tasks import trigger_workflow

        trigger_workflow(
            "pos-revenue-reconciled",
            workspace.pk,
            {"pos_sale_id": pos_sale.pk, "external_id": external_id, "source": "pos_sale.ingested"},
        )
        from apps.core.webhooks import dispatch_webhooks

        dispatch_webhooks(
            workspace.pk,
            "pos_sale_ingested",
            {"pos_sale_id": pos_sale.pk, "external_id": external_id, "total": str(pos_sale.total)},
        )

    return {"external_id": external_id, "status": "created" if created else "updated", "pos_sale_id": pos_sale.pk}


def ingest_sales(workspace: Workspace, payload: dict) -> list[dict]:
    """Ingest a batch of POS sales, isolating failures to individual rows."""
    sales = payload.get("sales") or []
    results: list[dict] = []
    for sale in sales:
        try:
            with transaction.atomic():
                results.append(_ingest_sale(workspace, sale))
        except Exception as exc:  # noqa: BLE001 - report per-row, keep the batch going
            results.append(
                {"external_id": str(sale.get("external_id") or ""), "status": "error", "error": str(exc)}
            )
    return results
