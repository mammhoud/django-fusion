"""Formint Cloud — URL configuration with Unfold admin, django-fusion, REST API."""

import msgspec

from django.contrib import admin
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt

from django_fusion.designer import urls as fusion_designer_urls

_root_health = lambda r: JsonResponse({"status": "healthy", "service": "formint-cloud"})

from apps.handlers.surface import stats as apps_handlers_surface_stats
from apps.handlers.surface import monitor_status as apps_handlers_surface_monitor_status
from apps.handlers.surface import urlpatterns as apps_handlers_surface_urlpatterns


# ── BoltAPI Analytics Dashboard ─────────────────────────────────
# Served at /apis/data/ as the root bolt dashboard page.
# The middleware injects bolt-sync-events.js for live WebSocket updates.

SYNC_MONITOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SYNC MONITOR — FORMINT CLOUD</title>
<style>
  /* ═══════════════════════════════════════════════════════════════
     FORMINT CLOUD // SYNC MONITOR
     Tactical Telemetry — industrial brutalist / CRT terminal build.
     Substrate: deactivated CRT. Phosphor: white. Hazard: red.
     Zero border-radius. Rigid blueprint grid. ASCII framing.
     ═══════════════════════════════════════════════════════════════ */
  :root {
    --bg: #0A0A0A;
    --bg-panel: #121212;
    --bg-inset: #0D0D0D;
    --ink: #EAEAEA;
    --ink-dim: #8A8A8A;
    --ink-faint: #555555;
    --hazard: #E61919;
    --phosphor: #4AF626;
    --line: #2A2A2A;
    --line-strong: #444444;
    --mono: "JetBrains Mono", "IBM Plex Mono", "Space Mono", ui-monospace, "Courier New", monospace;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { background: var(--bg); }
  body {
    background: var(--bg);
    color: var(--ink);
    font-family: var(--mono);
    font-size: 13px;
    line-height: 1.45;
    -webkit-font-smoothing: antialiased;
  }
  /* CRT scanlines — hardware limitation, not decoration */
  body::after {
    content: "";
    position: fixed; inset: 0;
    pointer-events: none;
    z-index: 60;
    background: repeating-linear-gradient(
      0deg,
      transparent, transparent 2px,
      rgba(0, 0, 0, 0.22) 2px, rgba(0, 0, 0, 0.22) 4px
    );
  }
  /* Mechanical grain */
  body::before {
    content: "";
    position: fixed; inset: 0;
    pointer-events: none;
    z-index: 61;
    opacity: 0.05;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)'/%3E%3C/svg%3E");
  }
  a { color: var(--ink); text-decoration: none; }
  a:hover { color: var(--hazard); }
  .mono { font-family: var(--mono); }

  /* ── Blueprint frame ──────────────────────────────────────────── */
  .frame {
    max-width: 1440px;
    margin: 0 auto;
    padding: 0 16px 48px;
  }
  .topbar {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    border-bottom: 2px solid var(--line-strong);
    padding: 14px 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 11px;
    color: var(--ink-dim);
  }
  .topbar-brand { font-size: 15px; font-weight: 700; color: var(--ink); letter-spacing: 0.02em; }
  .topbar-brand .hazard { color: var(--hazard); }
  .topbar-nav { display: flex; gap: 18px; justify-content: flex-end; }
  .topbar-nav .active { color: var(--ink); }
  .topbar-nav .active::before { content: ">> "; color: var(--hazard); }

  /* ── Masthead — macro type ────────────────────────────────────── */
  .masthead {
    padding: 28px 0 20px;
    border-bottom: 1px solid var(--line);
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 24px;
    align-items: end;
  }
  .masthead h1 {
    font-size: clamp(2.2rem, 6vw, 5rem);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: -0.03em;
    line-height: 0.9;
    margin: 0;
  }
  .masthead h1 .block { display: block; }
  .masthead h1 .red { color: var(--hazard); }
  .masthead h1 .thin { font-weight: 400; color: var(--ink-dim); }
  .masthead-meta {
    text-align: right;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--ink-dim);
    line-height: 1.9;
    border: 1px solid var(--line-strong);
    padding: 10px 14px;
  }
  .masthead-meta b { color: var(--ink); font-weight: 600; }

  /* ── Status strip ─────────────────────────────────────────────── */
  .status-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line-strong);
    margin: 20px 0;
  }
  .status-cell {
    background: var(--bg-panel);
    padding: 12px 14px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--ink-dim);
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .status-cell .val {
    font-size: clamp(1.4rem, 3vw, 2.2rem);
    font-weight: 700;
    color: var(--ink);
    letter-spacing: 0;
    line-height: 1;
  }
  .status-cell .val.red { color: var(--hazard); }
  .status-cell .val.green { color: var(--phosphor); }
  .led { width: 8px; height: 8px; display: inline-block; background: var(--ink-faint); }
  .led.on { background: var(--phosphor); }
  .led.warn { background: var(--hazard); }

  /* ── Tab rail ─────────────────────────────────────────────────── */
  .tab-bar {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1px;
    background: var(--line);
    border: 1px solid var(--line-strong);
    margin-bottom: 20px;
  }
  .tab {
    background: var(--bg-panel);
    color: var(--ink-dim);
    border: 0;
    padding: 11px 8px;
    font-family: var(--mono);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    cursor: pointer;
    transition: background 120ms, color 120ms;
  }
  .tab:hover { color: var(--ink); background: var(--bg-inset); }
  .tab.active { color: var(--ink); background: var(--bg-inset); box-shadow: inset 0 -2px 0 var(--hazard); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  /* ── Telemetry grid ───────────────────────────────────────────── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--line); border: 1px solid var(--line-strong); margin-bottom: 20px; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1px; background: var(--line); border: 1px solid var(--line-strong); margin-bottom: 20px; }
  .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--line); border: 1px solid var(--line-strong); margin-bottom: 20px; }
  .panel { background: var(--bg-panel); padding: 16px; min-width: 0; }
  .panel-title {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--ink-dim);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--line);
  }
  .panel-title::before { content: "[ "; color: var(--hazard); }
  .panel-title::after { content: " ]"; color: var(--hazard); }

  /* ── Tables ───────────────────────────────────────────────────── */
  table { width: 100%; border-collapse: collapse; font-size: 12px; }
  th {
    text-align: left;
    padding: 7px 8px;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--ink-dim);
    border-bottom: 1px solid var(--line-strong);
    font-weight: 600;
    white-space: nowrap;
  }
  td { padding: 7px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
  tr:last-child td { border-bottom: 0; }
  tr:hover td { background: var(--bg-inset); }
  td .code { color: var(--ink-dim); font-size: 11px; }

  .badge {
    display: inline-block;
    padding: 2px 7px;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid var(--line-strong);
    color: var(--ink-dim);
  }
  .badge.green { border-color: var(--phosphor); color: var(--phosphor); }
  .badge.red { border-color: var(--hazard); color: var(--hazard); }
  .badge.yellow { border-color: #F5A623; color: #F5A623; }
  .badge.blue { border-color: #3B82F6; color: #3B82F6; }

  /* ── Conflict entries ─────────────────────────────────────────── */
  .conflict-entry {
    border-left: 3px solid var(--hazard);
    padding: 12px 14px;
    margin-bottom: 10px;
    background: var(--bg-inset);
  }
  .conflict-entry .row { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  .conflict-entry .fields { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }
  .field-tag {
    border: 1px solid var(--line-strong);
    padding: 3px 7px;
    font-size: 10px;
    color: var(--ink-dim);
    letter-spacing: 0.04em;
  }
  .field-tag .local { color: var(--ink); }
  .field-tag .remote { color: var(--hazard); }
  .conflict-actions { display: flex; gap: 8px; margin-top: 10px; align-items: center; }
  select {
    background: var(--bg);
    color: var(--ink);
    border: 1px solid var(--line-strong);
    font-family: var(--mono);
    font-size: 11px;
    padding: 5px 8px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  select:focus { outline: 1px solid var(--hazard); }

  /* ── Buttons — mechanical, no radius ──────────────────────────── */
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-panel);
    color: var(--ink);
    border: 1px solid var(--line-strong);
    font-family: var(--mono);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 7px 14px;
    cursor: pointer;
    transition: background 120ms, color 120ms, border-color 120ms;
  }
  .btn:hover { border-color: var(--ink); }
  .btn:active { transform: translateY(1px); background: var(--bg-inset); }
  .btn.primary { border-color: var(--hazard); color: var(--hazard); }
  .btn.primary:hover { background: var(--hazard); color: var(--bg); }
  .btn.ghost { color: var(--ink-dim); }
  .btn.ghost:hover { color: var(--ink); }

  .empty {
    text-align: center;
    padding: 28px 12px;
    color: var(--ink-faint);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    border: 1px dashed var(--line-strong);
  }
  .empty::before { content: "/// "; color: var(--hazard); }
  .empty::after { content: " ///"; color: var(--hazard); }

  .loading {
    padding: 28px;
    text-align: center;
    color: var(--ink-dim);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.16em;
  }
  .loading::after {
    content: "";
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-left: 8px;
    background: var(--hazard);
    animation: blink 1s steps(2) infinite;
  }
  @keyframes blink { 50% { opacity: 0; } }

  .refresh-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0 0 20px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--ink-dim);
  }
  .refresh-bar .status { display: flex; align-items: center; gap: 10px; }

  .footer-bar {
    margin-top: 32px;
    padding: 14px 0;
    border-top: 1px solid var(--line);
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: var(--ink-faint);
  }
  .footer-bar .hazard { color: var(--hazard); }

  .toast {
    position: fixed;
    bottom: 20px; right: 20px;
    padding: 10px 16px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    background: var(--bg-panel);
    border: 1px solid var(--hazard);
    color: var(--ink);
    z-index: 70;
  }

  /* ── WS link-lost banner ─────────────────────────────────────── */
  .ws-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    background: var(--hazard);
    color: var(--bg);
    padding: 12px 16px;
    margin: 16px 0;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }
  .ws-banner .title { font-weight: 700; }
  .ws-banner .sub { opacity: 0.85; display: block; margin-top: 2px; }
  .ws-banner .btn { background: var(--bg); color: var(--hazard); border: 1px solid var(--bg); }
  .ws-banner .btn:hover { background: var(--bg-inset); }
  .stream-lost { color: var(--hazard); }
  .stream-live { color: var(--phosphor); }

  /* ── Crosshair at grid intersections ──────────────────────────── */
  .crosshair { color: var(--ink-faint); font-size: 9px; line-height: 1; user-select: none; }

  @media (max-width: 900px) {
    .topbar { grid-template-columns: 1fr; gap: 10px; }
    .topbar-nav { justify-content: flex-start; }
    .masthead { grid-template-columns: 1fr; }
    .masthead-meta { text-align: left; }
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
    .status-strip { grid-template-columns: 1fr 1fr; }
    .tab-bar { grid-template-columns: 1fr 1fr; }
  }
  @media (max-width: 560px) {
    .status-strip { grid-template-columns: 1fr; }
    .tab-bar { grid-template-columns: 1fr 1fr 1fr; }
    .frame { padding: 0 10px 32px; }
  }
