# Contributing to django-fusion

Thanks for contributing! This guide covers practical day-to-day workflow.

## Local development setup

```bash
# Clone standalone
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion

# Or, inside the Structa Cloud monorepo, the submodule lives at:
#   core/libs/django-fusion/

# Create a virtualenv (Python 3.11+ per pyproject.toml requires-python)
python3.11 -m venv .venv
source .venv/bin/activate

# Install in editable mode with test extras
pip install -e ".[test]"
```

> Remark: `requires-python = ">=3.11"` — Python 3.10 will fail to import some
> type annotations used in `core/services` and `core/models`.

## Running the test suite

```bash
# From the repo root (or submodule root if checked out standalone)
pytest

# Focused run
pytest tests/test_comp_routes.py -v

# Quiet-by-default opt-in verbose mode:
DJANGO_DEBUG_CONFTEST=1 pytest -s tests/test_form_components.py
```

The `DJANGO_DEBUG_CONFTEST=1` env var opts into extra diagnostic logging from
`tests/conftest.py` (Django TEMPLATES config, DJANGO_SETTINGS_MODULE). Without
it, conftest stays quiet — this is enforced by `tests/test_conftest_debug_is_quiet.py`.

The exact-match comparison (`os.environ.get("DJANGO_DEBUG_CONFTEST") == "1"`)
means empty strings or accidental values do NOT trigger the print.

## CI workflow (`.github/workflows/tests.yml`)

The GitHub Actions workflow is **staged at `docs/ci/tests.yml`**, not at
`.github/workflows/tests.yml`. This is intentional: the Personal Access
Token used by the parent Structa Cloud monorepo's `make push-libs` target
does not carry the **`workflow`** OAuth scope that GitHub requires to
create or update files under `.github/workflows/`.

When you have a token with the `workflow` scope (a maintainer push
under `mammhoud/django-fusion`), restore the workflow to its normal
location with this snippet from the submodule root:

```bash
# Run this from inside the submodule root (e.g. core/libs/django-fusion)
cd core/libs/django-fusion

mkdir -p .github/workflows
cp docs/ci/tests.yml .github/workflows/tests.yml
git add .github/workflows/tests.yml
git commit -m "ci: restore GitHub Actions workflow from docs/ci staging"
git push origin generic
```

Why the indirection? Without `workflow` scope, GitHub returns:

```
remote: Refusing to allow a Personal Access Token to create or update
        workflow `.github/workflows/tests.yml` without `workflow` scope.
```

…and refuses the push. So the file lives in `docs/ci/` until a workflow-
scoped token pushes it back. The content is identical between locations.

## Documentation

The repo uses stable doc IDs `DF-0NN` (from [`docs/INDEX.md`](./docs/INDEX.md)).
When you change code or add a feature:

1. Find the matching `DF-0NN` row in `docs/INDEX.md`.
2. Update or create the doc with the next free ID.
3. Update the index row's status (`🟡 TODO` → `✅ Exists`).
4. Reference the doc ID in commits and PR titles, e.g.:

```text
feat(comp): add `RoutableComponent.cache()` method (DF-003)

- Implement LRU cache decorator on routable components
- Document in DF-003
- Add test in tests/test_routable_components.py
```

**Never mark a doc "✅ Exists" before its content is written.** That was the
exact mistake in the previous iteration, and it created ~20 dead links.

## Commit message convention

- Reference `DF-NNN` for any doc change
- Reference `PR-NN` if a prompt from `PROMPTS.md` drove the change
- Use imperative mood ("add", not "added")
- Wrap the subject at ~72 characters
- Body explains *what* and *why*, not *how*

## Pull request expectations

PRs should include:

- Tests for any new public method or behavior
- A matching doc update with a `DF-0NN` ID
- Cross-references from related docs (e.g. DF-003 should mention DF-004)
- No unrelated formatting/whitespace changes

## Code style

This repo currently uses Black-style 88-character formatting and PEP 8 type
hints. Existing patterns:

- `from __future__ import annotations` is used in `comp/routes.py` and
  `core/services.py`
- Public classes use full type hints; private helpers may use abbreviations
- Never wrap imports in `try`/`except` (see project AGENTS.md)

## Releasing

Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
CHANGELOG.md follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
format. Maintainers handle version bumps and PyPI publication.

## Questions?

Open a GitHub issue or discussion on
[mammhoud/django-fusion](https://github.com/mammhoud/django-fusion).
