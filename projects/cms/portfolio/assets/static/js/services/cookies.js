export class CookieManagerHandler {
  /** @type {{ csrfHeaderName: string, csrfCookieName: string, csrfMetaName: string, retryOnCsrfFailure: boolean, cookieDefaults: object }} */
  config = {
    csrfHeaderName:      'X-CSRFToken',
    csrfCookieName:      'csrftoken',
    csrfMetaName:        'csrf-token',
    retryOnCsrfFailure:  true,
    cookieDefaults:      { path: '/', sameSite: 'lax', days: 90 },
  };

  /** @param {Partial<CookieManagerHandler['config']>} [userConfig] */
  constructor(userConfig = {}) {
    Object.assign(this.config, userConfig);
    /** @type {string|null} */
    this._csrf = null;
    this._installIntercepts();
  }

  // ── Lifecycle ────────────────────────────────────────────────

  async init() {
    this._csrf = this._locateToken();
    if (!this._csrf) {
      console.warn('[CookieManagerHandler] CSRF token not found');
    }
    return this;
  }

  // ── Cookie API ───────────────────────────────────────────────

  /**
   * @param {string} name
   * @param {string} value
   * @param {object} [opts]
   */
  set(name, value, opts = {}) {
    const cfg = { ...this.config.cookieDefaults, ...opts };
    let c = `${encodeURIComponent(name)}=${encodeURIComponent(value)}`;
    if (cfg.days) {
      c += `; expires=${new Date(Date.now() + cfg.days * 864e5).toUTCString()}`;
    }
    ['path', 'domain', 'sameSite'].forEach(k => { if (cfg[k]) c += `; ${k}=${cfg[k]}`; });
    if (cfg.secure)   c += '; secure';
    if (cfg.httpOnly) c += '; httponly';
    document.cookie = c;
    return true;
  }

  /** @param {string} name @returns {string|null} */
  get(name) {
    const eq = `${encodeURIComponent(name)}=`;
    return document.cookie.split(';')
      .map(p => p.trim())
      .find(p => p.startsWith(eq))
      ?.substring(eq.length) ?? null;
  }

  /** @param {string} name @returns {boolean} */
  has(name) { return this.get(name) !== null; }

  /** @param {string} name @param {object} [opts] */
  delete(name, opts = {}) { return this.set(name, '', { ...opts, days: -1 }); }

  /** @returns {Record<string, string>} */
  getAll() {
    return Object.fromEntries(
      document.cookie.split(';')
        .map(c => c.trim().split('='))
        .filter(([k]) => k)
        .map(([k, ...v]) => [decodeURIComponent(k), decodeURIComponent(v.join('='))])
    );
  }

  /** @param {string[]} [except=[]] */
  clear(except = []) {
    Object.keys(this.getAll()).forEach(n => { if (!except.includes(n)) this.delete(n); });
  }

  isEnabled() {
    try {
      this.set('__test', '1', { days: 1 });
      const ok = this.has('__test');
      this.delete('__test');
      return ok;
    } catch { return false; }
  }

  // ── Consent helpers ──────────────────────────────────────────

  getConsent() { return this.get('cookie_consent') === 'accepted'; }
  setConsent(yes = true) {
    return this.set('cookie_consent', yes ? 'accepted' : 'declined', { days: 365, sameSite: 'strict' });
  }

  // ── CSRF API ─────────────────────────────────────────────────

  get token() { return this._csrf; }
  set token(t) {
    this._csrf = t;
    const m = document.querySelector(`meta[name="${this.config.csrfMetaName}"]`);
    if (m) m.content = t;
  }

  /** @returns {Record<string, string>} */
  getHeaders() { return { [this.config.csrfHeaderName]: this._csrf }; }

  /** Refresh CSRF token from backend */
  async refresh() {
    try {
      const r = await fetch('/api/csrf/refresh/', { method: 'POST', credentials: 'include' });
      if (!r.ok) return false;
      const { token } = await r.json();
      this.token = token;
      return true;
    } catch (e) {
      console.error('[CookieManagerHandler] CSRF refresh failed:', e);
      return false;
    }
  }

  // ── Private ──────────────────────────────────────────────────

  _locateToken() {
    return (typeof htmx !== 'undefined' && htmx.config?.antiForgery?.headerValue)
      || document.querySelector(`meta[name="${this.config.csrfMetaName}"]`)?.content
      || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value
      || this.get(this.config.csrfCookieName)
      || null;
  }

  /** Extract CSRF from hx-headers attribute if present */
  _tokenFromElement(el) {
    if (!el) return null;
    const raw = el.getAttribute?.('hx-headers');
    if (!raw) return null;
    try {
      const h = JSON.parse(raw);
      return h['x-csrftoken'] ?? h['X-CSRFToken'] ?? null;
    } catch { return null; }
  }

  _installIntercepts() {
    // 1. HTMX
    if (typeof htmx !== 'undefined') {
      document.body.addEventListener('htmx:configRequest', (evt) => {
        const tok = this._tokenFromElement(evt.detail.elt) ?? this._csrf;
        if (tok) evt.detail.headers[this.config.csrfHeaderName] = tok;
      });
    }

    // 2. Native fetch — wrap once
    const nativeFetch = window.fetch;
    window.fetch = async (resource, init = {}) => {
      const opts = { ...init, headers: new Headers(init.headers) };
      const tok = this._tokenFromElement(document.activeElement) ?? this._csrf;
      if (tok && !opts.headers.has(this.config.csrfHeaderName)) {
        opts.headers.set(this.config.csrfHeaderName, tok);
      }

      let resp = await nativeFetch(resource, opts);

      // Retry once on CSRF failure
      if (resp.status === 403 && this.config.retryOnCsrfFailure && !opts._retried) {
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
}
