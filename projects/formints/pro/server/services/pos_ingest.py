"""Loop-CRM POS ingest push — Formint Pro → Loop-CRM finance bridge.

Pushes completed/refunded ``Sale`` rows to Loop-CRM's machine ingest endpoint
(``POST /api/v1/ingest/pos/sales/``) and marks each row's ``sync_status`` from
the per-row response. This is the push half of the Formint ↔ Loop-CRM
financial integration; Loop-CRM's ``apps/pos/services.ingest_sales`` is the
receive half (keyed on ``external_id`` per workspace).

Configuration (env):
  * ``LOOP_CRM_URL`` — Loop-CRM backend base URL (e.g. https://crm.example.com).
  * ``LOOP_CRM_INGEST_API_KEY`` — machine key; must match Loop-CRM's
    ``POS_INGEST_API_KEY`` setting.
  * ``LOOP_CRM_WORKSPACE_REF`` — the Loop-CRM ``Workspace.external_ref`` this
    POS terminal maps to (the ingest road resolves the target workspace from
    it, not from a session).

The push is idempotent: Loop-CRM upserts by ``external_id`` and returns a
per-row ``{external_id, status: created|updated|error}`` so we can mark each
local ``Sale`` ``synced``/``failed`` exactly like the existing DataToken loop.
"""

from __future__ import annotations

import logging
import os

from django.utils import timezone

logger = logging.getLogger("pos.loop_ingest")

INGEST_PATH = "/api/v1/ingest/pos/sales/"

# Local statuses Loop-CRM can reconcile into its finance trend. Anything else
# (pending/cancelled) is deliberately not pushed — cancelled sales have no
# recognized revenue and pending sales aren't final yet.
PUSHABLE_STATUS = ("completed", "refunded")


def _cfg() -> tuple[str, str, str]:
    """Return ``(base_url, api_key, workspace_ref)`` from the environment."""
    return (
        os.environ.get("LOOP_CRM_URL", "").rstrip("/"),
        os.environ.get("LOOP_CRM_INGEST_API_KEY", ""),
        os.environ.get("LOOP_CRM_WORKSPACE_REF", ""),
    )


def serialize_sale(sale) -> dict:
    """Serialize a local ``Sale`` (+ items + customer) into Loop-CRM's shape.

    ``external_id`` is namespaced ``formint-pro:<pk>`` so it can never collide
    with a formint-cloud push of the same source row; the response row is
    mapped back to the local PK through the same prefix.
    """
    items = [
        {
            "external_id": f"formint-pro:{sale.pk}:{item.pk}",
            "product_name": item.product_name,
            "quantity": int(item.quantity or 0),
            "unit_price": float(item.unit_price or 0),
            "line_total": float(item.line_total or 0),
        }
        for item in sale.items.all()
    ]

    customer = None
    if sale.customer_id is not None:
        cust = sale.customer
        customer = {
            "external_id": f"formint-pro:{cust.pk}",
            "email": cust.email or "",
            "first_name": cust.first_name or "",
            "last_name": cust.last_name or "",
            "phone": cust.phone or "",
        }

    return {
        "external_id": f"formint-pro:{sale.pk}",
        "status": sale.status,
        "payment_method": sale.payment_method or "cash",
        "subtotal": float(sale.subtotal or 0),
        "tax_amount": float(sale.tax_amount or 0),
        "discount_amount": float(sale.discount_amount or 0),
        "cashback_amount": float(sale.cashback_amount or 0),
        "total": float(sale.total or 0),
        "sale_date": sale.sale_date.isoformat() if sale.sale_date else None,
        "source": "formint-pro",
        "items": items,
        "customer": customer,
        "metadata": {
            "notes": sale.notes or "",
            "group_key": sale.group.group_key if sale.group_id else "",
        },
    }