</style>
</head>
<body>
<div class="frame">

  <!-- ── Top bar ─────────────────────────────────────────────────── -->
  <div class="topbar">
    <div class="topbar-brand">FORMINT CLOUD <span class="hazard">/</span> SYNC MONITOR</div>
    <div class="crosshair">+ + +</div>
    <div class="topbar-nav">
      <a href="/apis/data/">ANALYTICS</a>
      <a href="/apis/data/sync-monitor" class="active">SYNC MONITOR</a>
      <a href="/admin/">ADMIN</a>
    </div>
  </div>

  <!-- ── Masthead ────────────────────────────────────────────────── -->
  <div class="masthead">
    <div>
      <h1>
        <span class="block">SYNC <span class="red">MONITOR</span></span>
        <span class="block thin">BRANCH // QUEUE // CONFLICT</span>
      </h1>
    </div>
    <div class="masthead-meta">
      UNIT / <b>FMT-CLOUD-01</b><br>
      REV / <b>2.6</b> &nbsp; MODE / <b>TELEMETRY</b><br>
      <span id="last-refresh">T-0.000</span>
    </div>
  </div>

  <!-- ── WS link-lost banner (hidden while the stream is live) ── -->
  <div class="ws-banner" id="ws-banner" role="alert" style="display:none">
    <div>
      <span class="title">&gt;&gt;&gt; LINK LOST / WS DISCONNECTED</span>
      <span class="sub">AUTO-RETRY IN <span id="ws-retry-in">05S</span> &nbsp;·&nbsp; DATA SHOWN IS STALE</span>
    </div>
    <button class="btn" id="ws-retry-btn" type="button">RETRY LINK</button>
  </div>

  <!-- ── Status strip ────────────────────────────────────────────── -->
  <div class="status-strip">
    <div class="status-cell">
      <span class="led" id="ws-led"></span>
      <div>
        <div>LINK / WS</div>
        <div class="val" id="ws-status">STANDBY</div>
      </div>
    </div>
    <div class="status-cell">
      <div>
        <div>BRANCHES ONLINE</div>
        <div class="val" id="ov-branches-online">—</div>
      </div>
    </div>
    <div class="status-cell">
      <div>
        <div>QUEUE PENDING</div>
        <div class="val" id="ov-queue-pending">—</div>
      </div>
    </div>
    <div class="status-cell">
      <div>
        <div>CONFLICTS</div>
        <div class="val red" id="ov-conflicts">—</div>
      </div>
    </div>
  </div>

  <!-- ── Tab rail ────────────────────────────────────────────────── -->
  <div class="tab-bar">
    <button class="tab active" data-tab="overview">OVERVIEW</button>
    <button class="tab" data-tab="branches">BRANCHES</button>
    <button class="tab" data-tab="queue">QUEUE</button>
    <button class="tab" data-tab="conflicts">CONFLICTS</button>
    <button class="tab" data-tab="activity">ACTIVITY</button>
  </div>

  <div class="refresh-bar">
    <div class="status">
      <span class="crosshair">+</span>
      <span>LAST POLL // <span id="last-poll">—</span></span>
      <span>LAST PUSH // <span id="last-push">—</span></span>
      <span id="stream-state">STREAM // STANDBY</span>
    </div>
    <button class="btn" id="force-poll" type="button">⟳ FORCE POLL</button>
  </div>

  <!-- ═══ TAB: OVERVIEW ═══ -->
  <div class="tab-content active" id="tab-overview">
    <div class="grid-2">
      <div class="panel">
        <div class="panel-title">BRANCH STATUS</div>
        <div id="branch-summary-table"><div class="loading">POLLING…</div></div>
      </div>
      <div class="panel">
        <div class="panel-title">PENDING CONFLICTS</div>
        <div id="conflicts-preview"><div class="loading">POLLING…</div></div>
      </div>
    </div>
    <div class="grid-3">
      <div class="panel">
        <div class="panel-title">QUEUE PENDING</div>
        <div class="val" style="font-size:clamp(2rem,5vw,3.4rem);font-weight:700" id="ov-queue-pending-lg">—</div>
        <div style="margin-top:6px;font-size:11px;color:var(--ink-dim)">EST BACKLOG // <b style="color:var(--ink)" id="ov-backlog">—</b>s</div>
      </div>
      <div class="panel">
        <div class="panel-title">QUEUE FAILED</div>
        <div class="val" style="font-size:clamp(2rem,5vw,3.4rem);font-weight:700;color:var(--hazard)" id="ov-queue-failed">—</div>
        <div style="margin-top:6px;font-size:11px;color:var(--ink-dim)">RETRY WINDOW // EXP-BACKOFF</div>
      </div>
      <div class="panel">
        <div class="panel-title">CONFLICT MATRIX</div>
        <div class="val" style="font-size:clamp(2rem,5vw,3.4rem);font-weight:700" id="ov-conflicts-lg">—</div>
        <div style="margin-top:6px;font-size:11px;color:var(--ink-dim)">PENDING // <b style="color:var(--ink)" id="ov-conflict-pending">—</b></div>
      </div>
    </div>
  </div>

  <!-- ═══ TAB: BRANCHES ═══ -->
  <div class="tab-content" id="tab-branches">
    <div class="panel">
      <div class="panel-title">ALL BRANCHES — HEALTH &amp; SYNC STATUS</div>
      <div id="branches-table"><div class="loading">POLLING…</div></div>
    </div>
  </div>

  <!-- ═══ TAB: QUEUE ═══ -->
  <div class="tab-content" id="tab-queue">
    <div class="panel" style="margin-bottom:20px">
      <div class="panel-title">QUEUE ITEMS BY BRANCH</div>
      <div id="queue-table"><div class="loading">POLLING…</div></div>
    </div>
    <div class="panel">
      <div class="panel-title">PENDING QUEUE ITEMS</div>
      <div id="queue-pending-list"><div class="loading">POLLING…</div></div>
    </div>
  </div>

  <!-- ═══ TAB: CONFLICTS ═══ -->
  <div class="tab-content" id="tab-conflicts">
    <div class="panel">
      <div class="panel-title">PENDING CONFLICTS — RESOLUTION REQUIRED</div>
      <div id="conflicts-list"><div class="loading">POLLING…</div></div>
    </div>
  </div>

  <!-- ═══ TAB: ACTIVITY ═══ -->
  <div class="tab-content" id="tab-activity">
    <div class="panel" style="margin-bottom:20px">
      <div class="panel-title">LIVE FEED // WS STREAM</div>
      <div id="live-feed"><div class="empty">AWAITING STREAM EVENTS…</div></div>
    </div>
    <div class="panel">
      <div class="panel-title">RECENT SYNC ACTIVITY</div>
      <div id="activity-list"><div class="loading">POLLING…</div></div>
    </div>
  </div>

  <div class="footer-bar">
    <div>FORMINT CLOUD <span class="hazard">//</span> TELEMETRY CONSOLE</div>
    <div>© 2026 STRUCTA CLOUD &nbsp;|&nbsp; REV 2.6 &nbsp;|&nbsp; <a href="/admin/">ADMIN</a></div>
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

