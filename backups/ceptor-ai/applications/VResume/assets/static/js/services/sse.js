import { generateId } from '../lib/helpers.js';

// ─────────────────────────────────────────────────────────────
// Mixin: ConnectionMixin
// Responsibility: lifecycle of SSE / WebSocket connections
// ─────────────────────────────────────────────────────────────

const ConnectionMixin = (Base) => class extends Base {
  /**
   * Open an SSE (or WebSocket) connection.
   * @param {string} url
   * @param {object} [opts]
   * @param {boolean} [opts.autoReconnect=true]
   * @param {Function} [opts.onMessage]
   * @param {Function} [opts.onError]
   * @returns {Promise<string>} connectionId
   */
  async connect(url, opts = {}) {
    if (this._connections.size >= this._cfg.maxConnections) {
      throw new Error(`[SSEHandler] Max connections (${this._cfg.maxConnections}) reached`);
    }

    const id = generateId('conn');
    const useWS = url.startsWith('ws://') || url.startsWith('wss://');

    return useWS
      ? this._openWebSocket(id, url, opts)
      : this._openSSE(id, url, opts);
  }

  /**
   * Close a specific connection.
   * @param {string} id
   */
  disconnect(id) {
    const conn = this._connections.get(id);
    if (!conn) return false;
    this._cleanup(id);
    this._connections.delete(id);
    this._reconnectCount.delete(id);
    this._emit('connection:closed', { id });
    return true;
  }

  /** Close all open connections */
  disconnectAll() {
    [...this._connections.keys()].forEach(id => this.disconnect(id));
  }

  // ── Private ──────────────────────────────────────────────────

  /** @returns {Promise<string>} */
  _openSSE(id, url, opts) {
    return new Promise((resolve, reject) => {
      const es = new EventSource(url, { withCredentials: true });
      const conn = { id, type: 'sse', es, url, opts, status: 'connecting' };
      let resolved = false;

      es.onopen = () => {
        conn.status = 'open';
        if (!resolved) { resolved = true; resolve(id); }
        this._emit('connection:open', { id, type: 'sse' });
      };

      es.onmessage = (e) => {
        conn.status = 'open';
        if (!resolved) { resolved = true; resolve(id); }
        this._onMessage(id, e.data, conn);
      };

      es.onerror = (err) => {
        if (!resolved) { resolved = true; reject(new Error('SSE connection failed')); }
        this._onConnError(id, err, conn);
      };

      this._connections.set(id, conn);
      this._reconnectCount.set(id, 0);

      // Hard timeout: close after 1 h
      const t = setTimeout(() => this.disconnect(id), 3_600_000);
      this._timeouts.set(id, t);
    });
  }

  /** @returns {Promise<string>} */
  _openWebSocket(id, url, opts) {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(url);
      const conn = { id, type: 'ws', ws, url, opts, status: 'connecting' };

      const timeout = setTimeout(() => {
        ws.close();
        reject(new Error('WebSocket connection timeout'));
      }, 10_000);

      ws.onopen = () => {
        clearTimeout(timeout);
        conn.status = 'open';
        resolve(id);
        this._emit('connection:open', { id, type: 'ws' });
        // Heartbeat
        const hb = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping', ts: Date.now() }));
          }
        }, 30_000);
        this._heartbeats.set(id, hb);
      };

      ws.onmessage = (e) => this._onMessage(id, e.data, conn);

      ws.onerror = (err) => {
        clearTimeout(timeout);
        this._onConnError(id, err, conn);
        reject(err);
      };

      ws.onclose = (e) => {
        conn.status = 'closed';
        this._emit('connection:close', { id, code: e.code, reason: e.reason });
        if (opts.autoReconnect !== false && e.code !== 1000) {
          this._scheduleReconnect(id, url, opts);
        }
      };

      this._connections.set(id, conn);
      this._reconnectCount.set(id, 0);
    });
  }

  _onMessage(id, raw, conn) {
    try {
      const data = JSON.parse(raw);
      conn.opts.onMessage?.(data, id);
      this._emit('message', { id, data, type: conn.type });

      if (data.type === 'notification' || data.event === 'notification') {
        this._handleNotificationPayload(data.data ?? data);
      }
    } catch {
      console.warn('[SSEHandler] Non-JSON message ignored');
    }
  }

  _onConnError(id, err, conn) {
    conn.status = 'error';
    conn.opts.onError?.(err, id);
    this._emit('connection:error', { id, err });
    if (conn.opts.autoReconnect !== false) {
      this._scheduleReconnect(id, conn.url, conn.opts);
    }
  }

  _scheduleReconnect(id, url, opts) {
    const count = (this._reconnectCount.get(id) ?? 0) + 1;
    if (count > this._cfg.maxReconnectAttempts) {
      this.disconnect(id);
      return;
    }
    this._reconnectCount.set(id, count);
    const delay = this._cfg.reconnectDelay * Math.pow(1.5, count - 1);
    setTimeout(async () => {
      this._cleanup(id);
      try { await this.connect(url, opts); } catch { /* will retry */ }
    }, delay);
  }

  _cleanup(id) {
    const conn = this._connections.get(id);
    if (!conn) return;
    if (conn.type === 'sse') conn.es?.close();
    if (conn.type === 'ws' && conn.ws?.readyState === WebSocket.OPEN) conn.ws.close(1000);
    clearInterval(this._heartbeats.get(id));
    clearTimeout(this._timeouts.get(id));
    this._heartbeats.delete(id);
    this._timeouts.delete(id);
  }
};

