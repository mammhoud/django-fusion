# 📚 Guides — Step-by-Step Tutorials

Numbered walkthroughs for common tasks across the Structa Cloud monorepo.

> 💡 **New here?** Start with [01 — Setup](01-setup.md) to get everything running locally.

## Use Cases

### 1. First-Time Development Setup (`01-setup.md`)
- **Purpose:** Clone the monorepo, init submodules, install deps (Python, Rust, Node), configure env files, start infrastructure (PostgreSQL, Redis, Traefik)
- **Key traits:** Zero-to-running in one guide; covers both POS desktop app and Django sites; includes common-first-time troubleshooting table

### 2. Authentication Configuration (`02-auth.md`)
- **Purpose:** Set up POS superuser login (env-vars or SMTP codes), configure Django allauth with HTMX fragments, enable OAuth providers (Google, Facebook), activate TOTP 2FA / WebAuthn
- **Key traits:** Covers desktop and web auth models; adapter-based `TEMPLATE_MAP` lets you add auth views without modifying core code

### 3. POS Application Development (`03-dev.md`)
- **Purpose:** Understand the three-layer architecture (React → Rust/Tauri → Python/Sanic sidecar), run dev workflow, add features following the Rust op → Tauri command → TS page pattern
- **Key traits:** Full 25-module catalog with customization tags; sidecar testable standalone with `--db` flag; scripts for i18n, screenshots, checksums

### 4. Production Deployment (`04-deploy.md`)
- **Purpose:** Deploy Django sites behind Traefik with Let's Encrypt SSL (Cloudflare DNS-01), run health checks, manage DB backups/restores, troubleshoot production issues (502, SSL expiry, 404s)
- **Key traits:** Staged SSL rollout (staging → production → cleanup); step-by-step service deployment (databases → proxy → sites) plus `make deploy` shortcut

### 5. Customization & Extension (`05-customize.md`)
- **Purpose:** Determine what's safe to change (🟢), extensible via hooks (🟡), template-level (🔵), config-only (⚪), or core infrastructure (🔴)
- **Key traits:** Decision matrix covers all layers; consistent tag system re-used across every section of the docs

---

## Guide Index

| # | Guide | Covers | Time |
|---|-------|--------|------|
| [01](01-setup.md) | **First-Time Setup** | Clone, install deps, env files, start services | ~5 min |
| [02](02-auth.md) | **Authentication** | POS superuser, Django allauth, OAuth, MFA | ~10 min |
| [03](03-dev.md) | **POS Development** | Architecture, workflow, adding features, scripts | ~15 min |
| [04](04-deploy.md) | **Deployment** | Docker, SSL, Traefik, databases, troubleshooting | ~10 min |
| [05](05-customize.md) | **Customization** | What's safe to change (tag system + decision matrix) | ~10 min |

## After the Guides

- 📖 [Platform reference docs](../) — detailed per-language documentation
- 🔧 [Backend environment setup](../back-env/) — env vars for all projects
- 🧪 [Testing overview](../tests/) — run tests across all projects
- 🗄️ [Database guide](../databases/) — schema, migrations, connections

---

→ [Back to docs](../)
