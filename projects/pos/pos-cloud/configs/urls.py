"""POS Cloud — URL configuration with Unfold admin, django-fusion, REST API."""

import msgspec

from django.contrib import admin
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt

_root_health = lambda r: JsonResponse({"status": "healthy", "service": "pos-cloud"})


# ── BoltAPI Analytics Dashboard ─────────────────────────────────
# Served at /apis/data/ as the root bolt dashboard page.
# The middleware injects bolt-sync-events.js for live WebSocket updates.

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>POS Cloud Analytics</title>
<style>
  :root {
    --bg-dark: #0f172a;
    --bg-card: #1e293b;
    --accent: #10b981;
    --accent-glow: rgba(16,185,129,0.15);
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: #334155;
    --orange: #f59e0b;
    --blue: #3b82f6;
    --purple: #8b5cf6;
    --red: #ef4444;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body {
    background:var(--bg-dark);color:var(--text-main);
    font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    min-height:100vh;
  }
  .topbar {
    display:flex;justify-content:space-between;align-items:center;
    padding:1.25rem 2rem;background:var(--bg-card);
    border-bottom:1px solid var(--border);
  }
  .topbar-brand{display:flex;align-items:center;gap:.75rem}
  .topbar-brand img{width:32px;height:32px}
  .topbar-brand h1{font-size:1.25rem;color:var(--accent);font-weight:700}
  .topbar-brand span{color:var(--text-muted);font-size:.85rem}
  .topbar-actions{display:flex;gap:.75rem;align-items:center}
  .btn {
    display:inline-flex;align-items:center;gap:.4rem;
    padding:.5rem 1rem;border-radius:8px;font-size:.85rem;
    font-weight:600;text-decoration:none;transition:all .15s;
    border:1px solid transparent;cursor:pointer;
  }
  .btn-primary{background:var(--accent);color:#fff}
  .btn-primary:hover{background:#059669;box-shadow:0 0 12px var(--accent-glow)}
  .btn-ghost{color:var(--text-muted);border-color:var(--border)}
  .btn-ghost:hover{color:var(--text-main);border-color:var(--text-muted)}
  .main{padding:2rem;max-width:1280px;margin:0 auto}
  .kpi-grid {
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:1rem;margin-bottom:2rem;
  }
  .kpi-card {
    background:var(--bg-card);border:1px solid var(--border);
    border-radius:12px;padding:1.25rem;transition:all .3s;
    position:relative;overflow:hidden;
  }
  .kpi-card.pulse{animation:kpiPulse .6s ease}
  @keyframes kpiPulse {
    0%,100%{box-shadow:0 0 0 0 var(--accent-glow)}
    50%{box-shadow:0 0 0 8px transparent}
  }
  .kpi-icon{font-size:1.4rem;margin-bottom:.5rem}
  .kpi-label{color:var(--text-muted);font-size:.8rem;font-weight:600;text-transform:uppercase;letter-spacing:.05em}
  .kpi-value{font-size:2rem;font-weight:700;margin-top:.35rem;line-height:1.1}
  .kpi-value.accent-green{color:var(--accent)}
  .kpi-value.accent-orange{color:var(--orange)}
  .kpi-value.accent-blue{color:var(--blue)}
  .kpi-value.accent-purple{color:var(--purple)}
  .kpi-delta {
    font-size:.75rem;margin-top:.35rem;font-weight:600;
    display:none;align-items:center;gap:.25rem;
  }
  .kpi-delta.show{display:inline-flex}
  .kpi-delta.up{color:var(--accent)}
  .section-title {
    color:var(--text-muted);font-size:.85rem;font-weight:600;
    text-transform:uppercase;letter-spacing:.05em;
    margin-bottom:1rem;margin-top:1.5rem;
  }
  .links-grid{display:flex;gap:.75rem;flex-wrap:wrap}
  .link-card {
    background:var(--bg-card);border:1px solid var(--border);
    padding:.9rem 1.25rem;border-radius:10px;color:var(--text-main);
    text-decoration:none;flex:1;min-width:140px;text-align:center;
    font-size:.85rem;font-weight:500;transition:all .2s;
  }
  .link-card:hover{border-color:var(--accent);background:#1e293b;transform:translateY(-1px)}
  .footer-bar {
    text-align:center;padding:1.5rem;color:var(--text-muted);
    font-size:.78rem;border-top:1px solid var(--border);margin-top:2rem;
  }
  .footer-bar a{color:var(--accent);text-decoration:none}
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-brand">
    <img src="/static/pos-crest.svg" alt="POS Crest" onerror="this.style.display='none'">
    <div>
      <h1>POS Cloud Analytics</h1>
      <span>Real-time multi-branch dashboard</span>
    </div>
  </div>
  <div class="topbar-actions">
    <span style="display:flex;align-items:center;gap:.35rem">
      <span id="sync-status-dot" style="width:8px;height:8px;border-radius:50%;background:#64748b;display:inline-block"></span>
      <span id="sync-status-label" style="font-size:.78rem;color:var(--text-muted)">Connecting…</span>
    </span>
    <a href="/admin/" class="btn btn-primary">⚙ Unfold Admin</a>
  </div>
</div>

<div class="main">
  <div class="kpi-grid">
    <div class="kpi-card" data-sync-card="products">
      <div class="kpi-icon">📦</div>
      <div class="kpi-label">Total Products</div>
      <div class="kpi-value accent-green" id="kpi-products" data-sync-count="products">—</div>
    </div>
    <div class="kpi-card" data-sync-card="sales">
      <div class="kpi-icon">🛒</div>
      <div class="kpi-label">Total Sales</div>
      <div class="kpi-value accent-orange" id="kpi-sales" data-sync-count="sales">—</div>
    </div>
    <div class="kpi-card" data-sync-card="inventory">
      <div class="kpi-icon">📋</div>
      <div class="kpi-label">Inventory Txs</div>
      <div class="kpi-value accent-blue" id="kpi-inventory" data-sync-count="inventory">—</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-icon">🏪</div>
      <div class="kpi-label">Active Branches</div>
      <div class="kpi-value accent-purple" id="kpi-branches">—</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-icon">🏢</div>
      <div class="kpi-label">Organizations</div>
      <div class="kpi-value" id="kpi-orgs">—</div>
    </div>
    <div class="kpi-card" data-sync-card="heartbeat">
      <div class="kpi-icon">📡</div>
      <div class="kpi-label">Sync Events</div>
      <div class="kpi-value accent-green" id="kpi-syncs" data-sync-count="heartbeat">—</div>
    </div>
  </div>

  <div class="section-title">📊 API Data Endpoints</div>
  <div class="links-grid">
    <a href="/apis/data/products" class="link-card">📦 Products</a>
    <a href="/apis/data/sales" class="link-card">🛒 Sales</a>
    <a href="/apis/data/inventory" class="link-card">📋 Inventory</a>
    <a href="/apis/data/branches" class="link-card">🏪 Branches</a>
    <a href="/apis/data/sync-logs" class="link-card">📡 Sync Logs</a>
  </div>

  <div class="section-title">🔗 Quick Links</div>
  <div class="links-grid">
    <a href="/admin/core/organization/" class="link-card">🏢 Organizations</a>
    <a href="/admin/core/branch/" class="link-card">🏪 Branches</a>
    <a href="/admin/core/lead/" class="link-card">👤 Leads</a>
    <a href="/admin/core/deal/" class="link-card">🤝 Deals</a>
    <a href="/admin/core/inventoryreport/" class="link-card">📊 Reports</a>
  </div>
</div>

<div class="footer-bar">
  POS Cloud • <a href="/admin/">Unfold Admin</a> •
  <a href="/apis/data/stats">Stats API</a> •
  v1.0
</div>

<script>
  // ── Fetch stats and hydrate KPI cards ──
  async function fetchStats() {
    try {
      var res = await fetch('/apis/data/stats');
      if (!res.ok) return;
      var d = await res.json();
      document.getElementById('kpi-products').textContent = d.total_products || 0;
      document.getElementById('kpi-sales').textContent = d.total_sales || 0;
      document.getElementById('kpi-inventory').textContent = d.total_inventory || 0;
      document.getElementById('kpi-branches').textContent = d.branches || 0;
      document.getElementById('kpi-orgs').textContent = d.organizations || 0;
      document.getElementById('kpi-syncs').textContent = d.total_sync_logs || 0;
    } catch(e) { console.error('Stats fetch failed:', e); }
  }

  // Initial stats fetch (live WS updates handled by bolt-sync-events.js)
  fetchStats();
  setInterval(fetchStats, 30000);
</script>
</body>
</html>"""


# ── BoltAPI catch-all bridge ────────────────────────────────────
# django_bolt's BoltAPI stores routes internally without exposing
# a standard Django urlpatterns.  This catch-all view bridges Django's
# URL dispatcher to BoltAPI's internal route matching.

async def _bolt_dispatch(request, route: str = ""):
    """Forward /apis/data/* requests to the BoltAPI instance's handlers.

    When *route* is empty (the root dashboard URL), serve the analytics
    dashboard HTML page.  Otherwise delegate to BoltAPI's internal handlers.
    """
    # ── Dashboard root ──
    if not route:
        return HttpResponse(DASHBOARD_HTML)

    from core.api import api

    full_path = f"/{route}" if route else "/"
    if not full_path.startswith("/"):
        full_path = f"/{full_path}"

    # BoltAPI routes are stored as (method, path, handler_id, handler) tuples.
    for method, rpath, _hid, handler in api._routes:
        # Strip the api.prefix to get the relative path for matching.
        rel = rpath[len(api.prefix):] if rpath.startswith(api.prefix) else rpath
        if rel == full_path or rel == full_path.rstrip("/"):
            if request.method.upper() != method.upper():
                return JsonResponse(
                    {"error": f"Method {request.method} not allowed"}, status=405
                )
            try:
                result = await handler()
            except Exception as exc:
                return JsonResponse({"error": str(exc)}, status=500)

            # msgspec structs use __slots__ — convert to builtins for JSON.
            if isinstance(result, list):
                data = [msgspec.to_builtins(r) for r in result]
            else:
                data = msgspec.to_builtins(result)
            return JsonResponse(data, safe=False)

    raise Http404(f"No BoltAPI route matches {full_path}")


# Wrap with csrf_exempt so POST/other methods work without CSRF tokens.
_bolt_catch_all = csrf_exempt(_bolt_dispatch)


urlpatterns = [
    path("health", _root_health, name="root_health"),
    # Unfold Admin
    path("admin/", admin.site.urls),

    # BoltAPI analytics dashboard — catch-all bridge to internal routing
    # All /apis/data/* requests are forwarded to the BoltAPI instance in core/api.py
    re_path(r"^apis/data/(?P<route>.*)$", _bolt_catch_all, name="bolt_catch_all"),

    # REST API (django-fusion viewsets + sync receivers)
    path("api/", include("core.urls")),
]
