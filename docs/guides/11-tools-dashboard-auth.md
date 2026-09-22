---
title: Tools Dashboard & Auth
description: Self-hosted internal tools portal — dashboard listing, sign-in modal, per-tool unlock gate, session cookies, and API endpoints.
navigation:
  title: Tools Dashboard & Auth
  icon: i-lucide-wrench
object:
  type: "guide"
  id: "guide.tools-dashboard-auth"
attributes:
  source_path: "guides/11-tools-dashboard-auth.md"
  canonical_route: "/docs/en/guides/11-tools-dashboard-auth"
  source_of_truth: "repository-markdown"
  audience: "engineers, operators, and coding agents"
  status: "maintained"
  owner: "workspace"
tags:
  - structa-cloud
  - tools
  - auth
links:
  - label: "Deploy"
    to: "/guides/05-deploy"
    icon: "i-lucide-rocket"
  - label: "Reverse Proxy"
    to: "/guides/05-deploy"
    icon: "i-lucide-network"

# Tools Dashboard & Auth

> **Owner:** Workspace tooling · **Scope:** internal portal
> **Source path:** `application/tools/tools-web/`
> **Last updated:** 2026-09-12

---

## Overview

This service provides:

1. **Tools dashboard** at root — lists every self-hosted tool under application/tools/
2. **Sign-in modal** — authentication happens in a modal on the dashboard
3. **Per-tool unlock gate** — clicking a tool asks for a shared unlock password before navigating
4. **Theme toggle** — light/dark switch persisted in browser storage, defaults to system preference
5. **Session management** — signed HTTP-only cookies (HMAC)
6. **API endpoints** — login, logout, session check, unlock validation

