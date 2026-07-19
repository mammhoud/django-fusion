# 05 — Customization Guide

> **Related:** All platform docs — see per-platform customization sections
> **Tags:** #customization #override #extend #config #templates

What you can safely customize across all Structa Cloud projects, and what you shouldn't touch.

---

## Customization Tag System

Every doc uses these tags:

| Tag | Meaning | Example |
|-----|---------|---------|
| 🟢 `customizable` | Safe to modify, extend, override | POS pages, Django site templates |
| 🔴 `not-customizable` | Core framework — use public API only | `django-fusion/`, `auth.rs`, `App.tsx` |
| 🟡 `delegate` | Extend through hooks/plugins | Add Tauri command, add Django app |
| 🔵 `template` | Template-level only | Edit SCSS, i18n JSON, HTML templates |
| ⚪ `config` | Env vars or settings only | `SUPERUSER_EMAIL`, `POSTGRES_HOST` |

---

## POS Customization

### 🟢 What You Can Change

| Area | How |
|------|-----|
| Page layouts | Edit `src/pages/*.tsx` freely |
| UI components | Edit `src/components/*.tsx` |
| Styles | Edit `src/styles/` SCSS files |
| Translations | Add keys to `src/i18n/*.json` |
| Invoice design | Edit `INVOICE_TEMPLATE` in `sidecar/server.py` |
| Invoice styles | Add entries to `DESIGN_CONFIGS` in `sidecar/server.py` |
| Seed data | Edit `src-tauri/src/bin/seed.rs` |
| New Tauri command | Create in `operations/` → register in `lib.rs` |
| New API endpoint | Add route in `sidecar/server.py` |

### 🔴 What You Should NOT Change

| Area | Why |
|------|-----|
| `auth.rs` (Rust) | Security-critical: bcrypt, session validation |
| `AuthContext.tsx` | Auth flow, session management |
| `App.tsx` | Routing structure, auth gate |
| `sidecar.rs` | Sidecar process lifecycle |
| WebSocket protocol | Frontend `chat.ts` depends on exact format |

### 🔵 Template-Level Changes

| Area | Customize via |
|------|-------------|
| CSS/SCSS | `src/styles/_variables.scss` |
| Translations | `src/i18n/en.json`, `fr.json`, `ar.json` |
| Invoice HTML | `INVOICE_TEMPLATE` string in `server.py` |

### ⚪ Config-Only

| Setting | Where |
|---------|-------|
| Superuser credentials | `projects/pos/.env` (`SUPERUSER_*`) |
| Sidecar host/port | `POS_SIDECAR_HOST`, `POS_SIDECAR_PORT` |
| SMTP settings | `SMTP_*` env vars |
| Database path | `DATABASE_URL` env var |

---

## Django Sites Customization

### 🟢 What You Can Change

| Area | How |
|------|-----|
| Site templates | Override in `projects/<site>/templates/` |
| Site settings | Edit `projects/<site>/settings.py` |
| Add Django app | Create in `projects/<site>/www/` |
| Add plugin | Create in `projects/<site>/plugins/` |
| Add site to registry | Edit `configs/settings/ENV/sites.yml` |
| Auth templates | Create `templates/auth/` → add to `TEMPLATE_MAP` |
| Social auth | Set `GOOGLE_OAUTH_*`, `FACEBOOK_OAUTH_*` env vars |

### 🔴 What You Should NOT Change

| Area | Why |
|------|-----|
| `django-fusion/` | Core framework — use its public API |
| `configs/base/` | Base settings — override in site settings |
| `www/` (core) | Shared app code |
| `ceptor-ai/` | AI assistant core |

### 🟡 Delegate Pattern

| Task | How |
|------|-----|
| Override a template | Copy from `assets/templates/` → edit in site `templates/` |
| Add a component | Create in `components/` → use `{% comp "name" %}` |
| Register include path | `register_include_path()` in `AppConfig.ready()` |
| Add a viewset | Extend `ModelViewset` in site `www/` |

### ⚪ Config-Only

| Setting | Where |
|---------|-------|
| Database name | `DB_NAME_CTC`, `DB_NAME_LMS`, `DB_NAME_VRESUME` env vars |
| Allowed hosts | Site `settings.py` or env |
| Debug mode | `DJANGO_DEBUG=0|1` env var |
| Secret key | `DJANGO_SECRET_KEY` env var |

---

## Infrastructure Customization

### 🟢 What You Can Change

| Area | How |
|------|-----|
| Add a Docker service | Create `docker-compose.custom.yml` in `applications/compose/` |
| Add SSL certificate | `manage-certs.sh bootstrap-acme` |
| Add site router | Edit `proxy/traefik/dynamic.yml` |
| Database backup scripts | Add to `applications/scripts/` |

### 🔴 What You Should NOT Change

| Area | Why |
|------|-----|
| `proxy/traefik/traefik.yml` | Entrypoint definitions — breaks routing |
| `databases/docker-compose.yml` | Core DB services |
| Proxy ACME flow | Stages must be followed in order |

---

## Quick Decision Matrix

| I want to... | Do this... | Tag |
|-------------|-----------|-----|
| Change a page layout | Edit `src/pages/*.tsx` | 🟢 |
| Change site colors | Edit SCSS variables | 🔵 |
| Add a new POS feature | Rust op → Tauri cmd → TS page | 🟡 |
| Override a site template | Copy to site `templates/` dir | 🟡 |
| Change auth behavior | ❌ Don't — use env vars or adapters | 🔴 |
| Add a Django site | Add to `sites.yml` → create directory | 🟢 |
| Change database schema | Create Diesel/Django migration | 🟢 |
| Add API endpoint | Add route in `server.py` | 🟢 |

---

→ [Back to Guides](README.md) | [Backend Env](../back-env/) | [Template Architecture](../libs/templates-architecture.md)
