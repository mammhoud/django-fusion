# `tests/` — django-fusion test suite

Framework tests for the `django_fusion` package. Read the repository root
`AGENTS.md` first, then `../AGENTS.md`.

This suite covers the library only. Product and deployment tests live with the
consuming products (`projects/*`), not here.

## Layout

```text
tests/
├── conftest.py                     # sys.path bootstrap + Django configure()
├── _django_settings.py             # single source of truth for TEST_SETTINGS
├── urls.py                         # ROOT_URLCONF for the suite
├── analyzer/                       # fragment analyzer: parser, scanner, layout, views
├── fragments/                      # fragment view/renderer contracts
├── stubs/                          # wagtail/laces template-tag stubs
├── assets/                         # test templates and content fixtures
├── test_templates/                 # component templates under test
├── test_templates_comp_registry/   # sidecar (html/css/js) registry fixtures
├── test_rendering_decorators/      # templates for fusion_view dual-mode tests
└── test_*.py                       # top-level library tests
```

## Running

```bash
cd libs/django-fusion
uv run --extra test pytest            # full suite
uv run --extra test pytest -q         # quiet
uv run --extra test pytest tests/analyzer -q
uv run --extra test pytest tests/test_imports.py

# Opt-in diagnostics (exact-match gate on "1"):
DJANGO_DEBUG_CONFTEST=1 uv run --extra test pytest -s tests/test_form_components.py
```

Django settings live in `_django_settings.py` and are applied by
`conftest.py`; do not introduce a `DJANGO_SETTINGS_MODULE` for this suite.

## Conventions

- Pure-library tests only: no monorepo paths, no running services, no network.
- Assert response contracts and public behavior, not private implementation
  details.
- Optional extras (`bolt`, `tables`, `auth`, `webpack`, `tasks`) must degrade to
  a **skip**, never a collection error. Guard the third-party import *before*
  importing it — see `test_bolt_inprocess.py`.
- Keep tests independent and order-insensitive. Scanner/analyzer assertions
  must not depend on filesystem traversal order.
- Fixtures belong in `stubs/`, `assets/`, or the `test_templates*` directories;
  keep secrets and real data out of them.

## Content boundaries

Tests here must not reference product names, product model classes, or product
page vocabularies. If a test needs a product concept, it belongs in that
product's suite. `test_site_management_commands.py` pins this boundary for
management commands.

## Validation checklist

Run the narrowest affected test first, then the full suite. Report skipped tests
with their reason (missing optional extra, no database, no browser) rather than
claiming a pass.
