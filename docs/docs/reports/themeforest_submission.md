# VResume — ThemeForest Submission Guide & Checklist 🚀

This document outlines the organization and requirements for submitting **VResume** to ThemeForest. It ensures that all assets, documentation, and code standards meet Envato's quality guidelines.

---

## 📁 Package Organization

The final submission package should be organized as follows:

```text
VResume-Package/
├── 📄 README.md                (Main package overview)
├── 📂 documentation/           (Comprehensive user & dev guide)
├── 📂 licensing/               (MIT and other asset licenses)
├── 📂 source/                  (The actual Django/Wagtail source code)
│   ├── v1/                     (Core application)
│   ├── compose/                (Docker configurations)
│   ├── Makefile                (Automation shortcuts)
│   └── docker-compose.yml      (Deployment entry point)
└── 📂 themes/                  (Exported static theme versions)
```

---

## 🏗️ Technical Standards

### 1. Code Quality
- [x] **Python (Django/Wagtail)**: Follows PEP 8 standards (verified with Ruff).
- [x] **SCSS/CSS**: BEM naming convention used throughout. No hardcoded colors.
- [x] **JavaScript**: Modular structure, no global namespace pollution, documented with JSDoc.
- [x] **HTML**: Semantic HTML5, accessible (WCAG 2.1 AA compliant).

### 2. Configuration & Port Awareness
- [x] Unified configuration using `Dynaconf` and `Pydantic`.
- [x] Environment-aware ports (default `5080`, configurable via `.env`).
- [x] Dynamic `CSRF_TRUSTED_ORIGINS` and `ALLOWED_HOSTS` based on current port/domain.

### 3. Security Hardening
- [x] SSL/HTTPS support integrated.
- [x] HSTS, X-Frame-Options, and Content-Type-Sniffing enabled.
- [x] Secure cookie management (HttpOnly, Secure flags).
- [x] Rate limiting for login and API endpoints.

---

## 🐳 Docker Infrastructure

The submission includes two proxy options to ensure a `200 OK` response in various environments:

| Option | Proxy | Best For | Profile |
|--------|-------|----------|---------|
| **Option 1** | **Nginx** | Enterprise deployments, custom SSL | `proxy-nginx` |
| **Option 2** | **Caddy** | Rapid setup, automatic SSL | `proxy-caddy` |

**Quick Command:**
```bash
# Start with Nginx
docker compose --profile proxy-nginx up -d

# Start with Caddy
docker compose --profile proxy-caddy up -d
```

---

## 🔍 Search & Form Handling ("q" Enhancement)

The search functionality (`name="q"`) has been enhanced to handle multiple entries:
- **AND Logic**: Multiple terms (e.g., "django python") are split and filtered to ensure results contain all terms.
- **Cross-Field Search**: Searches across Title, Introduction, Excerpt, and Body.
- **HTMX Powered**: Instant results without full page reloads.

---

## 🎨 Asset Reorganization

The Themeforest assets are organized in the `v1/assets/` directory:
- `static/styles/`: Organized BEM SCSS partials.
- `static/js/`: Modularized components (Cookie Manager, Theme Switcher, etc.).
- `media/`: Placeholder-free images generated specifically for the theme.

---

## ✅ Final Checklist before Submission

- [ ] Run `make test` and ensure 100% pass rate.
- [ ] Verify `DEBUG=False` in `production` environment.
- [ ] Ensure all sensitive keys in `v1/.env` are placeholders.
- [ ] Check documentation for any broken links.
- [ ] Validate that both Nginx and Caddy proxies return `200 OK` on the home page.

---

**Status:** ✅ Ready for Final Review
**Version:** 1.1.0