class PosIngestClient:
    """Push completed/refunded sales to Loop-CRM and mark sync_status back."""

    def __init__(self, base_url: str = "", api_key: str | None = None,
                 workspace_ref: str | None = None, transport=None):
        env_url, env_key, env_ref = _cfg()
        self.base_url = (base_url or env_url).rstrip("/")
        self.api_key = api_key if api_key is not None else env_key
        self.workspace_ref = workspace_ref if workspace_ref is not None else env_ref
        self._transport = transport  # optional httpx transport for tests

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key and self.workspace_ref)

    # ── Collect ──────────────────────────────────────────────────────
    def collect_pending(self, limit: int = 500) -> list:
        """Return pushable sales not yet acknowledged by Loop-CRM."""
        from models.pos import Sale

        return list(
            Sale.objects.filter(status__in=PUSHABLE_STATUS)
            .exclude(sync_status="synced")
            .order_by("id")[:limit]
        )

    # ── Push ─────────────────────────────────────────────────────────
    def push(self, sales) -> dict:
        """POST serialized sales and reconcile each row's ``sync_status``.

        Returns ``{status, count, results}`` (or ``{status, reason}`` when
        unconfigured). A transport/HTTP failure marks every attempted row
        ``failed`` and returns ``{status: "failed", error, count}``.
        """
        if not self.is_configured:
            return {"status": "skipped", "reason": "unconfigured", "count": 0}
        if not sales:
            return {"status": "ok", "count": 0, "results": []}

        payload = {
            "external_ref": self.workspace_ref,
            "sales": [serialize_sale(s) for s in sales],
        }
        headers = {"Content-Type": "application/json", "X-API-Key": self.api_key}

        try:
            import httpx

            client_kwargs = {"timeout": 30.0}
            if self._transport is not None:
                client_kwargs["transport"] = self._transport
            with httpx.Client(**client_kwargs) as client:
                resp = client.post(
                    f"{self.base_url}{INGEST_PATH}",
                    json=payload,
                    headers=headers,
                )
                resp.raise_for_status()
                body = resp.json()
        except Exception as exc:  # noqa: BLE001 - offline/HTTP error
            logger.warning("Loop-CRM ingest push failed: %s", exc)
            self._mark_failed(sales)
            return {"status": "failed", "error": str(exc), "count": len(sales)}

        if not isinstance(body, dict):
            body = {}
        results = body.get("results") or []
        self._apply_results(sales, results)
        return {"status": "ok", "count": len(results), "results": results}

    # ── Reconcile local sync_status from the response ─────────────────
    def _apply_results(self, sales: list, results: list) -> None:
        """Map Loop-CRM's per-row response back onto the local ``Sale`` rows.

        Uses queryset ``.update()`` (not ``.save()``) so the ``flag_for_sync``
        post-save signal doesn't immediately re-flag a just-acknowledged row as
        ``pending`` — the same pattern as ``SyncChangeCollector.acknowledge``.
        """
        from models.pos import Sale

        status_by_pk: dict[int, str] = {}
        for row in results:
            ext = str(row.get("external_id") or "")
            if not ext.startswith("formint-pro:"):
                continue
            try:
                status_by_pk[int(ext.split(":", 1)[1])] = str(row.get("status") or "")
            except ValueError:
                continue

        synced_pks = [s.pk for s in sales if status_by_pk.get(s.pk) in ("created", "updated")]
        failed_pks = [s.pk for s in sales if status_by_pk.get(s.pk) == "error"]

        if synced_pks:
            Sale.objects.filter(pk__in=synced_pks).update(
                sync_status="synced", is_synced=True, synced_at=timezone.now(),
            )
        if failed_pks:
            Sale.objects.filter(pk__in=failed_pks).update(
                sync_status="failed", is_synced=False,
            )

    def _mark_failed(self, sales: list) -> None:
        if not sales:
            return
        from models.pos import Sale

        Sale.objects.filter(pk__in=[s.pk for s in sales]).update(
            sync_status="failed", is_synced=False,
        )


def push_pending_sales(limit: int = 500) -> dict:
    """Convenience entry point: collect + push pending POS sales to Loop-CRM.

    Best-effort: an unconfigured client returns ``{status: "skipped"}`` so
    callers (e.g. the branch scheduler) never fail on a missing Loop-CRM link.
    """
    client = PosIngestClient()
    if not client.is_configured:
        return {"status": "skipped", "reason": "unconfigured", "count": 0}
    return client.push(client.collect_pending(limit=limit))
