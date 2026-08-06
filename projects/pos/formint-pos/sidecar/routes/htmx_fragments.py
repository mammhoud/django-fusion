"""
POS Full -- HTMX fragment endpoints for inline table updates.

Returns styled HTML ``<tbody>`` fragments that replace the Alpine.js-rendered
table bodies via ``hx-get`` + ``hx-target`` + ``hx-trigger``. Each endpoint
accepts query parameters for server-side search, pagination, and filtering.

Endpoints::

    GET /htmx/products/    ?search=latte&category=hot-drinks&page=1
    GET /htmx/customers/   ?search=jane&tier=gold&page=1
    GET /htmx/inventory/   ?search=coffee&type=in&page=1
    GET /htmx/sales/       ?search=john&status=completed&page=1

Each returns ``text/html`` with one or more ``<tr>`` rows styled with the
same Tailwind utility classes used in the Astro pages. An empty result set
returns a single ``<tr>`` with a colspan-full "no results" message.

Frontend usage (Astro + HTMX)::

    <table class="data-table">
      <thead>...</thead>
      <tbody
        hx-get="/htmx/products/"
        hx-trigger="load, every 30s"
        hx-swap="innerHTML"
      >
        <!-- Skeleton loading shown until HTMX replaces it -->
      </tbody>
    </table>
"""

from __future__ import annotations

import html as _html
import logging
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db.models import Q

from robyn import Request, Response

logger = logging.getLogger("pos.htmx.fragments")

# ==========================================================================
# Helpers
# ==========================================================================

_PER_PAGE_DEFAULT = 25
_MAX_PER_PAGE = 100


def _parse_int(value: str | None, default: int) -> int:
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def _parse_page(query_params: dict) -> tuple[int, int]:
    """Return ``(page_number, per_page)`` clamped to safe ranges."""
    page = max(1, _parse_int(query_params.get("page"), 1))
    per_page = min(_MAX_PER_PAGE, max(1, _parse_int(query_params.get("per_page"), _PER_PAGE_DEFAULT)))
    return page, per_page


def _escape(value: Any) -> str:
    """HTML-escape a value for safe rendering inside a ``<td>``."""
    if value is None:
        return "\u2014"
    return _html.escape(str(value), quote=False)


def _currency(value: Decimal) -> str:
    return f"${value:,.2f}"


def _badge(text: str, kind: str = "default") -> str:
    """Return an inline status badge ``<span>`` matching Tailwind badge styles."""
    color_map: dict[str, str] = {
        "success": "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
        "warning": "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400",
        "error":   "border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-400",
        "info":    "border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400",
        "neutral": "border-slate-500/30 bg-slate-500/10 text-slate-600 dark:text-slate-400",
    }
    classes = color_map.get(kind, color_map["neutral"])
    escaped = _escape(text)
    return (
        '<span class="badge inline-flex items-center px-2 py-0.5 '
        f'rounded-full text-xs font-medium border {classes}">{escaped}</span>'
    )


def _pagination_bar(page: int, per_page: int, total: int, base_url: str, params: dict) -> str:
    """Return a pagination control bar HTML snippet with HTMX attributes."""
    if total <= per_page:
        return ""
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page + 1
    end = min(page * per_page, total)

    prev_params = {**params, "page": str(max(1, page - 1))}
    next_params = {**params, "page": str(min(total_pages, page + 1))}
    prev_href = f"{base_url}?{urlencode(prev_params)}"
    next_href = f"{base_url}?{urlencode(next_params)}"

    prev_disabled = "opacity-40 pointer-events-none" if page <= 1 else ""
    next_disabled = "opacity-40 pointer-events-none" if page >= total_pages else ""

    return (
        '<div class="flex items-center justify-between p-3 border-t '
        'border-[var(--color-border-subtle)] text-xs">'
        f"<span>Showing {start}&ndash;{end} of {total}</span>"
        '<div class="flex gap-1">'
        f'<a hx-get="{prev_href}" hx-target="closest tbody" hx-swap="innerHTML" '
        f'class="btn btn-ghost btn-xs {prev_disabled}">&larr; Prev</a>'
        f'<a hx-get="{next_href}" hx-target="closest tbody" hx-swap="innerHTML" '
        f'class="btn btn-ghost btn-xs {next_disabled}">Next &rarr;</a>'
        "</div></div>"
    )


