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

SYNC_MONITOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>POS Cloud — Sync Monitor</title>
<style>
  :root {
    --bg-dark: #0f172a;
    --bg-card: #1e293b;
    --accent: #10b981;
    --accent-glow: rgba(16,185,129,0.15);
    --red: #ef4444;
    --orange: #f59e0b;
    --blue: #3b82f6;
    --purple: #8b5cf6;
    --text-main: #f8fafc;
    --text-muted: #94a3b8;
    --border: #334155;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg-dark);color:var(--text-main);font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh}
  .topbar{display:flex;justify-content:space-between;align-items:center;padding:1.25rem 2rem;background:var(--bg-card);border-bottom:1px solid var(--border)}
  .topbar-brand{display:flex;align-items:center;gap:.75rem}
  .topbar-brand h1{font-size:1.25rem;color:var(--accent);font-weight:700}
  .topbar-brand span{color:var(--text-muted);font-size:.85rem}
  .topbar-nav{display:flex;gap:.5rem}
  .nav-link{color:var(--text-muted);text-decoration:none;padding:.4rem .8rem;border-radius:6px;font-size:.85rem;transition:all .15s}
  .nav-link:hover{color:var(--text-main);background:var(--bg-dark)}
  .nav-link.active{color:var(--accent);background:rgba(16,185,129,0.1)}
  .main{padding:2rem;max-width:1400px;margin:0 auto}
  h2{font-size:1.1rem;margin-bottom:1rem;display:flex;align-items:center;gap:.5rem}
  .refresh-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem}
  .refresh-bar .status{display:flex;align-items:center;gap:.5rem;font-size:.85rem;color:var(--text-muted)}
  .refresh-bar .status .dot{width:8px;height:8px;border-radius:50%;display:inline-block}
  .dot.green{background:var(--accent)}
  .dot.yellow{background:var(--orange)}
  .dot.red{background:var(--red)}
  .dot.gray{background:#64748b}
  .btn{display:inline-flex;align-items:center;gap:.4rem;padding:.45rem .9rem;border-radius:8px;font-size:.8rem;font-weight:600;text-decoration:none;transition:all .15s;border:1px solid transparent;cursor:pointer}
  .btn-primary{background:var(--accent);color:#fff}
  .btn-primary:hover{background:#059669;box-shadow:0 0 12px var(--accent-glow)}
  .btn-sm{padding:.35rem .7rem;font-size:.75rem}
  .btn-ghost{color:var(--text-muted);border-color:var(--border)}
  .btn-ghost:hover{color:var(--text-main);border-color:var(--text-muted)}
  .btn-danger{color:#fff;background:var(--red)}
  .btn-danger:hover{background:#dc2626}
  .btn-warning{color:#fff;background:var(--orange)}
  .btn-warning:hover{background:#d97706}
  .grid-2{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
  .grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem}
  .grid-4{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}
  .card{background:var(--bg-card);border:1px solid var(--border);border-radius:12px;padding:1.25rem;margin-bottom:1.5rem}
  .card-title{font-size:.8rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:.05em;margin-bottom:.75rem}
  .stat{text-align:center;padding:1rem}
  .stat-value{font-size:1.8rem;font-weight:700}
  .stat-label{font-size:.75rem;color:var(--text-muted);margin-top:.25rem}
  .stat-value.green{color:var(--accent)}
  .stat-value.orange{color:var(--orange)}
  .stat-value.blue{color:var(--blue)}
  .stat-value.red{color:var(--red)}
  .stat-value.purple{color:var(--purple)}
  table{width:100%;border-collapse:collapse;font-size:.85rem}
  th{text-align:left;padding:.6rem .75rem;color:var(--text-muted);font-weight:600;border-bottom:1px solid var(--border);font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}
  td{padding:.6rem .75rem;border-bottom:1px solid rgba(51,65,85,0.4)}
  tr:hover td{background:rgba(255,255,255,0.02)}
  .badge{display:inline-flex;align-items:center;gap:.35rem;padding:.2rem .55rem;border-radius:999px;font-size:.72rem;font-weight:600}
  .badge-green{background:rgba(16,185,129,0.15);color:var(--accent)}
  .badge-red{background:rgba(239,68,68,0.15);color:var(--red)}
  .badge-yellow{background:rgba(245,158,11,0.15);color:var(--orange)}
  .badge-gray{background:rgba(148,163,184,0.15);color:var(--text-muted)}
  .badge-blue{background:rgba(59,130,246,0.15);color:var(--blue)}
  .badge-purple{background:rgba(139,92,246,0.15);color:var(--purple)}
  .empty{text-align:center;padding:2rem;color:var(--text-muted);font-size:.85rem}
  .conflict-entry{border-left:3px solid var(--orange);padding:.75rem 1rem;margin-bottom:.5rem;background:rgba(245,158,11,0.05);border-radius:0 8px 8px 0}
  .conflict-entry .fields{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:.5rem}
  .conflict-entry .field-tag{background:rgba(245,158,11,0.1);padding:.2rem .5rem;border-radius:4px;font-size:.72rem;color:var(--orange)}
  .conflict-actions{display:flex;gap:.4rem;margin-top:.5rem}
  .toast{position:fixed;bottom:20px;right:20px;padding:.75rem 1.25rem;border-radius:8px;font-size:.85rem;z-index:9999;animation:slideIn .25s ease;box-shadow:0 4px 16px rgba(0,0,0,0.3)}
  .toast.success{background:rgba(16,185,129,0.9);color:#fff}
  .toast.error{background:rgba(239,68,68,0.9);color:#fff}
  @keyframes slideIn{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  .tab-bar{display:flex;gap:.25rem;margin-bottom:1.5rem;background:var(--bg-card);border:1px solid var(--border);border-radius:10px;padding:.25rem}
  .tab{flex:1;padding:.5rem 1rem;text-align:center;border-radius:8px;font-size:.82rem;font-weight:500;cursor:pointer;transition:all .15s;color:var(--text-muted);border:none;background:transparent}
  .tab:hover{color:var(--text-main);background:rgba(255,255,255,0.05)}
  .tab.active{background:rgba(16,185,129,0.15);color:var(--accent)}
  .tab-content{display:none}
  .tab-content.active{display:block}
  .loading-spinner{display:flex;align-items:center;justify-content:center;padding:3rem;color:var(--text-muted)}
  .loading-spinner::after{content:'';width:24px;height:24px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite;margin-left:.5rem}
  @keyframes spin{to{transform:rotate(360deg)}}
  .conflict-resolve-form{display:flex;gap:.5rem;align-items:center;margin-top:.5rem}
  .conflict-resolve-form select{background:var(--bg-dark);color:var(--text-main);border:1px solid var(--border);border-radius:6px;padding:.35rem .5rem;font-size:.78rem}
</style>
</head>
<body>
<div class="topbar">
  <div class="topbar-brand">
    <div>
      <h1>📡 Sync Monitor</h1>
      <span>Branch health, queue status &amp; conflict resolution</span>
    </div>
  </div>
  <div class="topbar-nav">
    <a href="/apis/data/" class="nav-link">📊 Analytics</a>
    <a href="/apis/data/sync-monitor" class="nav-link active">📡 Sync Monitor</a>
    <a href="/admin/" class="nav-link">⚙ Admin</a>
  </div>
</div>

<div class="main">
  <!-- Tab bar -->
  <div class="tab-bar">
    <button class="tab active" data-tab="overview">📊 Overview</button>
    <button class="tab" data-tab="branches">🏪 Branches</button>
    <button class="tab" data-tab="queue">📋 Queue</button>
    <button class="tab" data-tab="conflicts">⚡ Conflicts</button>
    <button class="tab" data-tab="activity">📜 Activity</button>
  </div>

  <!-- Refresh bar -->
  <div class="refresh-bar">
    <div class="status">
      <span class="dot gray" id="ws-dot"></span>
      <span id="ws-status">Connecting…</span>
      <span style="margin-left:1rem;font-size:.78rem;color:var(--text-muted)" id="last-refresh">Just now</span>
    </div>
    <button class="btn btn-primary btn-sm" onclick="refreshAll()">⟳ Refresh</button>
  </div>

  <!-- ═══ TAB: Overview ═══ -->
  <div class="tab-content active" id="tab-overview">
    <div class="grid-4" id="overview-stats">
      <div class="card"><div class="stat"><div class="stat-value green" id="ov-branches-online">—</div><div class="stat-label">Branches Online</div></div></div>
      <div class="card"><div class="stat"><div class="stat-value orange" id="ov-queue-pending">—</div><div class="stat-label">Queue Pending</div></div></div>
      <div class="card"><div class="stat"><div class="stat-value red" id="ov-queue-failed">—</div><div class="stat-label">Queue Failed</div></div></div>
      <div class="card"><div class="stat"><div class="stat-value purple" id="ov-conflicts">—</div><div class="stat-label">Conflicts</div></div></div>
    </div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">🏪 Branch Status</div>
        <div id="branch-summary-table"><div class="empty">Loading…</div></div>
      </div>
      <div class="card">
        <div class="card-title">⚡ Pending Conflicts</div>
        <div id="conflicts-preview"><div class="empty">Loading…</div></div>
      </div>
    </div>
  </div>

  <!-- ═══ TAB: Branches ═══ -->
  <div class="tab-content" id="tab-branches">
    <div class="card">
      <div class="card-title">All Branches — Health &amp; Sync Status</div>
      <div id="branches-table"><div class="loading-spinner">Loading branches…</div></div>
    </div>
  </div>

  <!-- ═══ TAB: Queue ═══ -->
  <div class="tab-content" id="tab-queue">
    <div class="card">
      <div class="card-title">Queue Items by Branch</div>
      <div id="queue-table"><div class="loading-spinner">Loading queue…</div></div>
    </div>
    <div class="card">
      <div class="card-title">Pending Queue Items</div>
      <div id="queue-pending-list"><div class="loading-spinner">Loading…</div></div>
    </div>
  </div>

  <!-- ═══ TAB: Conflicts ═══ -->
  <div class="tab-content" id="tab-conflicts">
    <div class="card">
      <div class="card-title">Pending Conflicts Requiring Resolution</div>
      <div id="conflicts-list"><div class="loading-spinner">Loading conflicts…</div></div>
    </div>
  </div>

  <!-- ═══ TAB: Activity ═══ -->
  <div class="tab-content" id="tab-activity">
    <div class="card">
      <div class="card-title">Recent Sync Activity</div>
      <div id="activity-list"><div class="loading-spinner">Loading activity…</div></div>
    </div>
  </div>
</div>

<script>
// ── Tab switching ──
document.querySelectorAll('.tab').forEach(function(tab) {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.tab').forEach(function(t){t.classList.remove('active')});
    document.querySelectorAll('.tab-content').forEach(function(t){t.classList.remove('active')});
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    refreshAll();
  });
});

// ── Data fetching ──
async function fetchJSON(url) {
  var res = await fetch(url);
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}

function formatTime(iso) {
  if (!iso) return '—';
  var d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  var now = new Date();
  var diff = (now - d) / 1000;
  if (diff < 60) return Math.round(diff) + 's ago';
  if (diff < 3600) return Math.round(diff / 60) + 'm ago';
  return d.toLocaleString();
}

function esc(str) {
  var d = document.createElement('div');
  d.appendChild(document.createTextNode(str || ''));
  return d.innerHTML;
}

function showToast(msg, type) {
  var t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(function(){ t.remove(); }, 3000);
}

// ── Refresh all tabs ──
var refreshInterval = null;

async function refreshAll() {
  document.getElementById('last-refresh').textContent = 'Refreshing…';
  await Promise.all([
    refreshOverview(),
    refreshBranches(),
    refreshQueue(),
    refreshConflicts(),
    refreshActivity(),
  ]);
  document.getElementById('last-refresh').textContent = 'Updated ' + new Date().toLocaleTimeString();
}

// Auto-refresh every 15 seconds
refreshInterval = setInterval(refreshAll, 15000);

// ── Overview Tab ──
async function refreshOverview() {
  try {
    var [health, queue, byBranch, conflicts] = await Promise.all([
      fetchJSON('/api/dashboard/branches/health'),
      fetchJSON('/api/dashboard/queue/summary'),
      fetchJSON('/api/dashboard/queue/by-branch'),
      fetchJSON('/api/dashboard/conflicts'),
    ]);

    var online = health.branches.filter(function(b){ return b.online; }).length;
    document.getElementById('ov-branches-online').textContent = online + '/' + health.branches.length;
    document.getElementById('ov-queue-pending').textContent = queue.pending;
    document.getElementById('ov-queue-failed').textContent = queue.failed;
    document.getElementById('ov-conflicts').textContent = conflicts.count;

    // Branch summary table
    var html = '<table><thead><tr><th>Branch</th><th>Status</th><th>Terminals</th><th>Pending</th><th>Failed</th></tr></thead><tbody>';
    health.branches.forEach(function(b) {
      var bq = (byBranch.branches || []).find(function(x){ return x.code === b.code; }) || {};
      var statusClass = b.online ? 'badge-green' : 'badge-gray';
      var statusLabel = b.online ? '🟢 Online' : '⚫ Offline';
      html += '<tr><td><strong>' + esc(b.name) + '</strong><br><span style="font-size:.75rem;color:var(--text-muted)">' + esc(b.code) + '</span></td>' +
        '<td><span class="badge ' + statusClass + '">' + statusLabel + '</span></td>' +
        '<td>' + b.connected_terminals + '</td>' +
        '<td>' + (bq.pending || 0) + '</td>' +
        '<td>' + (bq.failed || 0) + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('branch-summary-table').innerHTML = html;

    // Conflicts preview
    var c = conflicts.conflicts || [];
    if (c.length === 0) {
      document.getElementById('conflicts-preview').innerHTML = '<div class="empty">✅ No pending conflicts</div>';
    } else {
      html = '<table><thead><tr><th>Entity</th><th>Reason</th><th>When</th></tr></thead><tbody>';
      c.slice(0, 5).forEach(function(cf) {
        var fields = (cf.conflict_fields || []).map(function(f){ return f.field; }).join(', ');
        html += '<tr><td>' + esc(cf.entity_type) + ' #' + esc(cf.entity_id) + '</td>' +
          '<td style="font-size:.78rem;color:var(--text-muted)">' + esc(cf.reason) + '<br><span style="color:var(--orange)">' + esc(fields) + '</span></td>' +
          '<td style="font-size:.78rem;color:var(--text-muted)">' + formatTime(cf.created_at) + '</td></tr>';
      });
      if (c.length > 5) html += '<tr><td colspan="3" style="text-align:center;color:var(--text-muted);font-size:.78rem">+' + (c.length - 5) + ' more…</td></tr></tbody></table>';
      html += '</tbody></table>';
      document.getElementById('conflicts-preview').innerHTML = html;
    }
  } catch(e) { console.error('Overview refresh failed:', e); }
}

// ── Branches Tab ──
async function refreshBranches() {
  try {
    var health = await fetchJSON('/api/dashboard/branches/health');
    var html = '<table><thead><tr><th>Branch</th><th>Code</th><th>Type</th><th>Status</th><th>Terminals</th><th>Node ID</th></tr></thead><tbody>';
    health.branches.forEach(function(b) {
      var st = b.online ? '<span class="badge badge-green">🟢 Online</span>' : '<span class="badge badge-gray">⚫ Offline</span>';
      html += '<tr><td><strong>' + esc(b.name) + '</strong></td><td style="color:var(--text-muted)">' + esc(b.code) + '</td>' +
        '<td><span class="badge badge-blue">' + esc(b.pos_type) + '</span></td>' +
        '<td>' + st + '</td><td>' + b.connected_terminals + '</td>' +
        '<td style="font-size:.78rem;color:var(--text-muted)">' + esc(b.node_id || '—') + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('branches-table').innerHTML = html;
  } catch(e) { console.error('Branches refresh failed:', e); }
}

// ── Queue Tab ──
async function refreshQueue() {
  try {
    var [byBranch, pending] = await Promise.all([
      fetchJSON('/api/dashboard/queue/by-branch'),
      fetchJSON('/api/dashboard/queue/list/pending'),
    ]);
    var html = '<table><thead><tr><th>Branch</th><th>Code</th><th>Pending</th><th>Failed</th></tr></thead><tbody>';
    (byBranch.branches || []).forEach(function(b) {
      html += '<tr><td><strong>' + esc(b.branch) + '</strong></td><td style="color:var(--text-muted)">' + esc(b.code) + '</td>' +
        '<td>' + (b.pending > 0 ? '<span class="badge badge-yellow">' + b.pending + '</span>' : '<span style="color:var(--text-muted)">0</span>') + '</td>' +
        '<td>' + (b.failed > 0 ? '<span class="badge badge-red">' + b.failed + '</span>' : '<span style="color:var(--text-muted)">0</span>') + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('queue-table').innerHTML = html;

    // Pending items list
    var items = pending.items || [];
    if (items.length === 0) {
      document.getElementById('queue-pending-list').innerHTML = '<div class="empty">✅ No pending queue items</div>';
    } else {
      html = '<table><thead><tr><th>ID</th><th>Branch</th><th>Operation</th><th>Entity</th><th>Attempts</th><th>Next Retry</th></tr></thead><tbody>';
      items.forEach(function(item) {
        html += '<tr><td>' + item.id + '</td><td>' + esc(item.branch) + '</td>' +
          '<td><span class="badge badge-blue">' + esc(item.operation) + '</span></td>' +
          '<td>' + esc(item.entity_type) + '</td>' +
          '<td>' + item.attempt_count + '/' + item.max_attempts + '</td>' +
          '<td style="font-size:.78rem;color:var(--text-muted)">' + formatTime(item.next_retry_at) + '</td></tr>';
      });
      html += '</tbody></table>';
      document.getElementById('queue-pending-list').innerHTML = html;
    }
  } catch(e) { console.error('Queue refresh failed:', e); }
}

// ── Conflicts Tab ──
async function refreshConflicts() {
  try {
    var data = await fetchJSON('/api/dashboard/conflicts');
    var list = data.conflicts || [];
    if (list.length === 0) {
      document.getElementById('conflicts-list').innerHTML = '<div class="empty">✅ No pending conflicts. All sync data is in agreement.</div>';
      return;
    }
    var html = '';
    list.forEach(function(c) {
      var fields = (c.conflict_fields || []).map(function(f) {
        return '<span class="field-tag">' + esc(f.field) + ': local=' + esc(JSON.stringify(f.local_value)) + ' vs remote=' + esc(JSON.stringify(f.remote_value)) + '</span>';
      }).join('');
      html += '<div class="conflict-entry">' +
        '<div style="display:flex;justify-content:space-between;align-items:flex-start">' +
          '<div><strong>' + esc(c.entity_type) + ' #' + esc(c.entity_id) + '</strong> <span class="badge badge-yellow">' + esc(c.resolver_used) + '</span></div>' +
          '<span style="font-size:.75rem;color:var(--text-muted)">' + formatTime(c.created_at) + '</span>' +
        '</div>' +
        '<div style="font-size:.78rem;color:var(--text-muted);margin-top:.25rem">' + esc(c.reason) + '</div>' +
        '<div style="font-size:.78rem;color:var(--text-muted)">Branch: ' + esc(c.branch) + ' · Node: ' + esc(c.node_id) + '</div>' +
        (fields ? '<div class="fields">' + fields + '</div>' : '') +
        '<div class="conflict-actions">' +
          '<select class="conflict-resolve-select" id="resolve-select-' + c.id + '">' +
            '<option value="use_local">Keep Local (cloud)</option>' +
            '<option value="use_remote">Accept Remote (branch)</option>' +
            '<option value="merge">Merge</option>' +
          '</select>' +
          '<button class="btn btn-primary btn-sm" onclick="resolveConflict(' + c.id + ')">✓ Resolve</button>' +
          '<button class="btn btn-sm btn-ghost" onclick="dismissConflict(' + c.id + ')">✕ Dismiss</button>' +
        '</div>' +
      '</div>';
    });
    document.getElementById('conflicts-list').innerHTML = html;
  } catch(e) { console.error('Conflicts refresh failed:', e); }
}

async function resolveConflict(id) {
  var select = document.getElementById('resolve-select-' + id);
  if (!select) return;
  var resolution = select.value;
  try {
    var res = await fetch('/api/dashboard/conflicts/' + id + '/resolve', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ resolution: resolution, notes: 'Resolved via Sync Monitor dashboard' }),
    });
    var data = await res.json();
    if (res.ok) {
      showToast('Conflict #' + id + ' resolved as ' + resolution, 'success');
      refreshConflicts();
    } else {
      showToast('Failed: ' + (data.error || 'unknown'), 'error');
    }
  } catch(e) {
    showToast('Error resolving conflict: ' + e.message, 'error');
  }
}

async function dismissConflict(id) {
  try {
    var res = await fetch('/api/dashboard/conflicts/' + id + '/dismiss', { method: 'POST' });
    if (res.ok) {
      showToast('Conflict #' + id + ' dismissed', 'success');
      refreshConflicts();
    } else {
      showToast('Failed to dismiss', 'error');
    }
  } catch(e) {
    showToast('Error: ' + e.message, 'error');
  }
}

// ── Activity Tab ──
async function refreshActivity() {
  try {
    var data = await fetchJSON('/api/dashboard/activity?limit=50');
    var entries = data.entries || [];
    if (entries.length === 0) {
      document.getElementById('activity-list').innerHTML = '<div class="empty">No sync activity yet</div>';
      return;
    }
    var html = '<table><thead><tr><th>Time</th><th>Branch</th><th>Type</th><th>Count</th><th>Status</th></tr></thead><tbody>';
    entries.forEach(function(e) {
      var statusBadge = e.status === 'processed' || e.status === 'received' ? 'badge-green' :
        e.status === 'failed' ? 'badge-red' : 'badge-gray';
      var typeIcons = { products: '📦', sales: '🛒', inventory: '📋', heartbeat: '💓' };
      var icon = typeIcons[e.entity_type] || '📌';
      html += '<tr><td style="font-size:.78rem;color:var(--text-muted)">' + formatTime(e.received_at) + '</td>' +
        '<td>' + esc(e.branch) + '</td>' +
        '<td>' + icon + ' ' + esc(e.entity_type) + '</td>' +
        '<td>' + e.entity_count + '</td>' +
        '<td><span class="badge ' + statusBadge + '">' + esc(e.status) + '</span></td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('activity-list').innerHTML = html;
  } catch(e) { console.error('Activity refresh failed:', e); }
}

// ── WebSocket status indicator ──
(function() {
  var ws = null;
  function connect() {
    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    var url = proto + '//' + location.host + '/ws/sync-events/';
    ws = new WebSocket(url);
    ws.onopen = function() {
      document.getElementById('ws-dot').className = 'dot green';
      document.getElementById('ws-status').textContent = '🟢 Connected';
    };
    ws.onclose = function() {
      document.getElementById('ws-dot').className = 'dot yellow';
      document.getElementById('ws-status').textContent = '🟡 Disconnected';
      setTimeout(connect, 3000);
    };
    ws.onerror = function() {
      document.getElementById('ws-dot').className = 'dot red';
      document.getElementById('ws-status').textContent = '🔴 Error';
    };
  }
  connect();
})();

// ── Initial load ──
refreshAll();
</script>
</body>
</html>
"""


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

    # ── Sync Monitor ──
    if route == "sync-monitor":
        return HttpResponse(SYNC_MONITOR_HTML)

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
