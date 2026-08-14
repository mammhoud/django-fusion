# `tests/` — Workspace Test Guidance

Read the root `AGENTS.md` first. This directory contains cross-product tests and
fixtures; product-local tests remain beside their product code.

## Layout

```text
tests/
├── unit/                    # isolated models, services, auth, tasks, POS tests
├── integration/             # multi-app/site/auth workflows
├── http/                    # Django/TestClient/API and rendering checks
├── selenium/                # browser and site smoke suites
├── selenium-detailed/       # detailed user-flow/browser coverage
├── ci/                      # CI-oriented auth/admin/assets/email suites
├── websites/                # cross-site settings, URLs, and smoke checks
├── core/                    # shared invariants, cache/events/config checks
├── docker/                  # image/Compose validation
├── email/                   # email delivery/integration tests
├── apps/                    # shared app behavior tests
├── fixtures/                # JSON dumps, categorized by product/model/env
├── assets/                  # test templates and content fixtures
├── scripts/                 # fixture/data/production helpers
├── conftest.py              # workspace pytest configuration
└── settings.py              # test Django settings
```

## Test selection

```bash
# Workspace Python tests
uv run pytest tests/
uv run pytest tests/unit/ -q
uv run pytest tests/integration/ -q
uv run pytest tests/http/ -q

# Useful focused examples
uv run pytest tests/test_domain_urls.py -q
uv run pytest tests/websites/ -q
uv run pytest tests/core/ -q

# Product-local suites
cd projects/precis/main && uv run pytest backend/tests/
cd projects/precis/landi/backend && make test
cd projects/formints/formint && make test
cd libs/django-fusion && uv run pytest
```

For browser suites, use the product's documented Playwright/Selenium command.
Do not assume Chrome/Chromium is installed in every agent environment.

## Test categories and expectations

- **Unit:** deterministic, isolated, and fast; mock external providers only at
  the boundary.
- **Integration:** exercise real Django routing, middleware, models, and
  database behavior where practical.
- **HTTP:** assert response status, headers, content contracts, and user-visible
  behavior rather than private implementation details.
- **Browser:** cover auth, navigation, forms, translations, assets, and critical
  product flows from a user's perspective.
- **Contract/parity:** keep API envelopes, HTMX headers, WebSocket frames,
  render-mode behavior, and frontend/backend route names synchronized.
- **Deployment:** validate configuration and health without mutating production
  resources unless the test explicitly runs in an isolated environment.

## Fixtures and database safety

Fixtures are organized under `fixtures/` by product, model, environment, and
purpose. Before adding or loading one:

1. Read the fixture README and the relevant loader script.
2. Confirm the selected Django settings/database and site identity.
3. Prefer temporary SQLite/test databases for local tests.
4. Do not run production fixture loaders, restores, or destructive cleanup
   against a shared database without explicit user instruction.
5. Keep secrets, real user data, tokens, and credentials out of fixtures.

When changing models or Wagtail page structures, update migrations, fixture
schemas/loaders, and invariant tests together.

## Test conventions

- Use `pytest`/`pytest-django` configuration from the active workspace; do not
  silently override `DJANGO_SETTINGS_MODULE` in a shared test module.
- Use `rg` to find existing fixtures, markers, URL names, and test helpers.
- Prefer existing `conftest.py` fixtures and TestClient utilities.
- Mark slow/integration/browser tests using the established markers.
- Keep tests independent and order-insensitive.
- When a test starts a server or browser, make cleanup reliable and use a
  unique port/session where the local runner permits it.

## Validation checklist

For a code change, run the narrowest affected test first, then the product
check. For a shared framework or contract change, run both the library tests and
at least one consuming product test. Report skipped tests with the reason
(missing service, browser, database, or dependency) rather than claiming the
suite passed.