def _empty_row(colspan: int, message: str = "No results found.") -> str:
    return (
        f'<tr><td colspan="{colspan}" '
        f'class="px-3 py-12 text-center opacity-50 text-sm">{_escape(message)}</td></tr>'
    )


def _wrap_tbody(rows: str, pagination: str = "") -> str:
    return rows + pagination


# ==========================================================================
# Product fragment -- GET /htmx/products/
# ==========================================================================

_PRODUCT_DELETE_BTN = (
    '<button class="btn btn-ghost btn-xs" title="Delete" '
    'hx-delete="/htmx/products/{id}/" hx-target="closest tr" '
    'hx-swap="outerHTML" hx-confirm="Delete this product?">'
    '\U0001f5d1\ufe0f</button>'
)


def _product_row(p: Any) -> str:
    cat_name = p.category.name if p.category else "\u2014"
    if p.stock_quantity <= p.low_stock_threshold:
        stock_cell = _badge("Low", "warning")
    else:
        stock_cell = _badge(str(p.stock_quantity), "success")
    actions = (
        '<div class="flex gap-1">'
        '<button class="btn btn-ghost btn-xs" title="Edit">\u270f\ufe0f</button>'
        + _PRODUCT_DELETE_BTN.replace("{id}", str(p.id))
        + "</div>"
    )
    return (
        '<tr class="cursor-pointer hover:bg-[var(--color-surface-hover)]">'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{p.id}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs font-medium">{_escape(p.name)}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{_currency(p.price)}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs">{_escape(cat_name)}</span></td>'
        '<td class="px-3 py-2"><span class="text-xs">item</span></td>'
        f"<td class=\"px-3 py-2\">{stock_cell}</td>"
        f'<td class="px-3 py-2 w-20">{actions}</td>'
        "</tr>"
    )


async def products_fragment(request: Request) -> Response:
    """GET /htmx/products/?search=&category=&page=&per_page="""
    try:
        from models.pos import Product

        params = dict(request.query_params)
        page, per_page = _parse_page(params)
        search = (params.get("search") or "").strip()
        category = (params.get("category") or "").strip()

        qs = Product.objects.select_related("category").order_by("name")

        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(sku__icontains=search) | Q(barcode__icontains=search)
            )
        if category:
            qs = qs.filter(category__slug=category)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        rows = "".join(_product_row(p) for p in page_obj.object_list)
        if not rows:
            rows = _empty_row(7, "No products found. Try a different search.")

        pagination = _pagination_bar(page, per_page, paginator.count, "/htmx/products/", params)
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_wrap_tbody(rows, pagination),
        )
    except Exception as exc:
        logger.exception("products_fragment failed: %s", exc)
        return Response(
            status_code=500,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_empty_row(7, "Failed to load products."),
        )


async def product_delete(request: Request) -> Response:
    """DELETE /htmx/products/<id>/ -- remove a product row via HTMX."""
    try:
        from models.pos import Product

        pk = request.path_params.get("id")
        Product.objects.filter(pk=pk).delete()
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description="",
        )
    except Exception as exc:
        logger.exception("product_delete failed: %s", exc)
        return Response(status_code=500, headers={"Content-Type": "text/html"}, description="")


# ==========================================================================
# Customer fragment -- GET /htmx/customers/
# ==========================================================================

_CUSTOMER_DELETE_BTN = (
    '<button class="btn btn-ghost btn-xs" title="Delete" '
    'hx-delete="/htmx/customers/{id}/" hx-target="closest tr" '
    'hx-swap="outerHTML" hx-confirm="Delete this customer?">'
    '\U0001f5d1\ufe0f</button>'
)


