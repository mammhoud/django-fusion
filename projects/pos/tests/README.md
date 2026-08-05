# POS — Unified Test Directory

This directory consolidates test orchestration and NEW tests for the POS project (mini, solo, full editions). Python sidecar tests run from their original locations via wrapper scripts (see note below).

> **Note on Python test location**: The POS sidecar tests (`pos-full/sidecar/tests/`, `pos-solo/sidecar/tests/`) must run from their original directories because the root `pyproject.toml` sets `DJANGO_SETTINGS_MODULE = "tests.settings"` which `pytest-django` auto-discovers. Running pytest from any subdirectory triggers Django configuration with the root test settings, which reference a `plugins` module that doesn't exist in the POS project. The wrapper scripts in `py/full/` and `py/solo/` `cd` to the original locations and `unset DJANGO_SETTINGS_MODULE` to avoid this conflict.

## Directory Structure

```
tests/
├── README.md              ← this file
├── run-all.sh             ← unified orchestration runner
├── py/                    ← Python sidecar test runners (wrapper scripts)
│   ├── full/              ← wrapper: runs pos-full/sidecar/tests/ via pytest
│   │   └── run.sh
│   ├── solo/              ← wrapper: runs pos-solo/sidecar/tests/ via pytest
│   │   └── run.sh
│   └── formint/           ← wrapper: runs formint-pos backend tests via manage.py
│       └── run.sh
├── js/                    ← JS/TS frontend tests (vitest config)
│   ├── vitest.config.ts   ← shared vitest config (discovers pos-full/src/test/ + formint-pos frontend)
│   └── setup-global.ts    ← global test setup (polyfills, mocks)
├── selenium/              ← NEW: Browser-based admin panel tests
│   ├── conftest.py        ← Selenium driver + auth fixture
│   ├── test_admin_login.py
│   ├── test_admin_dashboard.py
│   ├── test_admin_crud.py
│   └── formint/           ← formint-pos Unfold admin suite (own conftest + pytest.ini)
│       ├── conftest.py
│       ├── pytest.ini
│       └── test_formint_admin.py
├── api/                   ← NEW: Node.js REST API endpoint tests
│   ├── test_products.mjs
│   └── test_sales.mjs
└── run-all.sh             ← Single command to run everything
```

## Quick Start

```bash
# Run all test suites
bash tests/run-all.sh

# Run only Python sidecar tests (fastest)
bash tests/run-all.sh py

# Run only JS vitest tests
bash tests/run-all.sh js

# Run API endpoint tests (requires sidecar on :8000)
bash tests/run-all.sh api

# Run selenium admin panel tests (requires Chrome + sidecar on :8000)
bash tests/run-all.sh selenium

# Skip slow tests (selenium + API)
bash tests/run-all.sh --quick
```

## Test Suite Details

### Python Sidecar Tests (`py/`)

| Suite | Edition | Tests | Run Command |
|-------|---------|-------|-------------|
| `py/full/` | pos-full | 53 (server + webhook + data_sync) | `bash tests/py/full/run.sh` |
| `py/solo/` | pos-solo | 155 (unified API models) | `bash tests/py/solo/run.sh` |
| `py/formint/` | formint-pos | 35 (ninja CRUD + HTMX + render-mode + admin) | `bash tests/py/formint/run.sh` |

Each `run.sh` wrapper:
1. `cd`s to the original sidecar directory (`pos-full/sidecar/` or `pos-solo/sidecar/`)
2. Runs `unset DJANGO_SETTINGS_MODULE` to avoid pytest-django auto-configuration
3. Invokes `python3 -m pytest tests/` with optional filter arguments

### JS Frontend Tests (`js/`)

The vitest config (`js/vitest.config.ts`) discovers tests from `pos-full/src/test/`
(identical copies exist in all 3 editions) **plus the formint-pos merged package**
frontend contract tests (`formint-pos/frontend/src/**/*.test.ts`). The config's
`server.fs.allow` includes the whole `projects/pos` root so out-of-edition tests
load correctly. New tests can be added directly under `tests/js/`.

### Selenium Admin Tests (`selenium/`) 🆕

Browser-based tests for the Unfold admin dashboard. Covers:
- Login page rendering and auth flow
- Dashboard KPI cards, charts, and tables
- Model list pages (Products, Customers, Sales, etc.)

The `formint/` subdirectory adds formint-pos admin coverage (login, loyalty
KPI cards, charts, sidebar links, loyalty/settings changelists). It ships its
own `pytest.ini` so the repo-root pytest-django config is not loaded.

Requires:
- Chromium / Chrome installed
- `python3 -m pip install selenium webdriver-manager`
- pos-full sidecar running on `:8000` with superuser seeded (formint suite:
  formint-pos backend on `:8000` with `FORMINT_ADMIN_*` superuser seeded)

### API Endpoint Tests (`api/`) 🆕

Lightweight Node.js scripts that test the REST API directly. Require:
- Node.js 18+ (for global `fetch`)
- pos-full sidecar running on `:8000`

## CI Integration

The `run-all.sh --quick` mode runs Python + JS tests and is suitable for CI pipelines.
Selenium and API tests can be run nightly or on demand.

## Known Issues

- **pos-full tests (49 failures, 6 errors)**: Pre-existing database migration issue — `no such table: full_nodes`. The Django test database doesn't create tables correctly. 13 tests (WebSocket broadcast + webhook config) still pass.
- **Vitest JS tests (145 failures)**: Pre-existing React rendering issues — components need context providers (AuthContext, Router, etc.) set up in test environment. Tauri mock infrastructure works correctly (no `invoke` errors). 14 tests pass.
- **Robyn server**: Fails to start with `Apps aren't loaded yet` — Django ORM bootstrap issue. API tests require this to be fixed before they can execute.

## Adding New Tests

1. **Python tests**: Add test files directly in the edition's `sidecar/tests/` dir, then update `run.sh` to discover them (formint-pos uses `manage.py test formint`)
2. **JS tests**: Add to `tests/js/` for editor-level tests, or directly in-edition `src/test/`
3. **Selenium tests**: Add `test_*.py` files to `tests/selenium/` (formint suite: `tests/selenium/formint/`)
4. **API tests**: Add `test_*.mjs` files to `tests/api/`
