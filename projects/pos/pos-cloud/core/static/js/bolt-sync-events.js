/**
 * sync-events.js — Real-time sync event listener for POS Cloud dashboards.
 *
 * Connects to the ws://<host>/ws/sync-events/ WebSocket endpoint and
 * updates both the analytics dashboard (/apis/) and the Unfold admin
 * dashboard (/admin/) live as branch sync data arrives.
 *
 * Features:
 *   - Live KPI badge incrementing on the admin dashboard
 *   - Sync event log viewer (last 50 events, scrollable) on the bolt dashboard
 *   - WebSocket status indicator (connected / disconnected)
 *   - Auto-reconnects with exponential backoff
 */
(function () {
  "use strict";

  var RECONNECT_BASE_MS = 1000;
  var RECONNECT_MAX_MS = 30000;
  var reconnectDelay = RECONNECT_BASE_MS;
  var ws = null;
  var reconnectTimer = null;

  // ── Ring buffer for the sync event log ───────────────────────────
  var MAX_LOG_ENTRIES = 50;
  var logEntries = [];
  var logPanel = null;

  // ── Helpers ──────────────────────────────────────────────────────

  function wsUrl() {
    var proto = location.protocol === "https:" ? "wss:" : "ws:";
    return proto + "//" + location.host + "/ws/sync-events/";
  }

  function pulseElement(el) {
    if (!el) return;
    el.style.transition = "box-shadow 0.15s ease";
    el.style.boxShadow = "0 0 0 3px rgba(16, 185, 129, 0.4)";
    setTimeout(function () { el.style.boxShadow = ""; }, 800);
  }

  function timeAgo(isoString) {
    var d = new Date(isoString);
    if (isNaN(d.getTime())) return "";
    var seconds = Math.floor((Date.now() - d.getTime()) / 1000);
    if (seconds < 5) return "just now";
    if (seconds < 60) return seconds + "s ago";
    var mins = Math.floor(seconds / 60);
    if (mins < 60) return mins + "m ago";
    return d.toLocaleTimeString();
  }

  /** Get a colored icon character for each entity type. */
  function typeIcon(entityType) {
    switch (entityType) {
      case "products":  return "📦";
      case "sales":     return "🛒";
      case "inventory": return "📋";
      case "heartbeat": return "💓";
      default:          return "📌";
    }
  }

  /** Get a badge color class for each entity type. */
  function typeBadgeClass(entityType) {
    switch (entityType) {
      case "products":  return "sync-log-badge--products";
      case "sales":     return "sync-log-badge--sales";
      case "inventory": return "sync-log-badge--inventory";
      case "heartbeat": return "sync-log-badge--heartbeat";
      default:          return "";
    }
  }

  /** Increment a counter element by delta, pulsing the parent card. */
  function incrementCount(entityType, delta) {
    var countEl = document.querySelector('[data-sync-count="' + entityType + '"]');
    if (!countEl) return;
    var current = parseInt(countEl.textContent, 10) || 0;
    countEl.textContent = String(current + delta);

    var badge = document.querySelector('[data-sync-badge="' + entityType + '"]');
    if (badge) {
      var deltaEl = badge.querySelector('[data-sync-delta="' + entityType + '"]');
      if (deltaEl) deltaEl.textContent = "+" + delta;
      badge.style.display = "block";
      clearTimeout(badge._hideTimer);
      badge._hideTimer = setTimeout(function () { badge.style.display = "none"; }, 4000);
    }

    var card = document.querySelector('[data-sync-card="' + entityType + '"]');
    if (card) pulseElement(card);
  }

  function updateLastSync(branchName, timestamp) {
    var el = document.querySelector('[data-sync-last-branch]');
    if (el && branchName) el.textContent = branchName;

    if (timestamp) {
      var timeEl = document.querySelector('[data-sync-last-time]');
      if (timeEl) {
        var d = new Date(timestamp);
        if (!isNaN(d.getTime())) {
          timeEl.textContent = d.toLocaleTimeString();
        }
      }
    }

    var card = document.querySelector('[data-sync-card="heartbeat"]');
    if (card) pulseElement(card);
  }

  function setWsStatus(status) {
    var dot = document.getElementById("sync-status-dot");
    var label = document.getElementById("sync-status-label");
    if (!dot || !label) return;
    dot.setAttribute("data-sync-status", status);
    dot.className = "w-2 h-2 rounded-full " + (
      status === "connected" ? "bg-emerald-500" :
      status === "connecting" ? "bg-amber-400" : "bg-gray-400"
    );
    label.textContent = status;
  }

  // ── Sync Event Log Viewer ────────────────────────────────────────

  /** Build and inject the log viewer panel into the bolt dashboard. */
  function createLogPanel() {
    // Only create on bolt dashboard pages, and only once.
    if (!location.pathname.startsWith("/apis")) return;
    if (logPanel || document.getElementById("sync-event-log")) return;

    var panel = document.createElement("div");
    panel.id = "sync-event-log";
    panel.innerHTML =
      '<div class="sync-log-header">' +
        '<span class="sync-log-title">📡 Sync Event Log</span>' +
        '<span class="sync-log-count" id="sync-log-count">0 events</span>' +
        '<button class="sync-log-toggle" id="sync-log-toggle" title="Minimize">▾</button>' +
        '<button class="sync-log-clear" id="sync-log-clear" title="Clear log">✖</button>' +
      '</div>' +
      '<div class="sync-log-list" id="sync-log-list">' +
        '<div class="sync-log-empty">Waiting for sync events…</div>' +
      '</div>';

    // Inject styles
    var style = document.createElement("style");
    style.textContent =
      "#sync-event-log {" +
        "position:fixed;bottom:16px;right:16px;width:380px;max-height:420px;" +
        "background:#1e293b;border:1px solid #334155;border-radius:12px;" +
        "box-shadow:0 8px 32px rgba(0,0,0,0.4);z-index:9999;" +
        "display:flex;flex-direction:column;font-family:system-ui,sans-serif;" +
        "font-size:13px;color:#e2e8f0;overflow:hidden;" +
      "}" +
      ".sync-log-header {" +
        "display:flex;align-items:center;gap:8px;padding:10px 14px;" +
        "background:#0f172a;border-bottom:1px solid #334155;" +
        "font-weight:600;font-size:13px;" +
      "}" +
      ".sync-log-title { flex:1; }" +
      ".sync-log-count { font-size:11px;color:#94a3b8; }" +
      ".sync-log-clear {" +
        "background:none;border:none;color:#64748b;cursor:pointer;" +
        "font-size:14px;padding:0 2px;line-height:1;" +
      "}" +
      ".sync-log-clear:hover { color:#f87171; }" +
      ".sync-log-toggle {" +
        "background:none;border:none;color:#64748b;cursor:pointer;" +
        "font-size:12px;padding:0 2px;line-height:1;transition:transform 0.2s;" +
      "}" +
      ".sync-log-toggle:hover { color:#e2e8f0; }" +
      ".sync-log-toggle.collapsed { transform:rotate(-90deg); }" +
      "#sync-event-log.collapsed #sync-log-list { display:none; }" +
      "#sync-event-log.collapsed { max-height:none; }" +
      ".sync-log-list {" +
        "flex:1;overflow-y:auto;padding:6px 0;" +
        "scroll-behavior:smooth;" +
      "}" +
      ".sync-log-list::-webkit-scrollbar { width:5px; }" +
      ".sync-log-list::-webkit-scrollbar-thumb { background:#475569;border-radius:3px; }" +
      ".sync-log-empty {" +
        "padding:24px 14px;text-align:center;color:#64748b;font-size:12px;" +
      "}" +
      ".sync-log-entry {" +
        "display:flex;align-items:flex-start;gap:8px;padding:6px 14px;" +
        "border-bottom:1px solid #1e293b;transition:background 0.15s;" +
        "animation:sync-log-slide-in 0.2s ease-out;" +
      "}" +
      ".sync-log-entry:hover { background:#1e293b; }" +
      ".sync-log-entry:first-child { background:#1e293b; }" +
      ".sync-log-entry-icon { font-size:16px;flex-shrink:0;margin-top:1px; }" +
      ".sync-log-entry-body { flex:1;min-width:0; }" +
      ".sync-log-entry-meta {" +
        "display:flex;align-items:center;gap:6px;margin-bottom:2px;" +
      "}" +
      ".sync-log-entry-branch {" +
        "font-weight:600;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;" +
      "}" +
      ".sync-log-badge {" +
        "display:inline-block;padding:0 6px;border-radius:4px;font-size:10px;" +
        "font-weight:600;text-transform:uppercase;letter-spacing:0.5px;white-space:nowrap;" +
      "}" +
      ".sync-log-badge--products  { background:#05966933;color:#34d399; }" +
      ".sync-log-badge--sales     { background:#2563eb33;color:#60a5fa; }" +
      ".sync-log-badge--inventory { background:#d9770633;color:#fbbf24; }" +
      ".sync-log-badge--heartbeat { background:#7c3aed33;color:#a78bfa; }" +
      ".sync-log-entry-detail { font-size:11px;color:#94a3b8; }" +
      ".sync-log-entry-time { font-size:10px;color:#64748b;flex-shrink:0;margin-top:1px; }" +
      "@keyframes sync-log-slide-in {" +
        "from { opacity:0; transform:translateX(20px); }" +
        "to   { opacity:1; transform:translateX(0); }" +
      "}";

    document.head.appendChild(style);
    document.body.appendChild(panel);
    logPanel = panel;

    // Clear button handler
    document.getElementById("sync-log-clear").onclick = function () {
      logEntries = [];
      renderLog();
    };

    // Toggle collapse button
    document.getElementById("sync-log-toggle").onclick = function () {
      var panel = document.getElementById("sync-event-log");
      var btn = document.getElementById("sync-log-toggle");
      if (!panel || !btn) return;
      var collapsed = panel.classList.toggle("collapsed");
      btn.classList.toggle("collapsed", collapsed);
      btn.title = collapsed ? "Expand" : "Minimize";
      btn.textContent = collapsed ? "▸" : "▾";
    };
  }

  /** Re-render the log list from the ring buffer. */
  function renderLog() {
    var list = document.getElementById("sync-log-list");
    var countEl = document.getElementById("sync-log-count");
    if (!list) return;

    if (logEntries.length === 0) {
      list.innerHTML = '<div class="sync-log-empty">Waiting for sync events…</div>';
    } else {
      list.innerHTML = logEntries.map(function (entry, i) {
        return (
          '<div class="sync-log-entry">' +
            '<span class="sync-log-entry-icon">' + typeIcon(entry.entity_type) + '</span>' +
            '<div class="sync-log-entry-body">' +
              '<div class="sync-log-entry-meta">' +
                '<span class="sync-log-entry-branch">' + escHtml(entry.branch || entry.node_id || "—") + '</span>' +
                '<span class="sync-log-badge ' + typeBadgeClass(entry.entity_type) + '">' + escHtml(entry.entity_type) + '</span>' +
              '</div>' +
              '<div class="sync-log-entry-detail">' + formatDetail(entry) + '</div>' +
            '</div>' +
            '<span class="sync-log-entry-time">' + timeAgo(entry.timestamp) + '</span>' +
          '</div>'
        );
      }).join("");
    }

    if (countEl) countEl.textContent = logEntries.length + " event" + (logEntries.length !== 1 ? "s" : "");
    // Auto-scroll to top only if user is already near the top.
    var wasAtTop = list.scrollTop < 40;
    if (wasAtTop) list.scrollTop = 0;
  }

  function escHtml(str) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function formatDetail(entry) {
    var parts = [];
    if (entry.synced != null) parts.push(entry.synced + " items");
    if (entry.status) parts.push(entry.status);
    if (entry.node_id && !entry.branch) parts.push("node " + entry.node_id);
    return parts.join(" • ") || "—";
  }

  /** Push an event onto the ring buffer and re-render. */
  function pushLogEntry(payload) {
    // Only accumulate entries if the log panel exists.
    if (!logPanel) return;
    logEntries.unshift({
      entity_type: payload.entity_type || "unknown",
      branch: payload.branch || "",
      node_id: payload.node_id || "",
      synced: payload.synced,
      status: payload.status,
      timestamp: payload.timestamp || new Date().toISOString(),
    });
    if (logEntries.length > MAX_LOG_ENTRIES) {
      logEntries.length = MAX_LOG_ENTRIES;
    }
    renderLog();
  }

  // ── Event handlers ───────────────────────────────────────────────

  function onProductsSync(data) {
    console.log("[sync-events] Products synced:", data.synced, "from", data.branch);
    incrementCount("products", data.synced || 0);
    pushLogEntry(data);
  }

  function onSalesSync(data) {
    console.log("[sync-events] Sales synced:", data.synced, "from", data.branch);
    incrementCount("sales", data.synced || 0);
    pushLogEntry(data);
  }

  function onInventorySync(data) {
    console.log("[sync-events] Inventory synced:", data.synced, "from", data.branch);
    incrementCount("inventory", data.synced || 0);
    pushLogEntry(data);
  }

  function onHeartbeat(data) {
    console.log("[sync-events] Heartbeat from", data.branch, "-", data.status);
    updateLastSync(data.branch, data.timestamp);
    pushLogEntry(data);
  }

  function onUnknown(data) {
    console.log("[sync-events] Unknown event:", data);
    pushLogEntry(data);
  }

  // ── Message dispatcher ───────────────────────────────────────────

  function handleMessage(event) {
    var payload;
    try { payload = JSON.parse(event.data); } catch (e) { return; }

    switch (payload.entity_type) {
      case "products":  onProductsSync(payload); break;
      case "sales":     onSalesSync(payload); break;
      case "inventory": onInventorySync(payload); break;
      case "heartbeat": onHeartbeat(payload); break;
      default:          onUnknown(payload); break;
    }
  }

  // ── Connection lifecycle ─────────────────────────────────────────

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) return;
    setWsStatus("connecting");

    ws = new WebSocket(wsUrl());

    ws.onopen = function () {
      console.log("[sync-events] Connected to", wsUrl());
      setWsStatus("connected");
      reconnectDelay = RECONNECT_BASE_MS;
    };

    ws.onmessage = handleMessage;

    ws.onclose = function (event) {
      console.warn("[sync-events] Disconnected (code=" + event.code + "), reconnecting in " + (reconnectDelay / 1000) + "s");
      setWsStatus("disconnected");
      scheduleReconnect();
    };

    ws.onerror = function () {
      setWsStatus("disconnected");
    };
  }

  function scheduleReconnect() {
    if (reconnectTimer) return;
    reconnectTimer = setTimeout(function () {
      reconnectTimer = null;
      connect();
      reconnectDelay = Math.min(reconnectDelay * 2, RECONNECT_MAX_MS);
    }, reconnectDelay);
  }

  // ── Start ────────────────────────────────────────────────────────

  if (location.pathname.startsWith("/apis") || location.pathname.startsWith("/admin")) {
    // Create the log viewer panel on the bolt dashboard.
    createLogPanel();
    connect();
  }
})();