def _customer_row(c: Any) -> str:
    name = f"{c.first_name} {c.last_name}".strip() or c.email or "Unknown"
    tier_name = c.client_category.name if c.client_category else None
    tier_map = {"Gold": "success", "Silver": "info", "Bronze": "neutral"}
    tier_badge = _badge(tier_name, tier_map.get(tier_name or "", "neutral")) if tier_name else ""
    display_name = f"{_escape(name)} {tier_badge}" if tier_badge else _escape(name)
    order_count = c.sales.count()
    joined = c.created_at.strftime("%Y-%m-%d") if c.created_at else "\u2014"
    actions = (
        '<div class="flex gap-1">'
        '<button class="btn btn-ghost btn-xs" title="Edit">\u270f\ufe0f</button>'
        + _CUSTOMER_DELETE_BTN.replace("{id}", str(c.id))
        + "</div>"
    )
    return (
        '<tr class="cursor-pointer hover:bg-[var(--color-surface-hover)]">'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{c.id}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs font-medium">{display_name}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs">{_escape(c.phone)}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs">{_escape(c.email)}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{order_count}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs">{joined}</span></td>'
        f'<td class="px-3 py-2 w-20">{actions}</td>'
        "</tr>"
    )


async def customers_fragment(request: Request) -> Response:
    """GET /htmx/customers/?search=&tier=&page=&per_page="""
    try:
        from models.pos import Customer

        params = dict(request.query_params)
        page, per_page = _parse_page(params)
        search = (params.get("search") or "").strip()
        tier = (params.get("tier") or "").strip()

        qs = Customer.objects.select_related("client_category").order_by("-created_at")

        if search:
            qs = qs.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        if tier:
            qs = qs.filter(client_category__name__iexact=tier)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        rows = "".join(_customer_row(c) for c in page_obj.object_list)
        if not rows:
            rows = _empty_row(7, "No customers found. Try a different search.")

        pagination = _pagination_bar(page, per_page, paginator.count, "/htmx/customers/", params)
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_wrap_tbody(rows, pagination),
        )
    except Exception as exc:
        logger.exception("customers_fragment failed: %s", exc)
        return Response(
            status_code=500,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_empty_row(7, "Failed to load customers."),
        )


async def customer_delete(request: Request) -> Response:
    """DELETE /htmx/customers/<id>/"""
    try:
        from models.pos import Customer
        pk = request.path_params.get("id")
        Customer.objects.filter(pk=pk).delete()
        return Response(status_code=200, headers={"Content-Type": "text/html"}, description="")
    except Exception as exc:
        logger.exception("customer_delete failed: %s", exc)
        return Response(status_code=500, headers={"Content-Type": "text/html"}, description="")


# ==========================================================================
# Inventory fragment -- GET /htmx/inventory/
# ==========================================================================

_TYPE_BADGE_MAP = {
    "in": ("Stock In", "success"),
    "out": ("Stock Out", "error"),
    "adjustment": ("Adjustment", "warning"),
    "return": ("Return", "info"),
    "restock": ("Restock", "success"),
    "transfer_in": ("Transfer In", "info"),
    "transfer_out": ("Transfer Out", "warning"),
    "waste": ("Waste", "error"),
}

_INVENTORY_DELETE_BTN = (
    '<button class="btn btn-ghost btn-xs" title="Delete" '
    'hx-delete="/htmx/inventory/{id}/" hx-target="closest tr" '
    'hx-swap="outerHTML" hx-confirm="Delete this record?">'
    '\U0001f5d1\ufe0f</button>'
)