// ── Fetch ──
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
  if (diff < 60) return Math.round(diff) + 's AGO';
  if (diff < 3600) return Math.round(diff / 60) + 'm AGO';
  return d.toLocaleString();
}

function esc(str) {
  var d = document.createElement('div');
  d.appendChild(document.createTextNode(str == null ? '' : String(str)));
  return d.innerHTML;
}

function showToast(msg, type) {
  var t = document.createElement('div');
  t.className = 'toast';
  t.setAttribute('aria-live', 'polite');
  t.textContent = (type === 'ok' ? '[ OK ] ' : '[ ERR ] ') + msg;
  document.body.appendChild(t);
  setTimeout(function(){ t.remove(); }, 3000);
}

// ── Poll ──
async function refreshAll() {
  var now = new Date();
  document.getElementById('last-poll').textContent = now.toLocaleTimeString();
  document.getElementById('last-refresh').textContent = 'T+ ' + now.toLocaleTimeString();
  await Promise.all([
    refreshOverview(),
    refreshBranches(),
    refreshQueue(),
    refreshConflicts(),
    refreshActivity(),
  ]);
}
// No interval polling — the WS stream drives refreshes (scheduleRefresh on
// each frame, throttled to 2s). A 10s fallback poll runs only while LOST.

// ── Overview ──
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
    document.getElementById('ov-queue-pending-lg').textContent = queue.pending;
    document.getElementById('ov-queue-failed').textContent = queue.failed;
    document.getElementById('ov-backlog').textContent = queue.estimated_backlog_seconds;
    document.getElementById('ov-conflicts').textContent = conflicts.count;
    document.getElementById('ov-conflicts-lg').textContent = conflicts.count;
    document.getElementById('ov-conflict-pending').textContent = conflicts.count;

    var html = '<table><thead><tr><th>BRANCH</th><th>STATUS</th><th>TERM</th><th>PEND</th><th>FAIL</th></tr></thead><tbody>';
    health.branches.forEach(function(b) {
      var bq = (byBranch.branches || []).find(function(x){ return x.code === b.code; }) || {};
      var badge = b.online ? '<span class="badge green">ONLINE</span>' : '<span class="badge">OFFLINE</span>';
      html += '<tr><td><strong>' + esc(b.name) + '</strong><br><span class="code">' + esc(b.code) + '</span></td>' +
        '<td>' + badge + '</td><td>' + b.connected_terminals + '</td>' +
        '<td>' + (bq.pending || 0) + '</td><td>' + (bq.failed || 0) + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('branch-summary-table').innerHTML = html;

    var c = conflicts.conflicts || [];
    if (c.length === 0) {
      document.getElementById('conflicts-preview').innerHTML = '<div class="empty">NO PENDING CONFLICTS</div>';
    } else {
      html = '<table><thead><tr><th>ENTITY</th><th>REASON</th><th>WHEN</th></tr></thead><tbody>';
      c.slice(0, 5).forEach(function(cf) {
        var fields = (cf.conflict_fields || []).map(function(f){ return f.field; }).join(', ');
        html += '<tr><td>' + esc(cf.entity_type) + ' #' + esc(cf.entity_id) + '</td>' +
          '<td style="color:var(--ink-dim);font-size:11px">' + esc(cf.reason) +
          '<br><span style="color:var(--hazard)">' + esc(fields) + '</span></td>' +
          '<td style="color:var(--ink-dim);font-size:11px">' + formatTime(cf.created_at) + '</td></tr>';
      });
      if (c.length > 5) html += '<tr><td colspan="3" style="text-align:center;color:var(--ink-faint)">+' + (c.length - 5) + ' MORE</td></tr>';
      html += '</tbody></table>';
      document.getElementById('conflicts-preview').innerHTML = html;
    }
  } catch(e) { console.error('Overview poll failed:', e); }
}