// ─────────────────────────────────────────────────────────────
// Mixin: HTMXMixin
// Responsibility: parse HTMX response headers for notifications
// ─────────────────────────────────────────────────────────────

const HTMXMixin = (Base) => class extends Base {
  _setupHTMX() {
    if (typeof htmx === 'undefined') return;

    // After HTMX swaps content, scan HX-Trigger headers for notifications
    document.addEventListener('htmx:afterRequest', (e) => {
      const xhr = e.detail?.xhr;
      if (!xhr) return;
      ['HX-Trigger', 'HX-Trigger-After-Settle', 'HX-Trigger-After-Swap'].forEach(h => {
        const val = xhr.getResponseHeader(h);
        if (val) this._parseHTMXTrigger(val);
      });
    });

    // Surface HTMX errors as notifications
    document.addEventListener('htmx:responseError', (e) => {
      const xhr = e.detail?.xhr;
      if (!xhr || xhr.status < 400) return;
      let message = `Error ${xhr.status}`;
      try { message = JSON.parse(xhr.responseText)?.message ?? message; } catch { /* ignore */ }
      this._handleNotificationPayload({ type: 'error', message, duration: 10_000 });
    });
  }

  /** @param {string} raw — JSON string from HX-Trigger header */
  _parseHTMXTrigger(raw) {
    try {
      const triggers = JSON.parse(raw);
      Object.entries(triggers).forEach(([key, value]) => {
        if (['showNotification', 'notification', 'notify'].includes(key)) {
          this._handleNotificationPayload(value);
        }
        if (key.startsWith('notify_')) {
          const type = key.replace('notify_', '');
          this._handleNotificationPayload({
            message: value?.message ?? value,
            type: ['success', 'error', 'warning', 'info'].includes(type) ? type : 'info',
          });
        }
      });
    } catch {
      // Simple comma-separated trigger names — not notification payloads
    }
  }
};

// ─────────────────────────────────────────────────────────────
// Mixin: NotificationMixin
// Responsibility: normalise payloads and dispatch to UI
// ─────────────────────────────────────────────────────────────

const NotificationMixin = (Base) => class extends Base {
  /**
   * Show a notification via the registered notification system or console.
   * @param {string|object} data
   * @param {object} [extra]
   */
  notify(data, extra = {}) {
    const payload = this._normalise(data, extra);
    if (!payload.message && !payload.title) return;

    if (this._notificationSystem?.show) {
      this._notificationSystem.show(payload.message, {
        type:     payload.type ?? 'info',
        title:    payload.title,
        duration: payload.duration ?? 5000,
        ...extra,
      });
    } else {
      console.info(`[Notification:${payload.type}] ${payload.title ? payload.title + ': ' : ''}${payload.message}`);
    }

    this._emit('notification:shown', payload);
  }

  // ── Private ──────────────────────────────────────────────────

  /** @param {string|object} raw @returns {object} */
  _normalise(raw, extra = {}) {
    if (typeof raw === 'string') return { message: raw, type: 'info', ...extra };
    return {
      message:  raw.message ?? raw.msg ?? '',
      type:     raw.type ?? raw.level ?? 'info',
      title:    raw.title ?? '',
      duration: raw.duration ?? 5000,
      icon:     raw.icon ?? '',
      ...extra,
    };
  }

  _handleNotificationPayload(data) {
    this.notify(data);
  }
};