The frontend is Alpine.js + htmx (vendored locally under `public/vendor/`) with zero build step.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  tools.structa.cloud (Traefik TLS)                          │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  tools-proxy (Nginx)                                        │
│  ├── / → tools-web:4321 (dashboard)                         │
│  ├── /login → tools-web:4321 (redirects to /)               │
│  ├── /api/* → tools-web:4321 (auth + unlock API)            │
│  ├── /adminer/ → adminer:8080                               │
│  ├── /mailpit/ → mailpit:8025                               │
│  ├── /grafana/ → grafana:3000                               │
│  ├── /docs/ → docus:3000                                    │
│  └── /notes/ → blinko:1111                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## User Configuration

Users are defined in `application/tools/tools-web/users.yml`:

```yaml
users:
  - username: "admin"
    password_hash: "$2a$10$..."  # bcrypt hash of "admin"
    role: "admin"
    name: "Administrator"
    email: "admin@structa.cloud"
    enabled: true

  - username: "supervisor"
    password_hash: "$2a$10$..."  # bcrypt hash of "supervisor"
    role: "supervisor"
    name: "Supervisor"
    email: "supervisor@structa.cloud"
    enabled: true
```

### Default Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin | admin |
| supervisor | supervisor | supervisor |

### Generating Password Hashes

```bash
cd application/tools/tools-web
node -e "console.log(require('bcryptjs').hashSync('your-password', 10))"
```

Update `users.yml` with the new hash and rebuild the Docker image.

---

## Unlock Password (`TOOLS_UNLOCK_PASSWORD`)

Every tool card asks for a **shared unlock password** before navigating. The
password comes from the `TOOLS_UNLOCK_PASSWORD` environment variable (see
`application/tools/.env.example`), NOT from `users.yml`.

```bash
# Generate a strong random value
openssl rand -base64 18 | tr -d '/+=' | head -c 20
```

Add it to the repo-root `.env` (or `application/tools/.env`) and redeploy:

```env
TOOLS_UNLOCK_PASSWORD=<random value>
TOOLS_SESSION_SECRET=<random value>   # optional; signs session cookies
```

If `TOOLS_UNLOCK_PASSWORD` is unset, `/api/unlock` returns 500 with a clear
message and the unlock modal shows "not configured".

---

## Design System

**Swiss Industrial Print** — consistent with `tools-proxy` Nginx landing page:
- Matte paper (`#F4F4F0`) + carbon ink (`#0A0A0A`) (dark theme swaps to `#12120F` / `#EDEBE6`)
- Aviation red accent (`#E61919`, brighter `#FF3B30` in dark mode)
- Zero border-radius
- Hard offset shadows (4px × 4px)
- Mono uppercase telemetry labels
- BEM-style component classes

### Fonts
- **Display:** Archivo Black / Arial Black
- **Sans:** Inter
- **Mono:** IBM Plex Mono

---

## API Endpoints

### `POST /api/login`
Authenticate user and create a signed session cookie.

**Request:**
```http
Content-Type: application/x-www-form-urlencoded

username=admin&password=admin
```

**Response (200):**
```json
{
  "success": true,
  "user": { "username": "admin", "role": "admin", "name": "Administrator", "email": "admin@structa.cloud" }
}
```

**Response (401):**
```json
{ "error": "Invalid username or password" }
```

### `POST /api/unlock`
Validate the shared unlock password for a tool and set a short-lived unlock
cookie. Returns the redirect target (the tool's path or host).

**Request:**
```http
Content-Type: application/x-www-form-urlencoded

password=<TOOLS_UNLOCK_PASSWORD>&tool=/notes/
```

**Response (200):**
```json
{ "success": true, "redirect": "/notes/" }
```

**Response (401):**
```json
{ "error": "Incorrect password for this tool" }
```

### `POST /api/logout`
Clear session + unlock cookies.

**Response (200):**
```json
{ "success": true }
```

### `GET /api/session`
Check current session.

**Response (200):**
```json
{
  "authenticated": true,
  "user": { "username": "admin", "role": "admin", "name": "Administrator", "email": "admin@structa.cloud" },
  "unlocked": false
}
```

Or if not authenticated:
```json
{ "authenticated": false, "unlocked": false }
```

---

## Session Management

- **Session cookie:** `tools_auth_session` — signed payload (`base64url(JSON).hmac`)
- **Unlock cookie:** `tools_unlocked` — signed `ok` marker, 12-hour expiry
- **Storage:** HTTP-only, SameSite=Lax, Secure in production (TLS at Traefik)
- **Expiry:** 7 days (session)
- **Signature:** HMAC-SHA256 with `TOOLS_SESSION_SECRET` (falls back to `TOOLS_UNLOCK_PASSWORD`)

---

## Deployment

### Local run
```bash
cd application/tools/tools-web
npm install
TOOLS_UNLOCK_PASSWORD=yourpass node server.mjs
# → http://localhost:4321
```

### Docker
```bash
# From repository root
docker compose -f application/tools/docker-compose.yml build tools-web
docker compose -f application/tools/docker-compose.yml up -d tools-web
```

### Networks
- `traefik-net` — Traefik routing
- `common` — Inter-container communication

### Health Check
```bash
wget -qO- http://localhost:4321/health/   # → healthy
```

---

## Project Structure

```
application/tools/tools-web/
├── server.mjs                  # Vanilla Node HTTP server (static + API)
├── public/
│   ├── index.html              # Dashboard + sign-in/unlock modals (Alpine)
│   ├── app.js                  # Alpine component (session, unlock, theme)
│   ├── styles.css              # Swiss Industrial Print + dark theme
│   ├── logo.svg
│   └── vendor/
│       ├── htmx.min.js         # Vendored htmx 2.x
│       └── alpine.min.js       # Vendored Alpine.js 3.x
├── users.yml                   # Sign-in accounts (bcrypt)
├── package.json                # bcryptjs + js-yaml only
└── Dockerfile                  # node:22-alpine, no build step
```

---

## Adding New Tools to Dashboard

Edit the `TOOLS` array in **both** `server.mjs` and `public/app.js` (they are
kept in sync with the nginx routes):

```javascript
{
  category: 'category-name',
  name: 'Display Name',
  description: 'Tool description',
  path: '/tool-path/',          // for internal tools
  // OR
  host: 'https://external.com', // for external tools
  external: true                // if external
}
```

---

## Security Notes

1. **HTTPS only** — cookies are `Secure`, requires TLS termination at Traefik
2. **HTTP-only cookies** — prevents XSS token theft
3. **Signed sessions** — HMAC-SHA256 prevents cookie forgery
4. **bcrypt** — passwords never stored in plaintext
5. **Shared unlock password** — one gate for all tools, stored only in env
6. **No basic auth** — nginx `auth_basic` removed; auth handled by tools-web

---

## Troubleshooting

### Login fails
- Verify `users.yml` has correct bcrypt hashes
- Check `users.yml` is copied to the Docker image
- Ensure `NODE_ENV=production`

### Unlock says "not configured"
- `TOOLS_UNLOCK_PASSWORD` is missing in the container environment — add it to
  `.env` and redeploy (`make deploy-tools` / compose up -d tools-web)

### Session not persisting
- Verify `Secure` cookie flag matches HTTPS
- Check `SameSite=Lax` allows cross-subdomain if needed
- Confirm Traefik passes `X-Forwarded-Proto` header

### Dashboard loads but modals don't work
- Confirm `public/vendor/alpine.min.js` and `htmx.min.js` are present
  (they are baked into the image at build time)

---

## Related Files

| File | Purpose |
|------|---------|
| `application/tools/tools-web/users.yml` | User accounts |
| `application/tools/tools-web/server.mjs` | HTTP server + auth/unlock API |
| `application/tools/nginx/default.conf.template` | Nginx routing |
| `application/tools/docker-compose.yml` | Service orchestration |
| `application/tools/tools-web/Dockerfile` | Container build |
| `application/tools/tools-web/docker-compose.yml` | tools-web service definition |
| `application/tools/.env.example` | `TOOLS_UNLOCK_PASSWORD` reference |

---

## Remarks & Notes

- Replaced the Astro SSR app (`astro-tools`) with a zero-framework Node server
  in 2026-08-26; `application/tools/astro-tools/` was removed.
- Frontend is Alpine.js + htmx with no build step — edit `public/` directly.
- Sign-in moved from a dedicated `/login` page into a modal on the dashboard.
- Per-tool unlock password gate added: opening any tool requires
  `TOOLS_UNLOCK_PASSWORD` from the environment.
- Theme toggle persists in `localStorage` (`tools-theme`) and defaults to the
  OS preference; dark tokens defined in `styles.css` under `.dark`.

<!-- AI-generated: review needed -->
