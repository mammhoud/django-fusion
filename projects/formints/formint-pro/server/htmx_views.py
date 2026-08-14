"""
POS Full — Django views for HTMX table row fragments.

Replaces ``routes/htmx_fragments.py``.  Each endpoint returns styled HTML
``<tr>`` rows that the Astro+Alpine pages swap in via ``hx-get`` +
``hx-target``.

Endpoints:
    GET  /htmx/products/     — product table rows with search/pagination
    DELETE /htmx/products/<id>/ — delete product row (200 empty for hx-target)
    GET  /htmx/customers/    — customer table rows
    DELETE /htmx/customers/<id>/ — delete customer row
    GET  /htmx/inventory/    — inventory transaction rows
    DELETE /htmx/inventory/<id>/ — delete inventory row
    GET  /htmx/sales/        — sales table rows
    DELETE /htmx/sales/<id>/  — delete sale row
"""

import html as _html
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator

from models.pos import Category, Customer, Product, Sale, InventoryTransaction

PAGE_SIZE = 20

# ── Badge helpers ──

def _badge(text: str, color: str) -> str:
    return f'<span class="badge badge-{color} badge-sm">{text}</span>'

def _stock_badge(qty: int) -> str:
    if qty <= 0:
        return _badge("Out", "error")
    if qty < 10:
        return _badge(f"{qty}", "warning")
    return _badge(f"{qty}", "success")

def _status_badge(s: str) -> str:
    m = {"completed": "success", "pending": "warning", "refunded": "error", "cancelled": "neutral"}
    return _badge(s, m.get(s, "neutral"))

def _payment_badge(method: str) -> str:
    m = {"cash": "success", "card": "info", "mobile": "warning"}
    return _badge(method, m.get(method, "neutral"))

def _tier_badge(tier: str) -> str:
    m = {"gold": "warning", "silver": "info", "bronze": "neutral"}
    return _badge(tier, m.get(tier.lower(), "neutral"))

def _inv_type_badge(t: str) -> str:
    m = {"stock_in": "success", "stock_out": "error", "adjustment": "warning", "waste": "neutral", "restock": "info"}
    return _badge(t, m.get(t, "neutral"))

def _esc(val) -> str:
    if val is None:
        return ""
    return _html.escape(str(val))

def _pagination(page_obj, base_url: str) -> str:
    """Return a pagination nav snippet for HTMX."""
    if page_obj.paginator.num_pages <= 1:
        return ""
    parts = ['<div class="join mt-3">']
    if page_obj.has_previous():
        parts.append(
            f'<button class="join-item btn btn-xs" hx-get="{base_url}?page={page_obj.previous_page_number()}" '
            f'hx-target="closest tbody" hx-swap="innerHTML">Prev</button>'
        )
    parts.append(f'<span class="join-item btn btn-xs btn-disabled">Page {page_obj.number}/{page_obj.paginator.num_pages}</span>')
    if page_obj.has_next():
        parts.append(
            f'<button class="join-item btn btn-xs" hx-get="{base_url}?page={page_obj.next_page_number()}" '
            f'hx-target="closest tbody" hx-swap="innerHTML">Next</button>'
        )
    parts.append('</div>')
    return "".join(parts)


def _delete_btn(url: str) -> str:
    return (
        f'<button class="btn btn-ghost btn-xs text-error" '
        f'hx-delete="{url}" hx-confirm="Delete?" '
        f'hx-target="closest tr" hx-swap="outerHTML">Del</button>'
    )


# ══════════════════════════════════════════════════════════════════════════
# Products
# ══════════════════════════════════════════════════════════════════════════

def htmx_products(request: HttpRequest) -> HttpResponse:
    search = request.GET.get("search", "").strip()
    category = request.GET.get("category", "").strip()
    page_num = int(request.GET.get("page", "1"))

    qs = Product.objects.select_related("category").order_by("name")
    if search:
        qs = qs.filter(name__icontains=search)
    if category:
        qs = qs.filter(category__name__iexact=category)

    pg = Paginator(qs, PAGE_SIZE)
    page = pg.get_page(page_num)

    rows = []
    for p in page:
        rows.append(
            f'<tr class="hover">'
            f'<td class="px-3 py-2 text-xs">{_esc(p.id)}</td>'
            f'<td class="px-3 py-2 text-xs font-medium">{_esc(p.name)}</td>'
            f'<td class="px-3 py-2 text-xs">{_esc(p.category.name) if p.category else "—"}</td>'
            f'<td class="px-3 py-2 text-xs tabular-nums">${float(p.price):.2f}</td>'
            f'<td class="px-3 py-2 text-xs">{_stock_badge(p.stock_quantity or 0)}</td>'
            f'<td class="px-3 py-2 text-xs">'
            f'{_delete_btn(f"/htmx/products/{p.id}/")}'
            f'</td></tr>'
        )

    if not rows:
        rows.append('<tr><td colspan="6" class="px-3 py-4 text-center text-xs opacity-50">No products found</td></tr>')

    html_out = "".join(rows) + _pagination(page, "/htmx/products/")
    return HttpResponse(html_out, content_type="text/html")


def htmx_product_delete(request: HttpRequest, product_id: int) -> HttpResponse:
    Product.objects.filter(id=product_id).delete()
    return HttpResponse(status=200)


# ══════════════════════════════════════════════════════════════════════════
# Customers
# ══════════════════════════════════════════════════════════════════════════