// ─────────────────────────────────────────────────────────────
// Base class
// ─────────────────────────────────────────────────────────────

class _SSEBase {
  constructor() {
    // intentionally empty — mixins populate behaviour
  }
}

// ─────────────────────────────────────────────────────────────
// SSEHandler — public class
// ─────────────────────────────────────────────────────────────

/**
 * Unified SSE + HTMX notification handler.
 *
 * @example
 * import { SSEHandler } from '@handlers/sse.js';
 *
 * const sse = new SSEHandler({ ssePath: '/notifications/' });
 * sse.install(myNotificationSystem);
 * // or manually:
 * await sse.connect('/notifications/');
 */
export class SSEHandler extends HTMXMixin(NotificationMixin(ConnectionMixin(_SSEBase))) {
  /**
   * @param {object} [opts]
   * @param {string}  [opts.ssePath='/notifications/']
   * @param {number}  [opts.maxConnections=5]
   * @param {number}  [opts.maxReconnectAttempts=5]
   * @param {number}  [opts.reconnectDelay=3000]
   */
  constructor(opts = {}) {
    super();

    this._cfg = {
      ssePath:              '/notifications/',
      maxConnections:       5,
      maxReconnectAttempts: 5,
      reconnectDelay:       3000,
      ...opts,
    };

    /** @type {Map<string, object>} */
    this._connections    = new Map();
    /** @type {Map<string, number>} */
    this._reconnectCount = new Map();
    /** @type {Map<string, ReturnType<typeof setInterval>>} */
    this._heartbeats     = new Map();
    /** @type {Map<string, ReturnType<typeof setTimeout>>} */
    this._timeouts       = new Map();

    /** @type {EventTarget} */
    this._bus = new EventTarget();

    /** @type {object|null} */
    this._notificationSystem = null;
  }

  // ── Public API ───────────────────────────────────────────────

  /**
   * Wire up to a notification UI system and start the default SSE connection.
   * @param {object} notificationSystem — must expose `.show(message, opts)`
   * @param {object} [opts]
   */
  install(notificationSystem, opts = {}) {
    this._notificationSystem = notificationSystem;
    Object.assign(this._cfg, opts);

    this._setupHTMX();

    if (this._cfg.ssePath) {
      this.connect(this._cfg.ssePath, { autoReconnect: true }).catch(err => {
        console.warn('[SSEHandler] Default SSE connection failed:', err.message);
      });
    }

    return this;
  }

  /** Expose global helpers for inline scripts / Django templates */
  exposeGlobal() {
    window.sseHandler = {
      notify:        (msg, opts) => this.notify(msg, opts),
      connect:       (url, opts) => this.connect(url, opts),
      disconnect:    (id)        => this.disconnect(id),
      disconnectAll: ()          => this.disconnectAll(),
      connections:   ()          => [...this._connections.entries()].map(([id, c]) => ({
        id, type: c.type, status: c.status, url: c.url,
      })),
    };
    return this;
  }

  // ── Event bus ────────────────────────────────────────────────

  /**
   * Subscribe to internal events.
   * @param {string} event
   * @param {EventListenerOrEventListenerObject} handler
   * @returns {() => void} unsubscribe
   */
  on(event, handler) {
    this._bus.addEventListener(event, handler);
    return () => this._bus.removeEventListener(event, handler);
  }

  /** @param {string} event @param {object} detail */
  _emit(event, detail = {}) {
    this._bus.dispatchEvent(new CustomEvent(event, { detail }));
  }
}

// ── Backward-compat alias (replaces old SSESecurityHandler) ──
export { SSEHandler as SSESecurityHandler };
