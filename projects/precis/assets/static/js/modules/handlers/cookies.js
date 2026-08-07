/* global htmx */
export class CookieManagerHandler {
  /* ---------- public config ---------- */
  config = {
    csrfHeaderName: 'X-CSRFToken',   // header sent to server
    csrfCookieName: 'csrftoken',     // fallback cookie names
    csrfMetaName: 'csrf-token',      // meta tag name
    retryOnCsrfFailure: true,        // auto-refresh once on 403
    cookieDefaults: { path: '/', sameSite: 'lax', days: 90 }
  };

  /* ---------- ctor ---------- */
  constructor(userConfig = {}) {
    Object.assign(this.config, userConfig);
    this._csrf = null;                // current token
    this._formInput = null;           // fallback input node
    this._installIntercepts();        // fetch + htmx
    console.log('🍪 CookieManagerHandler ready');
  }

  /* ---------- init (returns promise) ---------- */
  async init() {
    this._csrf = this._locateToken();
    if (!this._csrf) {
      console.warn('⚠️  CSRF token not found – injecting fallback input');
      this._injectFallbackInput();
      this._csrf = this._locateToken(); // try again
    }
    console.log('🔒 CSRF ready:', this._csrf);
    return Promise.resolve();
  }

  /* =========================================================
   *  COOKIE API  (unchanged signature)
   * ========================================================= */
  set(name, value, opts = {}) {
    const cfg = { ...this.config.cookieDefaults, ...opts };
    let c = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
    if (cfg.days) {
      const d = new Date(Date.now() + cfg.days * 864e5);
      c += `; expires=${d.toUTCString()}`;
    }
    ['path', 'domain', 'sameSite'].forEach(k => { if (cfg[k]) c += `; ${k}=${cfg[k]}`; });
    if (cfg.secure) c += '; secure';
    if (cfg.httpOnly) c += '; httponly';
    document.cookie = c;
    return true;
  }

  get(name) {
    const eq = `${encodeURIComponent(name)}=`;
    return document.cookie.split(';')
      .map(p => p.trim())
      .find(p => p.startsWith(eq))
      ?.substring(eq.length) || null;
  }

  has(name) { return this.get(name) !== null; }

  delete(name, opts = {}) { return this.set(name, '', { ...opts, days: -1 }); }

  getAll() {
    const out = {};
    document.cookie.split(';').forEach(c => {
      const [k, ...v] = c.trim().split('=');
      if (k) out[decodeURIComponent(k)] = decodeURIComponent(v.join('='));
    });
    return out;
  }

  clear(except = []) {
    Object.keys(this.getAll()).forEach(n => { if (!except.includes(n)) this.delete(n); });
    return true;
  }

  isEnabled() {
    try { this.set('__test', '1', { days: 1 }); const ok = this.has('__test'); this.delete('__test'); return ok; } catch { return false; }
  }

  /* ---------- consent helpers ---------- */
  getConsent() { return this.get('cookie_consent') === 'accepted'; }
  setConsent(yes = true) { return this.set('cookie_consent', yes ? 'accepted' : 'declined', { days: 365, path: '/', sameSite: 'strict' }); }

  /* =========================================================
   *  CSRF helpers
   * ========================================================= */
  get token() { return this._csrf; }
  set token(t) { this._csrf = t; this._updateMeta(t); }

  getHeaders() { return { [this.config.csrfHeaderName]: this._csrf }; }

  /* ---------- locate token (order documented above) ---------- */
  _locateToken() {
    return (typeof htmx !== 'undefined' && htmx.config?.antiForgery?.headerValue) ||
      document.querySelector(`meta[name="${this.config.csrfMetaName}"]`)?.content ||
      document.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
      this.get(this.config.csrfCookieName) ||
      this.get('X-CSRFToken') ||
      null;
  }

  _updateMeta(t) {
    const m = document.querySelector(`meta[name="${this.config.csrfMetaName}"]`);
    if (m) m.content = t;
  }

  _injectFallbackInput() {
    if (this._formInput) return;
    this._formInput = document.createElement('input');
    Object.assign(this._formInput, { type: 'hidden', name: 'csrfmiddlewaretoken', value: 'dummy' });
    document.body.appendChild(this._formInput);
  }

  /* =========================================================
   *  Unified request interception
   * ========================================================= */
  _installIntercepts() {
    /* 1. HTMX ------------------------------------------------ */
    if (typeof htmx !== 'undefined') {
      document.body.addEventListener('htmx:configRequest', (evt) => {
        const tok = this._tokenFromElement(evt.detail.elt) || this._csrf;
        if (tok) evt.detail.headers[this.config.csrfHeaderName] = tok;
      });
    }

    /* 2. Native fetch -------------------------------------- */
    const nativeFetch = window.fetch;
    window.fetch = async (resource, init = {}) => {
      const url = typeof resource === 'string' ? resource : resource.url;
      const opts = { ...init };
      opts.headers = new Headers(opts.headers);
      const tok = this._tokenFromElement(document.activeElement) || this._csrf;
      if (tok && !opts.headers.has(this.config.csrfHeaderName)) {
        opts.headers.set(this.config.csrfHeaderName, tok);
      }

      let resp = await nativeFetch(resource, opts);

      /* retry once on CSRF failure */
      if (resp.status === 403 && this.config.retryOnCsrfFailure && !opts._retried) {
        console.warn('🔄 CSRF failure – refreshing token');
        const ok = await this.refresh();
        if (ok) {
          opts.headers.set(this.config.csrfHeaderName, this._csrf);
          opts._retried = true;
          resp = await nativeFetch(resource, opts);
        }
      }
      return resp;
    };
  }

  /* grab token from hx-headers attribute if present */
  _tokenFromElement(el) {
    if (!el) return null;
    const raw = el.getAttribute('hx-headers');
    if (!raw) return null;
    try {
      const h = JSON.parse(raw);
      return h['x-csrftoken'] || h['X-CSRFToken'] || null;
    } catch { return null; }
  }

  /* ---------- refresh token from backend ---------- */
  async refresh() {
    try {
      const r = await fetch('/api/csrf/refresh/', { method: 'POST', credentials: 'include' });
      if (!r.ok) return false;
      const { token } = await r.json();
      this.token = token;
      return true;
    } catch (e) {
      console.error('❌ CSRF refresh failed:', e);
      return false;
    }
  }
}