def _inventory_row(tx: Any) -> str:
    label, kind = _TYPE_BADGE_MAP.get(
        tx.transaction_type,
        (tx.transaction_type.replace("_", " ").title(), "neutral"),
    )
    type_badge = _badge(label, kind)
    product_name = tx.product.name if tx.product else "Unknown"
    is_inflow = tx.transaction_type in ("in", "return", "restock", "transfer_in")
    qty_sign = "+" if is_inflow else "\u2013"
    qty_display = f"{qty_sign}{tx.quantity}"
    date_str = tx.created_at.strftime("%Y-%m-%d %H:%M") if tx.created_at else "\u2014"
    actions = (
        '<div class="flex gap-1">'
        '<button class="btn btn-ghost btn-xs" title="Edit">\u270f\ufe0f</button>'
        + _INVENTORY_DELETE_BTN.replace("{id}", str(tx.id))
        + "</div>"
    )
    return (
        '<tr class="cursor-pointer hover:bg-[var(--color-surface-hover)]">'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{tx.id}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs font-medium">{_escape(product_name)}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{qty_display}</span></td>'
        f"<td class=\"px-3 py-2\">{type_badge}</td>"
        f'<td class="px-3 py-2"><span class="text-xs">{date_str}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs max-w-[200px] truncate block">{_escape(tx.notes)}</span></td>'
        f'<td class="px-3 py-2 w-20">{actions}</td>'
        "</tr>"
    )


async def inventory_fragment(request: Request) -> Response:
    """GET /htmx/inventory/?search=&type=&page=&per_page="""
    try:
        from models.pos import InventoryTransaction

        params = dict(request.query_params)
        page, per_page = _parse_page(params)
        search = (params.get("search") or "").strip()
        tx_type = (params.get("type") or "").strip()

        qs = InventoryTransaction.objects.select_related("product").order_by("-created_at")

        if search:
            qs = qs.filter(
                Q(product__name__icontains=search)
                | Q(reference__icontains=search)
                | Q(notes__icontains=search)
            )
        if tx_type:
            qs = qs.filter(transaction_type=tx_type)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        rows = "".join(_inventory_row(tx) for tx in page_obj.object_list)
        if not rows:
            rows = _empty_row(7, "No inventory records found. Try a different search.")

        pagination = _pagination_bar(page, per_page, paginator.count, "/htmx/inventory/", params)
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_wrap_tbody(rows, pagination),
        )
    except Exception as exc:
        logger.exception("inventory_fragment failed: %s", exc)
        return Response(
            status_code=500,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_empty_row(7, "Failed to load inventory."),
        )


async def inventory_delete(request: Request) -> Response:
    """DELETE /htmx/inventory/<id>/"""
    try:
        from models.pos import InventoryTransaction
        pk = request.path_params.get("id")
        InventoryTransaction.objects.filter(pk=pk).delete()
        return Response(status_code=200, headers={"Content-Type": "text/html"}, description="")
    except Exception as exc:
        logger.exception("inventory_delete failed: %s", exc)
        return Response(status_code=500, headers={"Content-Type": "text/html"}, description="")


# ==========================================================================
# Sales fragment -- GET /htmx/sales/
# ==========================================================================

_STATUS_BADGE_MAP = {
    "completed": ("Completed", "success"),
    "pending": ("Pending", "warning"),
    "refunded": ("Refunded", "error"),
    "cancelled": ("Cancelled", "neutral"),
}

_PAYMENT_BADGE_MAP = {
    "cash": ("Cash", "success"),
    "card": ("Card", "info"),
    "mobile": ("Mobile", "warning"),
    "mixed": ("Mixed", "neutral"),
    "credit": ("Credit", "info"),
}

_SALE_DELETE_BTN = (
    '<button class="btn btn-ghost btn-xs" title="Delete" '
    'hx-delete="/htmx/sales/{id}/" hx-target="closest tr" '
    'hx-swap="outerHTML" hx-confirm="Delete this sale?">'
    '\U0001f5d1\ufe0f</button>'
)


