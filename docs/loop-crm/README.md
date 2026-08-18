# Loop-CRM

> Unified sales + marketing platform (Twenty DNA + Postiz DNA) on
> Django + django-fusion. Canonical product location:
> `projects/loop-crm/`.

<!-- AI-generated: review needed -->

## Product Docs (canonical, in-repo)

| Doc | Path | Covers |
|-----|------|--------|
| **Design System** | [`projects/loop-crm/docs/DESIGN_SYSTEM.md`](../../projects/loop-crm/docs/DESIGN_SYSTEM.md) | Industrial-brutalist / tactical telemetry design tokens, typography, layout, components. |
| **Setup & Build** | [`projects/loop-crm/docs/SETUP_AND_BUILD.md`](../../projects/loop-crm/docs/SETUP_AND_BUILD.md) | Step-by-step startup, backend + frontend setup, build and run commands. |

## Env & Config

| Doc | Path | Covers |
|-----|------|--------|
| **Env contract** | [`projects/loop-crm/configs/`](../../projects/loop-crm/configs/) | The 56-variable environment catalog + validator (`make validate-env`). |
| **Env example** | [`projects/loop-crm/.env.example`](../../projects/loop-crm/.env.example) | Copy-paste environment template. |
| **Site identity** | [`projects/loop-crm/Env/_site.yml`](../../projects/loop-crm/Env/_site.yml) | Domain, allowed hosts, per-environment overrides. |

## Commands

```bash
# From projects/loop-crm
make dev               # Astro frontend dev server
make backend-dev       # Django dev server (backend Makefile)
make check             # frontend typecheck
make backend-check     # Django system checks
make backend-test      # Django tests
make backend-migrate   # makemigrations + migrate
make backend-seed      # seed demo workspace (demo@loop.dev / demo-pass-123)
make validate-env      # check env against the configs contract
make i18n              # makemessages + compilemessages (en, ar)

# Through Nx (requires root npm install)
make nx-check          # npx nx run loop-crm:check
npx nx run loop-crm:backend-test
```

## Architecture Notes

- **Render-first:** Django renders the data screens (fusion tables/forms);
  the Astro shell proxies `/fragments`, `/api`, `/bolt`, `/accounts`.
- **API roads:** `/bolt/tables/{resource}` (canonical, JWT, needs django_bolt)
  and `/api/v1/tables/{resource}/` (compat, session cookie).
- **Redis-free dev:** a RESP PING probe decides; DEBUG falls back to LocMem
  cache + in-memory channel layer when Redis is missing or another app squats
  the port.
- **i18n:** `LocaleMiddleware` + `LANGUAGES` (en/ar) + `LOCALE_PATHS`; models
  use `gettext_lazy`. See `docs/ai/templates-and-request-flows.md` for the
  translation flow.

## Remarks & Notes

- On dev machines where the Kiro app holds ports 8000/6379, run the backend on
  `PORT=8001` and the Redis probe handles the rest.
- The session changelog for recent Loop-CRM work lives at
  [`docs/changelogs/session-2026-08-18.md`](../changelogs/session-2026-08-18.md).