def htmx_customers(request: HttpRequest) -> HttpResponse:
    search = request.GET.get("search", "").strip()
    tier = request.GET.get("tier", "").strip()
    page_num = int(request.GET.get("page", "1"))

    qs = Customer.objects.order_by("-created_at")
    if search:
        from django.db.models import Q
        qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone__icontains=search))
    if tier:
        qs = qs.filter(loyalty_tier__iexact=tier)

    pg = Paginator(qs, PAGE_SIZE)
    page = pg.get_page(page_num)

    rows = []
    for c in page:
        name = f"{c.first_name} {c.last_name}".strip()
        rows.append(
            f'<tr class="hover">'
            f'<td class="px-3 py-2 text-xs">{_esc(c.id)}</td>'
            f'<td class="px-3 py-2 text-xs font-medium">{_esc(name)}</td>'
            f'<td class="px-3 py-2 text-xs">{_esc(c.phone or "—")}</td>'
            f'<td class="px-3 py-2 text-xs">{_tier_badge(c.loyalty_tier or "bronze")}</td>'
            f'<td class="px-3 py-2 text-xs tabular-nums">${float(c.total_spent or 0):.2f}</td>'
            f'<td class="px-3 py-2 text-xs">'
            f'{_delete_btn(f"/htmx/customers/{c.id}/")}'
            f'</td></tr>'
        )

    if not rows:
        rows.append('<tr><td colspan="6" class="px-3 py-4 text-center text-xs opacity-50">No customers found</td></tr>')

    html_out = "".join(rows) + _pagination(page, "/htmx/customers/")
    return HttpResponse(html_out, content_type="text/html")


def htmx_customer_delete(request: HttpRequest, customer_id: int) -> HttpResponse:
    Customer.objects.filter(id=customer_id).delete()
    return HttpResponse(status=200)


# ══════════════════════════════════════════════════════════════════════════
# Inventory
# ══════════════════════════════════════════════════════════════════════════

def htmx_inventory(request: HttpRequest) -> HttpResponse:
    search = request.GET.get("search", "").strip()
    tx_type = request.GET.get("type", "").strip()
    page_num = int(request.GET.get("page", "1"))

    qs = InventoryTransaction.objects.select_related("product").order_by("-created_at")
    if search:
        qs = qs.filter(reference__icontains=search) | qs.filter(notes__icontains=search)
    if tx_type:
        qs = qs.filter(transaction_type=tx_type)

    pg = Paginator(qs, PAGE_SIZE)
    page = pg.get_page(page_num)

    rows = []
    for tx in page:
        product_name = tx.product.name if hasattr(tx, "product") and tx.product else "—"
        rows.append(
            f'<tr class="hover">'
            f'<td class="px-3 py-2 text-xs">{_esc(tx.id)}</td>'
            f'<td class="px-3 py-2 text-xs">{_esc(product_name)}</td>'
            f'<td class="px-3 py-2 text-xs">{_inv_type_badge(tx.transaction_type)}</td>'
            f'<td class="px-3 py-2 text-xs tabular-nums">{tx.quantity}</td>'
            f'<td class="px-3 py-2 text-xs">{_esc(tx.reference or "—")}</td>'
            f'<td class="px-3 py-2 text-xs opacity-50">{_esc(tx.created_at.strftime("%Y-%m-%d") if tx.created_at else "—")}</td>'
            f'<td class="px-3 py-2 text-xs">'
            f'{_delete_btn(f"/htmx/inventory/{tx.id}/")}'
            f'</td></tr>'
        )

    if not rows:
        rows.append('<tr><td colspan="7" class="px-3 py-4 text-center text-xs opacity-50">No inventory transactions found</td></tr>')

    html_out = "".join(rows) + _pagination(page, "/htmx/inventory/")
    return HttpResponse(html_out, content_type="text/html")


def htmx_inventory_delete(request: HttpRequest, tx_id: int) -> HttpResponse:
    InventoryTransaction.objects.filter(id=tx_id).delete()
    return HttpResponse(status=200)


# ══════════════════════════════════════════════════════════════════════════
# Sales
# ══════════════════════════════════════════════════════════════════════════

def htmx_sales(request: HttpRequest) -> HttpResponse:
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    payment = request.GET.get("payment", "").strip()
    page_num = int(request.GET.get("page", "1"))

    qs = Sale.objects.select_related("customer").order_by("-sale_date")
    if search:
        qs = qs.filter(id__icontains=search)
    if status:
        qs = qs.filter(status=status)
    if payment:
        qs = qs.filter(payment_method=payment)

    pg = Paginator(qs, PAGE_SIZE)
    page = pg.get_page(page_num)

    rows = []
    for s in page:
        customer_name = f"{s.customer.first_name} {s.customer.last_name}".strip() if s.customer else "Walk-in"
        rows.append(
            f'<tr class="hover">'
            f'<td class="px-3 py-2 text-xs">#{_esc(s.id)}</td>'
            f'<td class="px-3 py-2 text-xs">{_esc(customer_name)}</td>'
            f'<td class="px-3 py-2 text-xs tabular-nums">${float(s.total):.2f}</td>'
            f'<td class="px-3 py-2 text-xs">{_payment_badge(s.payment_method)}</td>'
            f'<td class="px-3 py-2 text-xs">{_status_badge(s.status)}</td>'
            f'<td class="px-3 py-2 text-xs opacity-50">{_esc(s.sale_date.strftime("%Y-%m-%d %H:%M") if s.sale_date else "—")}</td>'
            f'<td class="px-3 py-2 text-xs">'
            f'{_delete_btn(f"/htmx/sales/{s.id}/")}'
            f'</td></tr>'
        )

    if not rows:
        rows.append('<tr><td colspan="7" class="px-3 py-4 text-center text-xs opacity-50">No sales found</td></tr>')

    html_out = "".join(rows) + _pagination(page, "/htmx/sales/")
    return HttpResponse(html_out, content_type="text/html")


def htmx_sale_delete(request: HttpRequest, sale_id: int) -> HttpResponse:
    Sale.objects.filter(id=sale_id).delete()
    return HttpResponse(status=200)