def _sale_row(s: Any) -> str:
    status_label, status_kind = _STATUS_BADGE_MAP.get(s.status, (s.status.title(), "neutral"))
    status_badge = _badge(status_label, status_kind)
    payment_label, payment_kind = _PAYMENT_BADGE_MAP.get(
        s.payment_method, (s.payment_method.title(), "neutral")
    )
    payment_badge = _badge(payment_label, payment_kind)

    customer_name = (
        f"{s.customer.first_name} {s.customer.last_name}".strip()
        if s.customer
        else "Walk-in"
    )
    date_str = s.sale_date.strftime("%Y-%m-%d %H:%M") if s.sale_date else "\u2014"
    item_count = s.items.count()
    actions = (
        '<div class="flex gap-1">'
        '<button class="btn btn-ghost btn-xs" title="View">\U0001f441\ufe0f</button>'
        + _SALE_DELETE_BTN.replace("{id}", str(s.id))
        + "</div>"
    )
    return (
        '<tr class="cursor-pointer hover:bg-[var(--color-surface-hover)]">'
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">#{s.id}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs">{date_str}</span></td>'
        f'<td class="px-3 py-2"><span class="text-xs font-medium">{_escape(customer_name)}</span></td>'
        '<td class="px-3 py-2">'
        f'<span class="text-xs font-mono tabular-nums">{_currency(s.total)}</span>'
        f'<span class="text-xs opacity-50 ml-1">{payment_badge}</span>'
        "</td>"
        f"<td class=\"px-3 py-2\">{status_badge}</td>"
        f'<td class="px-3 py-2"><span class="text-xs tabular-nums">{item_count} items</span></td>'
        f'<td class="px-3 py-2 w-20">{actions}</td>'
        "</tr>"
    )


async def sales_fragment(request: Request) -> Response:
    """GET /htmx/sales/?search=&status=&payment=&page=&per_page="""
    try:
        from models.pos import Sale

        params = dict(request.query_params)
        page, per_page = _parse_page(params)
        search = (params.get("search") or "").strip()
        status_filter = (params.get("status") or "").strip()
        payment_filter = (params.get("payment") or "").strip()

        qs = (
            Sale.objects.select_related("customer")
            .prefetch_related("items")
            .order_by("-sale_date")
        )

        if search:
            qs = qs.filter(
                Q(customer__first_name__icontains=search)
                | Q(customer__last_name__icontains=search)
                | Q(notes__icontains=search)
            )
        if status_filter:
            qs = qs.filter(status=status_filter)
        if payment_filter:
            qs = qs.filter(payment_method=payment_filter)

        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        rows = "".join(_sale_row(s) for s in page_obj.object_list)
        if not rows:
            rows = _empty_row(7, "No transactions found. Try a different search.")

        pagination = _pagination_bar(page, per_page, paginator.count, "/htmx/sales/", params)
        return Response(
            status_code=200,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_wrap_tbody(rows, pagination),
        )
    except Exception as exc:
        logger.exception("sales_fragment failed: %s", exc)
        return Response(
            status_code=500,
            headers={"Content-Type": "text/html; charset=utf-8"},
            description=_empty_row(7, "Failed to load transactions."),
        )


async def sale_delete(request: Request) -> Response:
    """DELETE /htmx/sales/<id>/"""
    try:
        from models.pos import Sale
        pk = request.path_params.get("id")
        Sale.objects.filter(pk=pk).delete()
        return Response(status_code=200, headers={"Content-Type": "text/html"}, description="")
    except Exception as exc:
        logger.exception("sale_delete failed: %s", exc)
        return Response(status_code=500, headers={"Content-Type": "text/html"}, description="")


# ==========================================================================
# Route registration
# ==========================================================================


def register_htmx_fragment_routes(app: Any) -> None:
    """Register all HTMX fragment endpoints on the Robyn app.

    Call from ``routes/__init__.py``::

        from routes import htmx_fragments
        htmx_fragments.register_htmx_fragment_routes(app)
    """

    # Products
    app.add_route("/htmx/products/", "GET", products_fragment)
    app.add_route("/htmx/products/:id/", "DELETE", product_delete)

    # Customers
    app.add_route("/htmx/customers/", "GET", customers_fragment)
    app.add_route("/htmx/customers/:id/", "DELETE", customer_delete)

    # Inventory
    app.add_route("/htmx/inventory/", "GET", inventory_fragment)
    app.add_route("/htmx/inventory/:id/", "DELETE", inventory_delete)

    # Sales
    app.add_route("/htmx/sales/", "GET", sales_fragment)
    app.add_route("/htmx/sales/:id/", "DELETE", sale_delete)

    logger.info(
        "Registered HTMX fragment endpoints: "
        "/htmx/products/, /htmx/customers/, /htmx/inventory/, /htmx/sales/"
    )
