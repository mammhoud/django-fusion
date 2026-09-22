/**
 * tools-web — Alpine application for the tools dashboard.
 * Handles: session bootstrap, sign-in modal, per-tool unlock gate, theme toggle.
 */
(function () {
  'use strict';

  const TOOLS = [
    { category: 'notes', name: 'Blinko', description: 'Self-hosted AI note tool. Sign up on first visit — no defaults.', path: '/notes/', internal: true },
    { category: 'documentation', name: 'Docs · Docus', description: 'Product and infrastructure guides, English + Arabic, full sidebar navigation.', path: '/docs/', internal: true },
    { category: 'database', name: 'Adminer', description: 'Lightweight database administration UI for PostgreSQL and friends.', path: '/adminer/', internal: true },
    { category: 'email', name: 'Mailpit', description: 'Email catcher — inspect outbound mail from staging and dev.', path: '/mailpit/', internal: true },
    { category: 'observability', name: 'Grafana', description: 'Dashboards on top of Prometheus metrics for the shared stack.', path: '/grafana/', internal: true },
    { category: 'automation', name: 'xyOps', description: 'Job scheduling, workflows, server monitoring, alerts, and incident tickets.', host: 'https://ops.structa.cloud', external: true },
    { category: 'workspace', name: 'Space', description: 'Cloud development environment — VS Code, terminals, AI agents.', host: 'https://space.structa.cloud', external: true },
    { category: 'proxy', name: 'Proxy health', description: 'tools-proxy liveness endpoint — plain-text 200, used by Traefik.', path: '/health/', internal: true },
  ];

  function api(url, opts) {
    return fetch(url, Object.assign({ credentials: 'same-origin' }, opts)).then(async (r) => {
      const data = await r.json().catch(() => ({}));
      return { ok: r.ok, status: r.status, data };
    });
  }

  document.addEventListener('alpine:init', () => {
    Alpine.data('toolsApp', () => ({
      tools: TOOLS,
      authenticated: false,
      sessionName: '—',
      showLogin: false,
      showUnlock: false,
      loginUsername: '',
      loginPassword: '',
      loginError: '',
      loginBusy: false,
      pendingTool: '',
      pendingToolName: '',
      unlockPassword: '',
      unlockError: '',
      unlockBusy: false,
      dark: false,

      init() {
        this.dark = document.documentElement.classList.contains('dark');
        this.refreshSession();
      },

      get bodyClass() {
        return { dark: this.dark };
      },

      refreshSession() {
        return api('/api/session').then(({ data }) => {
          this.authenticated = Boolean(data.authenticated);
          if (data.user && data.user.name) this.sessionName = data.user.name;
          if (this.authenticated) {
            this.showLogin = false;
          } else {
            this.showLogin = true;
          }
        });
      },

      async doLogin() {
        this.loginBusy = true;
        this.loginError = '';
        const body = new URLSearchParams({
          username: this.loginUsername,
          password: this.loginPassword,
        });
        const { ok, data } = await api('/api/login', { method: 'POST', body });
        this.loginBusy = false;
        if (ok && data.success) {
          this.loginPassword = '';
          await this.refreshSession();
        } else {
          this.loginError = data.error || 'Sign in failed';
        }
      },

      openTool(target, name) {
        if (!this.authenticated) {
          this.showLogin = true;
          return;
        }
        this.pendingTool = target;
        this.pendingToolName = name || target;
        this.unlockPassword = '';
        this.unlockError = '';
        this.showUnlock = true;
        // Focus the password input once the modal is visible.
        setTimeout(() => {
          const input = document.getElementById('unlockPassword');
          if (input) input.focus();
        }, 50);
      },

      async doUnlock() {
        this.unlockBusy = true;
        this.unlockError = '';
        const body = new URLSearchParams({
          password: this.unlockPassword,
          tool: this.pendingTool,
        });
        const { ok, data } = await api('/api/unlock', { method: 'POST', body });
        this.unlockBusy = false;
        if (ok && data.success) {
          this.showUnlock = false;
          this.unlockPassword = '';
          window.location.href = data.redirect || this.pendingTool;
        } else {
          this.unlockError = data.error || 'Wrong password';
        }
      },

      logout() {
        return api('/api/logout', { method: 'POST' }).then(() => {
          this.authenticated = false;
          this.sessionName = '—';
          this.showLogin = true;
        });
      },

      toggleTheme() {
        this.dark = !this.dark;
        document.documentElement.classList.toggle('dark', this.dark);
        try {
          localStorage.setItem('tools-theme', this.dark ? 'dark' : 'light');
        } catch (e) {}
      },
    }));
  });
})();
