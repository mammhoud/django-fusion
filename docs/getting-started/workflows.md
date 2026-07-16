# Workflows & CI

## GitHub Actions

### `deploy-ci.yml`

Located at `.github/workflows/deploy-ci.yml`.

Triggers on changes to:
- `Makefile` and `Makefile.*`
- `.github/workflows/deploy-ci.yml`
- `.github/actions/deploy-preflight/**`
- `**/docker-compose*.yml` and `*.yaml`
- `core/libs/**/*.md`
- `applications/scripts/check_markdown_links.py`

Jobs:

1. **preflight** — runs the local Composite Action `.github/actions/deploy-preflight` to validate Docker daemon and `make deploy-ci`.
2. **markdown-links** — runs `applications/scripts/check_markdown_links.py` to validate Markdown cross-links.

### `check-extras.yml`

Located at `.github/workflows/check-extras.yml`.

Validates that any `uv add "pkg[extras]"` / `pip install "pkg[extras]"` line in `core/libs/**/docs/` matches the extras declared in the corresponding `pyproject.toml`.

## Makefile delegation

The root `Makefile` is a thin entrypoint that delegates site work to `core/Makefile`.

```bash
# Run a target for a specific site
cd core
make check WEBSITE=ctc-research
make docker-up WEBSITE=lms-demo
make test WEBSITE=vresume
```

Common targets:

| Target | Purpose |
|---|---|
| `check` | Django system checks |
| `docker-up` | Build and start a site container |
| `docker-down` | Stop site containers |
| `docker-health-check` | Health-check running containers |
| `tests-unit` | Unit tests |
| `tests-integration` | Integration tests |

## Recommended enhancements

1. Add a `docs.yml` workflow that runs `docsify-cli` to validate sidebar links and render the docs on every docs PR.
2. Pin `actions/checkout` and `actions/setup-python` to specific hashes for supply-chain security.
3. Add a `make docs-serve` target in `core/Makefile` that starts a local docsify server for preview.
