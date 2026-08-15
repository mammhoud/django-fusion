"""
POS Full — Django views for fusion fragment HTML renders.

Replaces ``routes/fusion_fragments.py``.  These endpoints render the
server-side fusion component fragments (dashboard, suppliers, about)
that were previously served via Robyn.

Endpoints:
    GET  /fusion/render/dashboard  — dashboard fragment HTML
    GET  /fusion/render/suppliers  — suppliers fragment HTML
    GET  /fusion/render/about      — about fragment HTML
"""

import logging
import os
from pathlib import Path

from django.http import HttpRequest, HttpResponse

from models.pos import Category, Customer, Employee, Product, Sale
from models.node import Node

logger = logging.getLogger("pos.fusion_views")


def _html_response(content: str, status: int = 200) -> HttpResponse:
    return HttpResponse(content, status=status, content_type="text/html; charset=utf-8")


def fusion_render_dashboard(request: HttpRequest) -> HttpResponse:
    """Render the dashboard fragment with live stats."""
    products_count = Product.objects.filter(is_active=True).count()
    sales_count = Sale.objects.count()
    customers_count = Customer.objects.count()
    employees_count = Employee.objects.filter(is_active=True).count()
    nodes_online = Node.objects.filter(status="online").count()
    nodes_offline = Node.objects.filter(status="offline").count()

    html = (
        '<div class="fusion-dashboard" hx-swap-oob="true" id="fusion-dashboard">'
        '  <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">'
        f'    <div class="stat-card"><div class="stat-value">{products_count}</div><div class="stat-label">Products</div></div>'
        f'    <div class="stat-card"><div class="stat-value">{sales_count}</div><div class="stat-label">Sales</div></div>'
        f'    <div class="stat-card"><div class="stat-value">{customers_count}</div><div class="stat-label">Customers</div></div>'
        f'    <div class="stat-card"><div class="stat-value">{employees_count}</div><div class="stat-label">Employees</div></div>'
        f'    <div class="stat-card"><div class="stat-value text-success">{nodes_online}</div><div class="stat-label">Nodes Online</div></div>'
        f'    <div class="stat-card"><div class="stat-value text-error">{nodes_offline}</div><div class="stat-label">Nodes Offline</div></div>'
        '  </div>'
        '</div>'
    )
    return _html_response(html)


def fusion_render_suppliers(request: HttpRequest) -> HttpResponse:
    """Render the suppliers list fragment."""
    from models.inventory import Supplier
    suppliers = Supplier.objects.filter(is_active=True).order_by("name")[:20]

    rows = []
    for s in suppliers:
        rows.append(
            '<tr class="hover">'
            f'<td class="px-3 py-2 text-sm font-medium">{s.name}</td>'
            f'<td class="px-3 py-2 text-xs">{s.contact_person or "—"}</td>'
            f'<td class="px-3 py-2 text-xs">{s.phone or "—"}</td>'
            f'<td class="px-3 py-2 text-xs">{s.email or "—"}</td>'
            '</tr>'
        )

    tbody = (
        "".join(rows) if rows
        else '<tr><td colspan="4" class="text-center opacity-50 py-4">No suppliers</td></tr>'
    )

    html = (
        '<div class="fusion-suppliers" hx-swap-oob="true" id="fusion-suppliers">'
        '  <table class="table table-sm">'
        '    <thead><tr><th>Name</th><th>Contact</th><th>Phone</th><th>Email</th></tr></thead>'
        f'    <tbody>{tbody}</tbody>'
        '  </table>'
        '</div>'
    )
    return _html_response(html)


def fusion_render_about(request: HttpRequest) -> HttpResponse:
    """Render the about/system info fragment."""
    try:
        from about import __version__, __title_full__
    except ImportError:
        __version__ = "1.0.0"
        __title_full__ = "Formint POS Professional"

    db_path = Path(__file__).resolve().parent.parent / "restaurant.db"
    db_size = "N/A"
    if db_path.exists():
        size_bytes = db_path.stat().st_size
        if size_bytes > 1024 * 1024:
            db_size = f"{size_bytes / (1024*1024):.1f} MB"
        else:
            db_size = f"{size_bytes / 1024:.0f} KB"

    python_version = os.environ.get("PYTHON_VERSION", "3.11")

    html = (
        '<div class="fusion-about" hx-swap-oob="true" id="fusion-about">'
        '  <div class="space-y-2 text-sm">'
        f'    <div class="flex justify-between py-1 border-b border-base-300"><span class="opacity-60">Application</span><span class="font-medium">{__title_full__}</span></div>'
        f'    <div class="flex justify-between py-1 border-b border-base-300"><span class="opacity-60">Version</span><span class="font-medium">v{__version__}</span></div>'
        f'    <div class="flex justify-between py-1 border-b border-base-300"><span class="opacity-60">Database</span><span class="font-medium">SQLite ({db_size})</span></div>'
        '    <div class="flex justify-between py-1 border-b border-base-300"><span class="opacity-60">Models</span><span class="font-medium">30+</span></div>'
        f'    <div class="flex justify-between py-1 border-b border-base-300"><span class="opacity-60">Python</span><span class="font-medium">{python_version}</span></div>'
        '    <div class="flex justify-between py-1 border-b border-base-300"><span class="opacity-60">Stack</span><span class="font-medium">Django + django-bolt + Ninja + Channels</span></div>'
        '  </div>'
        '</div>'
    )
    return _html_response(html)
