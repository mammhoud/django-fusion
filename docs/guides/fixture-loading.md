# 📦 Fixture Loading Workflow

How to load Wagtail page content and seed data into the fusion site databases.

---

## Overview

Fusion sites (`cms-fusion`, `precis-lms`) ship with JSON fixture files that
populate the Wagtail database with pages, locales, users, and homepage
content blocks. Fixtures are loaded via the `load_fusion_fixtures` management
command, which wraps Django's `loaddata` with dependency ordering.

```
Fixture Files ──→ load_fusion_fixtures ──→ Django loaddata ──→ Wagtail DB
  assets/fixtures/     management command      JSON → ORM         Tables
```

## Fixture Directory Structure

```
projects/cms-fusion/assets/fixtures/
├── test/                  # Test fixtures (4 files, ~97 KB)
│   ├── locales.json       # Language records (en, ar, fr, de, es, pt-br)
│   ├── users.json         # User accounts (page ownership)
│   ├── initial_choices.json  # Content type & image records
│   └── pages.json         # Wagtail page tree (home, about, contact, …)
├── seed/                  # Seed/demo content (1 file, ~6 KB)
│   └── homepage_content.json  # Sliders, features, about, CTA blocks
├── production/            # Production dumps
│   ├── just-locales.json
│   └── cleaned-dump-data.json
└── by-model/              # Per-model dumps
    ├── auth/
    ├── wagtailcore/
    └── wagtailimages/
```

> **Dependency order matters.** Locales load first, then users, then content
> types, then pages. The management command handles this automatically.
>
> **Fixtures are synced** between `cms-fusion` and `precis-lms` — both projects
> share identical fixture files under `assets/fixtures/`.

## Quick Start

```bash
# Load test fixtures (locales → users → choices → pages)
cd projects/cms-fusion/backend
python manage.py load_fusion_fixtures

# Load test + homepage content
python manage.py load_fusion_fixtures --full

# Preview what would be loaded (safe, no changes)
python manage.py load_fusion_fixtures --full --dry-run
```

## Command Reference

### `load_fusion_fixtures`

| Flag | Description |
|------|-------------|
| `-c test` | **Default.** Load test fixtures (4 files) |
| `-c seed` | Load seed/homepage_content.json only |
| `-c production` | Load production dumps (locales + cleaned data) |
| `-c by-model` | Load per-model dumps |
| `-c all` | Load everything (⚠️ overlapping PKs across categories) |
| `--full` | Load test + seed (equivalent to `-c test` + `-c seed`) |
| `--fixture PATH` | Load a single fixture file relative to `assets/fixtures/` |
| `-n` / `--dry-run` | Preview fixtures with size without loading |
| `--skip-missing` | Skip missing fixture files instead of erroring |
| `--dir DIR` | Override fixture directory path |

### Examples

```bash
# Preview all test + seed fixtures
python manage.py load_fusion_fixtures --full --dry-run

# Load only locale data
python manage.py load_fusion_fixtures --fixture test/locales.json

# Load production data, skip missing files
python manage.py load_fusion_fixtures -c production --skip-missing
```

### Dry-Run Output

```
📦 Fusion Fixture Loader

🔍 DRY RUN — 5 fixture(s) would be loaded:

  ✅  test/locales.json             (0.8 KB)
  ✅  test/users.json               (0.5 KB)
  ✅  test/initial_choices.json     (7.1 KB)
  ✅  test/pages.json               (89.2 KB)
  ✅  seed/homepage_content.json    (6.4 KB)
```

## When Fixtures Load

Fixtures are loaded at these points in the workflow:

| Context | Trigger | Notes |
|---------|---------|-------|
| **Local dev** | `python manage.py load_fusion_fixtures` | Manual, one-time or after DB reset |
| **Docker deploy** | `RUN_SETUP=true` env var in docker-compose | Runs inside backend container on startup |
| **CI/CD** | `manage.py load_fusion_fixtures --dry-run` | Validates fixture JSON is parseable |
| **Testing** | DB models populated via ORM in `setUpTestData` | Fixture JSON files are not used in tests (see below) |

## Testing vs. Fixtures

The `test_fixture_content.py` test suite does **not** use `loaddata`.
Instead, it creates Wagtail model instances directly via the ORM in
`setUpTestData`. This is intentional:

- Test database uses in-memory SQLite with migrations disabled (`_DisableMigrations`)
- `loaddata` requires a fully migrated database with content types
- ORM-created test data avoids these constraints and runs faster

The test suite verifies the same data structure as the fixtures:

```python
# Tests create Wagtail pages that mirror fixture structure:
home = root.add_child(instance=Page(
    title="Test Home Page", slug="test-home", live=True,
    seo_title="Fusion CMS | AI-Powered Platform",
    ...
))
```

## Proxy Access

After fixtures are loaded, page content is served through the Traefik
proxy. Two layers work together:

- **Docker labels** (`docker-compose.yml`) — container-level discovery:
  `traefik.enable=true`, `PathPrefix(/api)`, port, health check
- **File-based config** (`applications/proxy/traefik/dynamic/cms-fusion.yml`) —
  full routing with SSL termination, middleware (compress, CSRF, security
  headers), entrypoints (`web` + `web-secure`), and path-based priority

```
Browser → https://cms-fusion.localhost/api/pages/
       → Traefik proxy (SSL + middleware)
       → cms-fusion-api router (PathPrefix /api, priority 100)
       → cms-fusion-backend:5075
       → Django loads pages from Wagtail DB
```

See [Proxy & SSL](../infrastructure/proxy.md) for full proxy configuration details.

## CI Integration

The `fusion-ci.yml` workflow runs fixture content tests on every PR:

```yaml
# .github/workflows/fusion-ci.yml
- name: Run fixture content tests
  run: uv run python -m pytest cms-fusion/backend/tests/test_fixture_content.py -v --tb=short

- name: Run remaining tests
  run: uv run python -m pytest cms-fusion/backend/tests/ --ignore=...test_fixture_content.py -q
```

Fixture tests run **first** (fast-fail principle), and the remaining
tests exclude them via `--ignore` to avoid double execution.

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| `CommandError: Fixture directory not found` | Wrong working directory | Use `--dir` to specify path, or run from `backend/` |
| `IntegrityError` on load | Duplicate PKs from overlapping categories | Don't mix `test` + `production` categories |
| `ContentType matching query does not exist` | No migration for custom page models | Create `ContentType` records manually, or run `migrate` first |
| Fixture file not found | Wrong base path | Check `--dir` override or verify fixture file exists under `assets/fixtures/` |

---

→ [Back to Guides](README.md)
→ [Proxy & SSL Setup](../infrastructure/proxy.md)
