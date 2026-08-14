# Pro Edition — Local Completion Record

**Canonical product:** `projects/formints/formint-pro/`  
**Legacy aliases:** `pos-full`, `pos-solo`, and `formint/` are compatibility names only.

## Current architecture

Pro is a merged Django/Ninja + Astro/Tauri product. Django is the primary local
API and data authority; the Robyn/django-bolt runner remains an optional legacy
compatibility path for desktop packaging and is not required by the normal
Django checks.

```text
frontend/ (Astro + Alpine + HTMX)
  → server/ (Django ORM + Django Ninja/ninja-extra + django-fusion + Unfold)
  → server/restaurant.db (SQLite in local development)

optional server.py / bolt_api.py compatibility runner → legacy :8766 contract
src-tauri/ → desktop shell
```

The canonical server boundary is `server/`, not the retired `sidecar/` or
`formint/` paths. The Django model app is `pos_full`; `formint.models` re-exports
that single model layer.

## Completed local work

- [x] Reconciled `projects/formints/formint-pro/README.md` with the actual
  Django-first architecture and optional legacy runner.
- [x] Reconciled the Pro Makefile descriptions and retained the explicit
  compatibility build targets.
- [x] Added Standard-parity `Currency` and `TaxProfile` models, admin entries,
  migration `server/models/migrations/0002_currency_taxprofile.py`, schemas,
  and Ninja CRUD routes at `/api/v1/currencies/` and
  `/api/v1/tax-profiles/`.
- [x] Added read-only CSV/JSON exports at
  `/export/{products|sales|customers|inventory}.csv` and
  `/export/<resource>.csv?format=json`.
- [x] Added Pro regression tests for the money/tax models, OpenAPI route
  registration, and export response contract.
- [x] Preserved the existing scoped API-key enforcement for the legacy Robyn
  `/api/v1/` runner. The Django test/API road remains session/API-gateway
  compatible and does not silently claim Robyn middleware is active there.

## Verification

| Gate | Result |
|---|---|
| Pro frontend `./node_modules/.bin/astro check` | PASS — 0 errors, existing hints only |
| Pro Python syntax compilation for changed modules | PASS |
| Pro `make check` | BLOCKED — `server/.venv/bin/python3` is absent in this checkout |
| Pro `make test` | BLOCKED — same missing local Python environment |

After the repository owner provisions the existing Pro environment, run:

```bash
cd projects/formints/formint-pro
make check
make test
```

No database migration or seed command was run by this completion pass.

## Reference parity

Pro now exposes the Standard money/tax/export surfaces in its own canonical
Django API while retaining its larger CRM, sync, fusion, and admin surface.
Cloud remains the hosted multi-tenant implementation in
`projects/formints/formint-cloud/`; Standard remains the standalone Rust/Diesel
implementation in `projects/formints/formint-standard/`.

External publishing, release tags, and git commits remain owner actions.
