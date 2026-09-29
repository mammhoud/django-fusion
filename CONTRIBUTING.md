# Contributing to django-fusion

Thanks for contributing! This guide covers the practical day-to-day workflow.

## Local development setup

```bash
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion

# Python 3.11+ (see requires-python in pyproject.toml)
uv sync --extra test          # or: uv run --extra test pytest
```

`uv` is not required — `python -m venv .venv && .venv/bin/pip install -e ".[test,dev]"`
works too.

> **Remark:** `requires-python = ">=3.11"`. Python 3.10 fails to import some of
> the annotations used in the package.

## Running the test suite

```bash
uv run --extra test pytest                  # full suite
uv run --extra test pytest -q               # quiet
uv run --extra test pytest tests/analyzer    # one directory
uv run --extra test pytest tests/test_imports.py -v

# Opt-in verbose diagnostics (exact-match gate on "1"):
DJANGO_DEBUG_CONFTEST=1 uv run --extra test pytest -s tests/test_form_components.py
```

The suite is self-contained: no database server, no network, no surrounding
repository. Django settings live in `tests/_django_settings.py` and are applied
by `tests/conftest.py`; do not add a `DJANGO_SETTINGS_MODULE`.

Two facts about the suite are worth knowing before you add a test:

1. **Django's template engine caches aggressively.** `tests/conftest.py` restores
   `settings.TEMPLATES` and the engine caches between modules. If your test
   rewrites `settings.TEMPLATES`, that guard is what keeps the next module
   working — do not remove it.
2. **Optional extras must skip, not error.** Guard the third-party import
   *before* importing it, e.g. `jwt = pytest.importorskip("jwt")`. A collection
   error from a missing extra breaks the whole run.

## CI

`.github/workflows/ci.yml` runs on every push and pull request:

| Job | What it does |
|---|---|
| `test` | pytest across Python 3.11/3.12 and Django 4.2/5.2 |
| `package` | `uv build`, `twine check`, and a wheel smoke test |
| `lint` | `ruff check src tests` |

Run the same three locally before opening a PR:

```bash
uv run --extra test pytest -q
uv run --with ruff ruff check src tests
make dist && make check-dist
```

## Documentation

Docs use stable `DF-0NN` IDs from [`docs/INDEX.md`](./docs/INDEX.md). When you
change code or add a feature:

1. Find the matching `DF-0NN` row in `docs/INDEX.md`.
2. Update it, or create the next free ID for a new topic.
3. Update the index row (`🟡 TODO` → `✅ Exists`).
4. Reference the ID in commits and PR titles:

```text
feat(comp): add RoutableComponent.cache() method (DF-003)

- Implement the cache decorator on routable components
- Document in DF-003
- Add tests in tests/analyzer/
```

**Never mark a doc `✅ Exists` before its content is written.** Dead links were
the exact failure mode that motivated the current index.

If you document a new public import path, add it to
`tests/test_documented_import_paths.py` in the same change — that test is what
stops the docs from silently drifting away from the code.

## What belongs where

Keep the base package product-agnostic:

- **In `django-fusion`** — generic component/routing/fragment behavior, shared
  abstract model bases, framework settings, health and asset contracts.
- **In the consuming project** — concrete models and migrations, page types,
  component templates and their copy, URL mounts, task implementations, and
  deployment policy.

Two hard rules:

1. No product names, product page types, or product model classes in `src/`.
2. No monorepo paths anywhere in the repository — the library is published
   standalone and must build and test outside any workspace.

`tests/test_imports.py` and `tests/test_site_management_commands.py` pin both
boundaries.

## Commit message convention

- Reference `DF-NNN` for documentation changes.
- Reference `PR-NN` if a prompt from `PROMPTS.md` drove the change.
- Use the imperative mood ("add", not "added").
- Keep the subject under ~72 characters.
- The body explains *what* and *why*, not *how*.

## Pull request expectations

- Tests for any new public method or behavior.
- A matching doc update with a `DF-0NN` ID.
- Cross-references from related docs.
- No unrelated formatting or whitespace churn.

## Code style

Black-compatible 88-character formatting and PEP 8 type hints. Existing patterns:

- `from __future__ import annotations` at the top of modules that need it.
- Public classes carry full type hints; private helpers may use abbreviations.
- Import framework symbols from their owning module. Do not add re-export shims
  or forwarding `__init__.py` re-exports.

`ruff` is the linter:

```bash
uv run --with ruff ruff check src tests
```

## Releasing

Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html) and
`CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

The full runbook — version bump, build, `twine check`, wheel smoke test,
TestPyPI rehearsal, production upload, trusted publishing, and rollback — is
[**DF-023 Publishing**](./docs/23-publishing.md). The short path:

```bash
make version        # confirm pyproject.toml, __init__.py, and the changelog agree
make test
make dist
make check-dist
make publish-test   # TestPyPI rehearsal
git tag -a vX.Y.Z -m "django-fusion X.Y.Z"
make publish        # guarded: clean tree at the release tag
```

A version that reached PyPI is spent. To fix a bad release, ship the next number;
you cannot edit or re-upload an existing version.

## Questions?

Open an issue or discussion on
[mammhoud/django-fusion](https://github.com/mammhoud/django-fusion).

**Mahmoud Ezzat Moustafa** — Structa Cloud

- GitHub: [github.com/mammhoud](https://github.com/mammhoud)
- LinkedIn: [linkedin.com/in/mammhoud](https://www.linkedin.com/in/mammhoud)
- Facebook: [facebook.com/mammhoud](https://www.facebook.com/mammhoud)
