"""
POS Solo — Fusion fragment rendering endpoints.

Provides server-rendered HTML fragments that the frontend ``FusionProxy``
component fetches via ``dangerouslySetInnerHTML`` when the health check
signals fragment-first mode.

Each endpoint delegates data retrieval to a ``FragmentComponent`` subclass
from the ``fragments/`` package, mirroring the pos-full pattern.

Mirrors ``pos-full/sidecar/routes/fusion_fragments.py`` but adapted for
the solo's single-restaurant database and use of a local Tauri invoke
bridge instead of a network sidecar.
"""

from __future__ import annotations

import logging
from typing import Any

from django.template import Template, Context
from robyn import Request, Response

logger = logging.getLogger("pos.fusion.fragments")

# ── Inline fragment templates ──────────────────────────────────────

_SUPPLIERS_FRAGMENT_TEMPLATE = """
<div class="fusion-fragment" data-fragment-name="suppliers">
  <h2 class="text-lg font-semibold mb-3">Suppliers ({{ count }})</h2>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
    {% for s in suppliers %}
    <div class="card--glass rounded-xl p-3 flex items-start gap-3">
      <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 text-lg font-bold">
        {{ s.name|first|upper }}
      </div>
      <div class="min-w-0">
        <div class="font-semibold text-slate-900 dark:text-white text-sm truncate">{{ s.name }}</div>
        {% if s.contact_name %}
          <div class="text-xs text-slate-500 truncate">{{ s.contact_name }}</div>
        {% endif %}
        {% if s.phone %}
          <div class="text-xs text-slate-400 truncate">{{ s.phone }}</div>
        {% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
</div>
"""

_DASHBOARD_FRAGMENT_TEMPLATE = """
<div class="fusion-fragment" data-fragment-name="dashboard">
  <div class="flex items-center gap-3 mb-6">
    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold">
      {{ restaurant_name|first|upper }}
    </div>
    <div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white">{{ restaurant_name }}</h1>
      <p class="text-sm text-slate-500 dark:text-slate-400">Dashboard</p>
    </div>
  </div>
  <div class="grid grid-cols-4 gap-4">
    <div class="card--glass rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{{ product_count }}</div>
      <div class="text-xs text-slate-500 mt-1">Products</div>
    </div>
    <div class="card--glass rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{{ customer_count }}</div>
      <div class="text-xs text-slate-500 mt-1">Customers</div>
    </div>
    <div class="card--glass rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ employee_count }}</div>
      <div class="text-xs text-slate-500 mt-1">Employees</div>
    </div>
    <div class="card--glass rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-rose-600 dark:text-rose-400">{{ sale_count }}</div>
      <div class="text-xs text-slate-500 mt-1">Sales</div>
    </div>
  </div>
</div>
"""

_ABOUT_FRAGMENT_TEMPLATE = """
<div class="fusion-fragment" data-fragment-name="about">
  <div class="card--glass rounded-2xl p-6">
    <div class="flex items-center gap-3 mb-4">
      <div class="w-12 h-12 rounded-full bg-gradient-to-br from-teal-400 to-purple-500 flex items-center justify-center text-white">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
        </svg>
      </div>
      <div>
        <h2 class="text-xl font-semibold text-slate-900 dark:text-white">{{ title }}</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">v{{ version }}</p>
      </div>
    </div>
    <p class="text-slate-600 dark:text-gray-300 text-sm leading-relaxed">{{ description }}</p>
    <div class="mt-4 pt-4 border-t border-slate-200 dark:border-white/10">
      <p class="text-xs text-slate-500 dark:text-gray-400">
        &copy; {{ year }} Structa Cloud. All rights reserved.
      </p>
    </div>
  </div>
</div>
"""


def _render_template(template_source: str, context: dict[str, Any]) -> str:
    template = Template(template_source)
    return template.render(Context(context))


def register_fusion_fragment_routes(app: Any) -> None:
    """Register all fragment rendering endpoints on the Robyn app."""

    @app.get("/fusion/render/dashboard")
    async def render_dashboard_fragment(request: Request):
        try:
            from fragments.dashboard import DashboardFragment

            context = DashboardFragment().get_context()
            html = _render_template(_DASHBOARD_FRAGMENT_TEMPLATE, context)
            return Response(
                status_code=200,
                headers={"Content-Type": "text/html; charset=utf-8"},
                description=html,
            )
        except Exception as exc:
            logger.exception("Failed to render dashboard fragment: %s", exc)
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                description='{"error": "Fragment rendering failed"}',
            )

    @app.get("/fusion/render/suppliers")
    async def render_suppliers_fragment(request: Request):
        try:
            from fragments.suppliers import SuppliersFragment

            context = SuppliersFragment().get_context()
            html = _render_template(_SUPPLIERS_FRAGMENT_TEMPLATE, context)
            return Response(
                status_code=200,
                headers={"Content-Type": "text/html; charset=utf-8"},
                description=html,
            )
        except Exception as exc:
            logger.exception("Failed to render suppliers fragment: %s", exc)
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                description='{"error": "Fragment rendering failed"}',
            )

    @app.get("/fusion/render/about")
    async def render_about_fragment(request: Request):
        try:
            from fragments.about import AboutFragment

            context = AboutFragment().get_context()
            html = _render_template(_ABOUT_FRAGMENT_TEMPLATE, context)
            return Response(
                status_code=200,
                headers={"Content-Type": "text/html; charset=utf-8"},
                description=html,
            )
        except Exception as exc:
            logger.exception("Failed to render about fragment: %s", exc)
            return Response(
                status_code=500,
                headers={"Content-Type": "application/json"},
                description='{"error": "Fragment rendering failed"}',
            )

    logger.info("Registered fusion fragment rendering endpoints: /fusion/render/dashboard, /fusion/render/suppliers, /fusion/render/about")
