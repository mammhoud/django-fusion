# 🧪 Testing

> Test architecture and coverage across all Structa Cloud projects.

> ⚠️ **Historical**: POS examples referencing `pos-full/` predate the merge of
> `pos-full` + `pos-solo` into `projects/pos/formint-pos/` (unified tests now in
> `projects/pos/tests/`).

---

## Test Architecture

```
structa.cloud/
├── tests/                              # Workspace-level tests
│   ├── conftest.py                     # Pytest fixtures + Django config
│   ├── settings.py                     # Test Django settings
│   ├── apps/                           # Mock Django apps for tests
│   └── projects/configs/               # Test config helpers
├── projects/
│   └── <site>/tests/                   # Per-site Django tests
├── libs/
│   └── django-fusion/tests/            # Library tests
│       ├── analyzer/                   # Analyzer tests
│       ├── test_register_*.py          # Component registry tests
│       └── django_grep/                # Grep integration tests
└── projects/pos/
    └── pos-<variant>/src/              # Rust unit tests (inline)
```

---

## Running Tests

### All Tests (from repo root)

```bash
uv run pytest                          # Full suite
uv run pytest tests/                   # Workspace tests only
uv run pytest libs/django-fusion/tests/analyzer/  # Analyzer tests
```

### Per-Project Django Tests

```bash
cd projects
make test WEBSITE=lms                  # LMS tests
make test WEBSITE=portfolio            # Portfolio tests
make test WEBSITE=cypercloud           # Cypercloud tests
```

### POS Tests (Rust)

```bash
cd projects/pos/pos-full
cargo test                             # All Rust unit tests
cargo test --lib                       # Library tests only
```

---

## Test Configuration

| Component | Config File | Settings Module |
|-----------|------------|-----------------|
| Root pytest | `pyproject.toml` (`[tool.pytest.ini_options]`) | `tests.settings` |
| Per-site Django | `projects/<site>/tests/conftest.py` | Site-specific |
| django-fusion | `libs/django-fusion/tests/conftest.py` | Library-specific |

### Root `pyproject.toml` pytest config

```toml
[tool.pytest.ini_options]
addopts = ["--import-mode=importlib"]
testpaths = ["tests", "libs/django-fusion/tests/analyzer"]
DJANGO_SETTINGS_MODULE = "tests.settings"
pythonpath = [".", "libs/django-fusion/src"]
```

---

## Test Types

| Type | Framework | Scope |
|------|-----------|-------|
| Django unit tests | `pytest-django` | Per-site models, views, forms |
| Django integration | `pytest-django` | Request/response, templates |
| Component equivalence | `pytest` | `{% include %}` vs `{% comp %}` |
| Analyzer tests | `pytest` | django-fusion code analysis |
| Rust unit tests | `cargo test` | POS backend operations |
| CI preflight | `make deploy-ci` | Compose file validation |

---

## CI Integration

```yaml
# .github/workflows/pytest-core.yml
pytest:
  name: Run pytest from projects/
  defaults:
    run:
      working-directory: projects
  steps:
    - run: uv run pytest
```

---

## Related

| Topic | Path |
|-------|------|
| Best practices | [`../guides/07-best-practices.md`](../guides/07-best-practices.md) |
| django-fusion | [`../libs/django-fusion.md`](../libs/django-fusion.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
