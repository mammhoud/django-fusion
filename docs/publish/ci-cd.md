# 🔄 CI/CD Pipelines

> GitHub Actions workflows for CI validation, testing, and deployment across all Structa Cloud projects.

---

## Workflow Reference

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-ci.yml` | PR + push to `**` | Compose preflight + markdown link validation |
| `pytest-core.yml` | PR + push touching `tests/` or `projects/` | Full test suite from `projects/` |
| `check-extras.yml` | PR touching `libs/**/*.md` | Validate pyproject.toml extras in docs |
| `release.yml` (×3) | Tag `v*.*.*` + manual | POS edition desktop releases |

---

## deploy-ci.yml

```yaml
# .github/workflows/deploy-ci.yml
on:
  pull_request:
    paths:
      - '**/docker-compose*.yml'
      - 'libs/**/*.md'
  push:
    branches: ['**']

jobs:
  preflight:
    - make deploy-ci                    # Compose config validation
  markdown-links:
    - python applications/scripts/check_markdown_links.py  # Broken link check
```

**What it validates:**
- All Docker Compose files parse without error
- Deployment order is valid (postgres-first / legacy)
- All Docker networks are syntactically valid
- No broken relative or HTTP links in Markdown files

---

## pytest-core.yml

```yaml
# .github/workflows/pytest-core.yml
on:
  pull_request:
    paths: ['tests/**', 'projects/**']
  push:
    branches: ['**']

jobs:
  pytest:
    defaults:
      run:
        working-directory: projects
    steps:
      - uses: actions/checkout@v4
      - run: uv sync
      - run: uv run pytest
```

**Tests discovered:**
- `tests/` — Workspace-level Django tests
- `libs/django-fusion/tests/analyzer/` — Framework analyzer tests

---

## check-extras.yml

```yaml
# .github/workflows/check-extras.yml
on:
  pull_request:
    paths: ['libs/**/*.md', '**/pyproject.toml']

jobs:
  check-extras:
    - python applications/scripts/check_extras_in_docs.py
```

Validates every `uv add "pkg[extras]"` line in docs matches actual `pyproject.toml` `[project.optional-dependencies]`.

---

## POS Release Workflows (×3)

Each POS edition has its own release workflow:

```yaml
# projects/pos/formint-pos/.github/workflows/release.yml
on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest, target: x64, bundles: nsis,msi
          - os: ubuntu-latest,  target: x64, bundles: appimage
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - run: pnpm install
      - run: pnpm tauri build --target ${{ matrix.target }}
      - uses: softprops/action-gh-release@v1
```

Three identical workflows at:
- `projects/pos/pos-minimal/.github/workflows/release.yml`
- `projects/pos/formint-pos/.github/workflows/release.yml` (merged package — formerly pos-solo + pos-full)

---

## Running Locally

```bash
# Run preflight validation (same as CI gate)
make deploy-ci

# Run full test suite
uv run pytest

# Check markdown links (requires Python 3.11+)
python applications/scripts/check_markdown_links.py

# Check pyproject.toml extras in docs
python applications/scripts/check_extras_in_docs.py
```

---

## Related

| Topic | Path |
|-------|------|
| Docker deploy | [`docker-deploy.md`](docker-deploy.md) |
| POS releases | [`pos-release.md`](pos-release.md) |
| Testing | [`../tests/`](../tests/) |