// ── Branches ──
async function refreshBranches() {
  try {
    var health = await fetchJSON('/api/dashboard/branches/health');
    var html = '<table><thead><tr><th>BRANCH</th><th>CODE</th><th>TYPE</th><th>STATUS</th><th>TERM</th><th>NODE</th></tr></thead><tbody>';
    health.branches.forEach(function(b) {
      var st = b.online ? '<span class="badge green">ONLINE</span>' : '<span class="badge">OFFLINE</span>';
      html += '<tr><td><strong>' + esc(b.name) + '</strong></td><td class="code">' + esc(b.code) + '</td>' +
        '<td><span class="badge blue">' + esc(b.pos_type) + '</span></td><td>' + st + '</td>' +
        '<td>' + b.connected_terminals + '</td><td class="code">' + esc(b.node_id || '—') + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('branches-table').innerHTML = html;
  } catch(e) { console.error('Branches poll failed:', e); }
}

// ── Queue ──
async function refreshQueue() {
  try {
    var [byBranch, pending] = await Promise.all([
      fetchJSON('/api/dashboard/queue/by-branch'),
      fetchJSON('/api/dashboard/queue/list/pending'),
    ]);
    var html = '<table><thead><tr><th>BRANCH</th><th>CODE</th><th>PENDING</th><th>FAILED</th></tr></thead><tbody>';
    (byBranch.branches || []).forEach(function(b) {
      html += '<tr><td><strong>' + esc(b.branch) + '</strong></td><td class="code">' + esc(b.code) + '</td>' +
        '<td>' + (b.pending > 0 ? '<span class="badge yellow">' + b.pending + '</span>' : '0') + '</td>' +
        '<td>' + (b.failed > 0 ? '<span class="badge red">' + b.failed + '</span>' : '0') + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('queue-table').innerHTML = html;

    var items = pending.items || [];
    if (items.length === 0) {
      document.getElementById('queue-pending-list').innerHTML = '<div class="empty">NO PENDING ITEMS</div>';
    } else {
      html = '<table><thead><tr><th>ID</th><th>BRANCH</th><th>OP</th><th>ENTITY</th><th>ATT</th><th>NEXT</th></tr></thead><tbody>';
      items.forEach(function(item) {
        html += '<tr><td>' + item.id + '</td><td>' + esc(item.branch) + '</td>' +
          '<td><span class="badge blue">' + esc(item.operation) + '</span></td>' +
          '<td>' + esc(item.entity_type) + '</td>' +
          '<td>' + item.attempt_count + '/' + item.max_attempts + '</td>' +
          '<td class="code">' + formatTime(item.next_retry_at) + '</td></tr>';
      });
      html += '</tbody></table>';
      document.getElementById('queue-pending-list').innerHTML = html;
    }
  } catch(e) { console.error('Queue poll failed:', e); }
}

// ── Conflicts ──
async function refreshConflicts() {
  try {
    var data = await fetchJSON('/api/dashboard/conflicts');
    var list = data.conflicts || [];
    if (list.length === 0) {
      document.getElementById('conflicts-list').innerHTML = '<div class="empty">NO PENDING CONFLICTS — DATA IN AGREEMENT</div>';
      return;
    }
    var html = '';
    list.forEach(function(c) {
      var fields = (c.conflict_fields || []).map(function(f) {
        return '<span class="field-tag">' + esc(f.field) + ' <span class="local">L=' + esc(JSON.stringify(f.local_value)) + '</span> / <span class="remote">R=' + esc(JSON.stringify(f.remote_value)) + '</span></span>';
      }).join('');
      html += '<div class="conflict-entry">' +
        '<div class="row">' +
          '<div><strong>' + esc(c.entity_type) + ' #' + esc(c.entity_id) + '</strong> <span class="badge yellow">' + esc(c.resolver_used) + '</span></div>' +
          '<span class="code">' + formatTime(c.created_at) + '</span>' +
        '</div>' +
        '<div style="color:var(--ink-dim);font-size:11px;margin-top:4px">' + esc(c.reason) + '</div>' +
        '<div class="code">BRANCH ' + esc(c.branch) + ' // NODE ' + esc(c.node_id) + '</div>' +
        (fields ? '<div class="fields">' + fields + '</div>' : '') +
        '<div class="conflict-actions">' +
          '<select id="resolve-select-' + c.id + '">' +
            '<option value="use_local">KEEP LOCAL</option>' +
            '<option value="use_remote">ACCEPT REMOTE</option>' +
            '<option value="merge">MERGE</option>' +
          '</select>' +
          '<button class="btn primary" onclick="resolveConflict(' + c.id + ')">RESOLVE</button>' +
          '<button class="btn ghost" onclick="dismissConflict(' + c.id + ')">DISMISS</button>' +
        '</div>' +
      '</div>';
    });
    document.getElementById('conflicts-list').innerHTML = html;
  } catch(e) { console.error('Conflicts poll failed:', e); }
}

async function resolveConflict(id) {
  var select = document.getElementById('resolve-select-' + id);
  if (!select) return;
  var resolution = select.value;
  try {
    var res = await fetch('/api/dashboard/conflicts/' + id + '/resolve', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ resolution: resolution, notes: 'Resolved via Sync Monitor console' }),
    });
    var data = await res.json();
    if (res.ok) {
      showToast('CONFLICT #' + id + ' RESOLVED // ' + resolution, 'ok');
      refreshConflicts();
    } else {
      showToast('FAILED: ' + (data.error || 'UNKNOWN'), 'err');
    }
  } catch(e) {
    showToast('ERROR: ' + e.message, 'err');
  }
}

async function dismissConflict(id) {
  try {
    var res = await fetch('/api/dashboard/conflicts/' + id + '/dismiss', { method: 'POST' });
    if (res.ok) {
      showToast('CONFLICT #' + id + ' DISMISSED', 'ok');
      refreshConflicts();
    } else {
      showToast('DISMISS FAILED', 'err');
    }
  } catch(e) {
    showToast('ERROR: ' + e.message, 'err');
  }
}

// ── Activity ──
async function refreshActivity() {
  try {
    var data = await fetchJSON('/api/dashboard/activity?limit=50');
    var entries = data.entries || [];
    if (entries.length === 0) {
      document.getElementById('activity-list').innerHTML = '<div class="empty">NO SYNC ACTIVITY LOGGED</div>';
      return;
    }
    var html = '<table><thead><tr><th>TIME</th><th>BRANCH</th><th>TYPE</th><th>COUNT</th><th>STATUS</th></tr></thead><tbody>';
    entries.forEach(function(e) {
      var badge = (e.status === 'processed' || e.status === 'received') ? '<span class="badge green">' + esc(e.status) + '</span>' :
        e.status === 'failed' ? '<span class="badge red">' + esc(e.status) + '</span>' : '<span class="badge">' + esc(e.status) + '</span>';
      html += '<tr><td class="code">' + formatTime(e.received_at) + '</td>' +
        '<td>' + esc(e.branch) + '</td>' +
        '<td>' + esc(e.entity_type) + '</td>' +
        '<td>' + e.entity_count + '</td>' +
        '<td>' + badge + '</td></tr>';
    });
    html += '</tbody></table>';
    document.getElementById('activity-list').innerHTML = html;
  } catch(e) { console.error('Activity poll failed:', e); }
}

// ── WebSocket sync-events stream ──
// The monitor consumes /ws/sync-events/ (served by daphne on the API port).
// Frames push live activity into the LIVE FEED and trigger quiet refreshes
// of the REST tiles — no interval polling while the stream is up.
var WS_PORT = '8767'; // daphne API port (make dev-api) — serves /ws/sync-events/
var wsSocket = null;
var wsBanner = document.getElementById('ws-banner');
var wsReconnectTimer = null;
var wsCountdownTimer = null;
var wsRetryDelay = 5000;          // auto-retry cadence while LOST
var wsRetryIn = 0;                // seconds shown in the countdown
var fallbackPollTimer = null;     // slow REST poll ONLY while LOST
var lastRefreshAt = 0;            // throttle for WS-triggered refetches
var liveActivity = [];            // frames pushed over the stream (LIVE FEED)

function setStreamState(state) {
  var led = document.getElementById('ws-led');
  var st = document.getElementById('ws-status');
  var bar = document.getElementById('stream-state');
  if (state === 'LIVE') {
    led.className = 'led on';
    st.textContent = 'LINKED';
    st.className = 'val green';
    if (bar) { bar.textContent = 'STREAM // LIVE'; bar.className = 'stream-live'; }
  } else if (state === 'LOST') {
    led.className = 'led warn';
    st.textContent = 'LOST';
    st.className = 'val red';
    if (bar) { bar.textContent = 'STREAM // LOST'; bar.className = 'stream-lost'; }
  } else {
    led.className = 'led';
    st.textContent = 'STANDBY';
    st.className = 'val';
    if (bar) { bar.textContent = 'STREAM // STANDBY'; bar.className = ''; }
  }
}

function showLostBanner(show) {
  if (!wsBanner) return;
  wsBanner.style.display = show ? 'flex' : 'none';
  wsBanner.setAttribute('aria-live', 'assertive');
}

function updateRetryCountdown() {
  var el = document.getElementById('ws-retry-in');
  if (el) el.textContent = String(Math.max(0, wsRetryIn)).padStart(2, '0') + 'S';
}

function startFallbackPoll() {
  if (fallbackPollTimer) return;
  fallbackPollTimer = setInterval(function () { refreshAll(); }, 10000);
}

function stopFallbackPoll() {
  if (fallbackPollTimer) { clearInterval(fallbackPollTimer); fallbackPollTimer = null; }
}

function scheduleRefresh() {
  var now = Date.now();
  if (now - lastRefreshAt < 2000) return;
  lastRefreshAt = now;
  refreshAll();
}

function renderLiveFeed() {
  var el = document.getElementById('live-feed');
  if (!el) return;
  if (liveActivity.length === 0) {
    el.innerHTML = '<div class="empty">AWAITING STREAM EVENTS…</div>';
    return;
  }
  var html = '<table><thead><tr><th>PUSH</th><th>BRANCH</th><th>TYPE</th><th>COUNT</th><th>STATUS</th></tr></thead><tbody>';
  liveActivity.forEach(function (e) {
    var badge = e.status === 'link'
      ? '<span class="badge blue">LINK</span>'
      : '<span class="badge green">PUSHED</span>';
    html += '<tr><td class="code">' + formatTime(e.received_at) + '</td>' +
      '<td>' + esc(e.branch || '—') + '</td>' +
      '<td>' + esc(e.entity_type) + '</td>' +
      '<td>' + e.entity_count + '</td>' +
      '<td>' + badge + '</td></tr>';
  });
  html += '</tbody></table>';
  el.innerHTML = html;
}

function handleFrame(frame) {
  // sync_event frames: receiver broadcasts + terminal link changes.
  if (frame && typeof frame.entity_type === 'string') {
    var now = new Date();
    document.getElementById('last-push').textContent = now.toLocaleTimeString();
    liveActivity.unshift({
      received_at: now.toISOString(),
      branch: frame.branch || '',
      entity_type: frame.entity_type,
      entity_count: frame.synced == null ? 1 : frame.synced,
      status: frame.entity_type.indexOf('terminal') === 0 ? 'link' : 'pushed',
    });
    if (liveActivity.length > 20) liveActivity.pop();
    renderLiveFeed();
    scheduleRefresh(); // refresh health/queue/conflict tiles (throttled)
  }
  // broker_message frames target branch groups the monitor does not join;
  // identify_ack / error frames are not expected — ignored defensively.
}

function connectWs() {
  var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  var url = proto + '//' + location.hostname + ':' + WS_PORT + '/ws/sync-events/';
  wsSocket = new WebSocket(url);
  wsSocket.onopen = function () {
    if (wsCountdownTimer) { clearInterval(wsCountdownTimer); wsCountdownTimer = null; }
    showLostBanner(false);
    setStreamState('LIVE');
    stopFallbackPoll();
    refreshAll(); // fresh tiles on (re)connect
  };
  wsSocket.onmessage = function (ev) {
    var frame;
    try { frame = JSON.parse(ev.data); } catch (e) { return; }
    handleFrame(frame);
  };
  wsSocket.onerror = function () { /* onclose handles reconnect */ };
  wsSocket.onclose = function () {
    setStreamState('LOST');
    showLostBanner(true);
    startFallbackPoll();
    wsRetryIn = Math.round(wsRetryDelay / 1000);
    updateRetryCountdown();
    if (wsCountdownTimer) clearInterval(wsCountdownTimer);
    wsCountdownTimer = setInterval(function () {
      wsRetryIn -= 1;
      if (wsRetryIn < 0) wsRetryIn = 0;
      updateRetryCountdown();
    }, 1000);
    if (wsReconnectTimer) clearTimeout(wsReconnectTimer);
    wsReconnectTimer = setTimeout(connectWs, wsRetryDelay);
  };
}

document.getElementById('ws-retry-btn').addEventListener('click', function () {
  if (wsReconnectTimer) clearTimeout(wsReconnectTimer);
  if (wsCountdownTimer) clearInterval(wsCountdownTimer);
  if (wsSocket) { try { wsSocket.close(); } catch (e) {} }
  connectWs();
});

document.getElementById('force-poll').addEventListener('click', function () {
  refreshAll();
});

connectWs();

// ── Initial poll ──
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
<title>Formint Cloud Analytics</title>
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
      <h1>Formint Cloud Analytics</h1>
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
  Formint Cloud • <a href="/admin/">Unfold Admin</a> •
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

    from apps.core.api import api

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
    # Server surface: /stats + root CRUD paths the frontend proxies to :8767
    path("stats", apps_handlers_surface_stats, name="stats"),
    path("monitor/status", apps_handlers_surface_monitor_status, name="monitor-status"),
    path("", include((apps_handlers_surface_urlpatterns, "surface"), namespace="surface")),

    # Unfold Admin
    path("admin/", admin.site.urls),

    # Protected, read-only MCP designer tools for website/webapp audits and
    # component scaffolds. Access is enforced by the django-fusion view.
    path("fusion/mcp/designer/", include(fusion_designer_urls)),

    # BoltAPI analytics dashboard — catch-all bridge to internal routing
    # All /apis/data/* requests are forwarded to the BoltAPI instance in core/api.py
    re_path(r"^apis/data/(?P<route>.*)$", _bolt_catch_all, name="bolt_catch_all"),

    # REST API (django-fusion viewsets + sync receivers + community bridges)
    path("api/", include("apps.core.urls")),

    # django-fusion API-first handlers (server contract)
    path("fusion/", include("apps.handlers.urls")),
]
