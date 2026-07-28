# django-fusion — Full Execution Plan with Phases

**Library repo:** mammhoud/django-fusion (`generic` branch)  
**Scope:** Documentation (DF-0NN), Prompts (PR-NN), Project hygiene, PyPI readiness  
**Audience:** Developers writing docs, AI agents using `AGENTS.md`, library consumers on PyPI (eventually)

This plan takes the recommendations from `django-fusion-enhancements.md` and breaks them into actionable phases with validation checkpoints. Unlike the monorepo plan, this is a **library**, so focus is on documentation, testing, and publishing readiness — not deployment.

---

## PHASE 0: Baseline Audit (15–30 min)

**Goal:** Understand the current state of the library and identify which enhancements from the companion doc are already done.

### 0.1 — Verify Current Doc State

```bash
# From repo root (mammhoud/django-fusion, generic branch)

echo "=== Current docs/ structure ===" && \
  find docs -type f -name "*.md" | sort

echo "=== Current root-level doc/prompt files ===" && \
  ls -1 *.md

echo "=== Broken symlinks (from earlier audit) ===" && \
  find . -type l ! -exec test -r {} \; -print 2>/dev/null

echo "=== Test file count ===" && \
  find tests -name "test_*.py" | wc -l

echo "=== Current pyproject.toml license/readme metadata ===" && \
  grep -E "license|readme|authors|classifiers" pyproject.toml | head -20
```

**Validate:**
- All existing docs are accounted for (currently: INDEX.md, DOCUMENTATION_MAP.md, COMPONENT_TAG.md, COMPONENT_CASE_STUDIES.md, VIEWFLOW_MAPPING.md, legacy-django-grep/)
- No broken symlinks at repo root
- Tests exist and are numerous (37+ files)

**Save output to:** `reports/phase-0-django-fusion-baseline.txt`

### 0.2 — Verify Submodule Status (when pulled from monorepo)

```bash
# If this repo is checked out as a submodule from ceptor-ai:
# (This check applies only if you're working in ceptor-ai/applications/libs/django-fusion/)

git status
git branch -a | grep generic
git log --oneline -10

# If checked out standalone (most likely for isolated dev):
# (This check still applies — just verify we're on generic)

git branch -a
git checkout generic
```

**Validate:**
- Currently on `generic` branch
- No uncommitted changes (`git status` clean)

**Save output to:** `reports/phase-0-branch-status.txt`

### 0.3 — Check Package Metadata Completeness

```bash
# From repo root

echo "=== pyproject.toml [project] section ===" && \
  sed -n '/^\[project\]/,/^\[/p' pyproject.toml | head -40

echo "=== License file ===" && \
  ls -la LICENSE* 2>&1

echo "=== CI workflows ===" && \
  ls -la .github/workflows/ 2>&1

echo "=== CONTRIBUTING.md ===" && \
  ls -la CONTRIBUTING.md 2>&1
```

**Validate:**
- `pyproject.toml` has `license`, `readme`, `authors`, `classifiers` — or these are missing (expected)
- No LICENSE file exists yet (expected — needs to be added)
- No CI in `.github/workflows/` (expected — will be added in Phase 4)
- No CONTRIBUTING.md (expected — will be added in Phase 4)

**Save output to:** `reports/phase-0-package-metadata.txt`

---

## PHASE 1: Documentation Deduplication & Index (30–45 min)

**Goal:** Clean up the docs and ensure the index is truthful (not listing files that don't exist).

### 1.1 — Audit & Fix docs/INDEX.md and docs/DOCUMENTATION_MAP.md

```bash
# From repo root

# 1. List all actual docs files
echo "=== Files that exist in docs/ ===" && \
  find docs -type f -name "*.md" -o -name "*.py" | sort

# 2. Extract all links from INDEX.md and DOCUMENTATION_MAP.md
echo "=== Files mentioned in INDEX.md ===" && \
  grep -oE '\[.*?\]\(([^)]+\.md)\)' docs/INDEX.md | sed 's/.*(\(.*\)).*/\1/' | sort -u

echo "=== Files mentioned in DOCUMENTATION_MAP.md ===" && \
  grep -oE '\[.*?\]\(([^)]+\.md)\)' docs/DOCUMENTATION_MAP.md | sed 's/.*(\(.*\)).*/\1/' | sort -u

# 3. Check which mentioned files don't exist
echo "=== Dead links (files mentioned but missing) ===" && \
  python3 <<'PYEOF'
import os
import re

# Parse docs
for doc_file in ["docs/INDEX.md", "docs/DOCUMENTATION_MAP.md"]:
    with open(doc_file) as f:
        content = f.read()
    
    # Find all markdown links
    links = re.findall(r'\[.*?\]\(([^)]+\.md)\)', content)
    for link in links:
        path = os.path.join("docs", link) if not link.startswith("docs/") else link
        if not os.path.exists(path) and not os.path.exists(link):
            print(f"MISSING (from {doc_file}): {link}")
PYEOF
```

**Validate:**
- Identify all dead links
- Record them for deletion from the index (Phase 1.2)

**Save output to:** `reports/phase-1-docs-audit.txt`

### 1.2 — Update docs/INDEX.md to Match Reality

```bash
# From repo root

# 1. Backup the current INDEX
cp docs/INDEX.md docs/INDEX.md.bak

# 2. Create a new INDEX that only lists files that exist
cat > docs/INDEX.md <<'EOF'
# django-fusion Documentation Index

This index maps documentation files to stable IDs (`DF-0NN`) for cross-referencing in commits, PRs, and prompts.

## Documentation Map

| ID | File | Topic | Status |
|---|---|---|---|
| DF-000 | `docs/INDEX.md` | This index | ✅ Exists |
| DF-001 | `docs/01-getting-started.md` | Getting started & installation | 🟡 TODO |
| DF-002 | `docs/02-architecture.md` | System architecture | 🟡 TODO |
| DF-003 | `docs/03-component-system.md` | Component system (Python side) | 🟡 TODO |
| DF-004 | `docs/04-component-tag.md` | Component template tag | ✅ Exists (legacy: COMPONENT_TAG.md) |
| DF-005 | `docs/05-routing.md` | URL routing & viewsets | 🟡 TODO |
| DF-006 | `docs/06-forms-and-tables.md` | Forms & tables integration | 🟡 TODO |
| DF-007 | `docs/07-configuration.md` | Configuration & settings | 🟡 TODO |
| DF-008 | `docs/08-api-reference.md` | API reference | 🟡 TODO |
| DF-009 | `docs/09-health.md` | Health checks | 🟡 TODO |
| DF-010 | `docs/10-wagtail-integration.md` | Wagtail CMS integration | 🟡 TODO |
| DF-011 | `docs/11-best-practices.md` | Best practices & patterns | 🟡 TODO |
| DF-012 | `docs/12-integration-examples.md` | Integration examples (absorbs COMPONENT_CASE_STUDIES.md) | 🟡 TODO |
| DF-013 | `docs/13-troubleshooting.md` | Troubleshooting | 🟡 TODO |
| DF-014 | `docs/14-faq.md` | Frequently asked questions | 🟡 TODO |
| DF-015 | `docs/15-viewflow-mapping.md` | Viewflow comparison (legacy: VIEWFLOW_MAPPING.md) | ✅ Exists |

## Legacy Files (do not update; scheduled for deduplication)

- `docs/COMPONENT_TAG.md` → Move to `docs/04-component-tag.md` (DF-004)
- `docs/COMPONENT_CASE_STUDIES.md` → Merge into `docs/12-integration-examples.md` (DF-012)
- `docs/VIEWFLOW_MAPPING.md` → Rename to `docs/15-viewflow-mapping.md` (DF-015)
- `docs/legacy-django-grep/` → Archive to `docs/legacy/` (not actively maintained)

## Using this Index

- When **writing a new doc**, add a row here with the next free `DF-0NN` ID and mark as 🟡 TODO.
- When **content is ready**, change status to ✅ Exists.
- **Never mark a file "Exists" if it's not actually written** — this index is your source of truth.
- Use `DF-NNNN` IDs in commit messages, PRs, and cross-references.

---

**Last updated:** [date]
EOF

# 3. Delete or redirect the old DOCUMENTATION_MAP.md
mv docs/DOCUMENTATION_MAP.md docs/DOCUMENTATION_MAP.md.archive

# 4. Create a redirect stub (for one release cycle)
cat > docs/DOCUMENTATION_MAP.md <<'EOF'
> This file has been consolidated into [`docs/INDEX.md`](./INDEX.md). See there for the current documentation status.
EOF

# 5. Commit
git add docs/INDEX.md docs/DOCUMENTATION_MAP.md
git commit -m "Phase 1: Fix docs/INDEX.md to match reality

- Removed dead links (files mentioned but not existing)
- Introduced DF-0NN stable IDs for cross-references
- Marked TODO docs that need to be written
- Never mark files 'complete' before they exist

DF-000: docs/INDEX.md"
```

**Validate:**
- `docs/INDEX.md` exists and is complete
- No ✅ rows point to non-existent files
- Legacy files are listed with instructions for where they'll move
- `docs/DOCUMENTATION_MAP.md` now redirects to INDEX.md

**Save output to:** `reports/phase-1-index-fixed.txt`

### 1.3 — Rename Legacy Files to Numbered Names

```bash
# From repo root

# 1. Rename COMPONENT_TAG.md to 04-component-tag.md
mv docs/COMPONENT_TAG.md docs/04-component-tag.md

# 2. Archive COMPONENT_CASE_STUDIES.md for manual merge into integration examples
cp docs/COMPONENT_CASE_STUDIES.md docs/COMPONENT_CASE_STUDIES.md.archive

# 3. Rename VIEWFLOW_MAPPING.md to 15-viewflow-mapping.md
mv docs/VIEWFLOW_MAPPING.md docs/15-viewflow-mapping.md

# 4. Create stubs for renamed files (for one release)
cat > docs/COMPONENT_TAG.md <<'EOF'
> This file has moved to [`docs/04-component-tag.md`](./04-component-tag.md) (DF-004).
EOF

cat > docs/VIEWFLOW_MAPPING.md <<'EOF'
> This file has moved to [`docs/15-viewflow-mapping.md`](./15-viewflow-mapping.md) (DF-015).
EOF

# 5. Archive the legacy-django-grep/ to legacy/
mkdir -p docs/legacy
mv docs/legacy-django-grep docs/legacy/django-grep-legacy

# 6. Commit
git add -A
git commit -m "Phase 1: Rename docs to numbered structure

- COMPONENT_TAG.md → 04-component-tag.md (DF-004)
- VIEWFLOW_MAPPING.md → 15-viewflow-mapping.md (DF-015)
- legacy-django-grep/ → legacy/django-grep-legacy/
- Create redirect stubs for one-release deprecation

Closes: DF-000 INDEX update"
```

**Validate:**
- New numbered filenames exist (04-component-tag.md, 15-viewflow-mapping.md)
- Redirect stubs exist at old paths
- No loss of content (check that renamed files have same content as originals)

**Save output to:** `reports/phase-1-files-renamed.txt`

---

## PHASE 2: Root-Level File Cleanup (15–30 min)

**Goal:** Remove the broken symlink and fix install/path references so docs work standalone.

### 2.1 — Remove Broken Symlink

```bash
# From repo root

echo "=== Check for broken symlinks ===" && \
  find . -type l ! -exec test -r {} \; -print 2>/dev/null

# Remove the broken django-fusion symlink at root
rm -f django-fusion

# Verify it's gone
ls -la django-fusion 2>&1

# Commit
git add -u
git commit -m "Phase 2: Remove broken symlink (django-fusion)

This symlink pointed to /app/libs/django-fusion in the Structa Cloud monorepo.
It's not needed in the standalone repo."
```

**Validate:**
- `ls -la django-fusion 2>&1` returns "No such file or directory"

**Save output to:** `reports/phase-2-symlink-removed.txt`

### 2.2 — Fix Install Path References in Documentation

```bash
# From repo root

# 1. Check where install paths are mentioned
echo "=== Files mentioning monorepo install path ===" && \
  grep -rn "applications/libs/django-fusion" . --include="*.md" 2>/dev/null

# 2. Update README.md to fix the install path
cat > README.md <<'EOF'
# django-fusion

`django-fusion` is a Django helper library for component-based template systems, routing, caching, and form/table integration.

## Quick Start

### Installation

**Standalone (PyPI, recommended):**
```bash
pip install django-fusion
```

**Local editable (development):**
```bash
# Clone the repo
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion

# Install in editable mode
pip install -e .
```

### Basic Setup

1. Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    "django_fusion.comp",
    "django_fusion.core",
    # ...
]
```

2. Load component tags globally:
```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {
            "builtins": [
                "django_fusion.comp.templatetags.components",
            ],
        },
    },
]
```

3. Use components in templates:
```django
{% comp "button" label="Click me" variant="primary" / %}
```

## Documentation

- [Getting Started](./docs/01-getting-started.md) (DF-001)
- [Architecture](./docs/02-architecture.md) (DF-002)
- [Component System](./docs/03-component-system.md) (DF-003)
- [Component Tag ({% comp %})](./docs/04-component-tag.md) (DF-004)
- [Full Index](./docs/INDEX.md) (DF-000)

## Features

- **Component system** — `RoutableComponent`, `FragmentComponent` for modular templates
- **Routing helpers** — `Site`, `Application`, `Viewset` for organizing URLs
- **Form/table mixins** — CRUD patterns with `FormMixin`, `TableMixin`
- **Caching** — `CachedManager` for efficient model queries
- **Health checks** — Deployment monitoring endpoints
- **Wagtail integration** — CMS blocks, snippets, viewsets

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup and guidelines.

## License

See [LICENSE](./LICENSE) for license details.

---

**Repository:** https://github.com/mammhoud/django-fusion  
**Issues:** https://github.com/mammhoud/django-fusion/issues  
**Discussions:** https://github.com/mammhoud/django-fusion/discussions
EOF

# 3. Update AGENTS.md to use repo-relative paths
sed -i \
  -e 's|applications/libs/django-fusion/src/|src/|g' \
  -e 's|applications/libs/django-fusion/docs/|docs/|g' \
  -e 's|applications/libs/django-fusion/tests/|tests/|g' \
  AGENTS.md

# 4. Update PROMPTS.md similarly
sed -i \
  -e 's|applications/libs/django-fusion/|./|g' \
  PROMPTS.md

# 5. Commit
git add README.md AGENTS.md PROMPTS.md
git commit -m "Phase 2: Fix install paths & documentation for standalone repo

- README.md now shows pip install and repo-relative paths
- Remove monorepo-specific 'applications/libs/django-fusion' prefixes
- Update AGENTS.md and PROMPTS.md with standalone paths
- This repo is now fully independent"
```

**Validate:**
- `README.md` mentions `pip install django-fusion`
- All paths are either absolute URLs (github.com) or relative to repo root
- `grep -rn "applications/libs" . --include="*.md"` returns no results

**Save output to:** `reports/phase-2-paths-fixed.txt`

---

## PHASE 3: Documentation Creation (Using Companion Prompts)

**Goal:** Write the missing documentation files using the PR-NN prompts from the companion `django-fusion-enhancements.md`.

For this phase, you have two options:

**Option A: Use prompts directly (manual writing)**  
Copy each prompt from `django-fusion-enhancements.md` §3 and follow its instructions manually.

**Option B: Use an AI agent**  
Feed the prompts to Claude (or another AI) and request it write each doc.

Either way, the structure is the same: one prompt per file, validated before committing.

### 3.1 — Create docs/01-getting-started.md (DF-001)

Use **PR-01** from companion doc §3.2.

```bash
# From repo root

# 1. Create the file (manually or via AI prompt)
cat > docs/01-getting-started.md <<'EOF'
# Getting Started with django-fusion (DF-001)

**Time estimate:** 10 minutes

This guide walks you through installing django-fusion and creating your first component.

## Installation

### Via pip (recommended)

```bash
pip install django-fusion
```

### Development install

```bash
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion
pip install -e ".[dev]"
```

> Remark: The `[dev]` extra includes testing dependencies (pytest, factory-boy, etc.).

## Django Setup

### 1. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    
    # django-fusion
    "django_fusion.comp",           # Component system
    "django_fusion.core",           # Models, managers, services
    "django_fusion.health",         # Health checks (optional)
    "django_fusion.analyzer",       # Component analyzer (optional)
    
    # Your apps
    "myapp",
]
```

### 2. Configure Template Loader

To use `{% comp %}` without `{% load components %}` in every template:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                # Make component tag globally available
                "django_fusion.comp.templatetags.components",
            ],
        },
    },
]
```

> Remark: Setting `APP_DIRS: True` allows Django to find templates in app `templates/` subdirectories automatically.

### 3. (Optional) Enable Health Checks

```python
# urls.py
from django_fusion.health.urls import health_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", include(health_urls)),  # Health endpoints
]
```

## Your First Component

### 1. Create a Component File

```bash
mkdir -p myapp/components
touch myapp/components/__init__.py
touch myapp/components/button.py
```

### 2. Define a Component

```python
# myapp/components/button.py
from django_fusion.comp.routes import RoutableComponent
from pydantic import Field

class ButtonComponent(RoutableComponent):
    """A simple button component."""
    
    label: str = Field(..., description="Button text")
    variant: str = Field("primary", description="Button style (primary, secondary, danger)")
    disabled: bool = Field(False, description="Is button disabled?")
    
    class Meta:
        template = "components/button.html"
```

### 3. Create the Template

```django
{# myapp/templates/components/button.html #}
<button class="btn btn-{{ component.variant }}" {% if component.disabled %}disabled{% endif %}>
  {{ component.label }}
</button>
```

### 4. Register the Component

```python
# myapp/components/__init__.py
from django_fusion.comp.registry import component_registry
from .button import ButtonComponent

component_registry.register(ButtonComponent, name="button")
```

### 5. Use in Templates

```django
{# myapp/templates/index.html #}
{% comp "button" label="Click me" variant="primary" / %}
{% comp "button" label="Disabled" disabled=True / %}
```

## What's Next?

- [Component System (DF-003)](./03-component-system.md) — Learn the Python-side component API
- [Component Tag (DF-004)](./04-component-tag.md) — Template syntax reference
- [Routing (DF-005)](./05-routing.md) — Build URLs and viewsets
- [Best Practices (DF-011)](./11-best-practices.md) — Design patterns and tips

---

See [docs/INDEX.md](./INDEX.md) (DF-000) for the full documentation index.
EOF

# 2. Commit
git add docs/01-getting-started.md
git commit -m "Phase 3: Add getting started guide (DF-001)

Covers installation, Django setup, and a minimal button component example.
Source: PR-01 from django-fusion-enhancements.md

DF-001: docs/01-getting-started.md"
```

**Validate:**
- File exists and has real content
- Examples are copy-pasted from real source (or marked with source file path)
- No unresolved TODOs or placeholder text

**Save output to:** `reports/phase-3-df-001-created.txt`

### 3.2 — Create docs/02-architecture.md (DF-002)

Use **PR-02** from companion doc §3.3.

*(Process identical to 3.1; output: docs/02-architecture.md with system overview and Mermaid diagram)*

### 3.3 — Create docs/03-component-system.md (DF-003)

Use **PR-03** from companion doc §3.4.

*(Similarly, creates docs/03-component-system.md, coordinating with DF-004)*

### 3.4 — Continue Through Remaining Prompts

For each remaining prompt (PR-04 through PR-17 from the companion doc):
1. Create the target doc file (DF-NNNN or PR-NNNN)
2. Write content using the prompt as specification
3. Validate against the checklist
4. Commit with reference to the prompt

**Focus order (fast path):**
- DF-001, DF-002 (foundation)
- DF-003, DF-004 (components — the library's centerpiece)
- DF-005, DF-006 (routing + forms/tables — common usage patterns)
- DF-008 (API reference — bulk of remaining enhancements; consider generating from docstrings via prompt to Claude)
- DF-009, DF-010 (optional features — can wait if time-constrained)
- DF-011, DF-012 (patterns + examples — high value for UX)
- DF-013, DF-014 (support docs — lower priority but help retention)

---

## PHASE 4: Project Hygiene (30–45 min)

**Goal:** Add LICENSE, CONTRIBUTING, CHANGELOG, and CI workflow.

### 4.1 — Add LICENSE

```bash
# From repo root

# 1. Determine the correct license
#    (Ask maintainer or default to MIT for Django libraries)
#    For this example, using MIT:

cat > LICENSE <<'EOF'
MIT License

Copyright (c) 2024 Structa Cloud / Mahmoud [maintainer]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF

# 2. Commit
git add LICENSE
git commit -m "Phase 4: Add MIT License

This is a public, open-source library. MIT license permits
free use, modification, and redistribution with attribution."
```

**Validate:**
- LICENSE file exists and is properly formatted
- License choice matches project intent

**Save output to:** `reports/phase-4-license-added.txt`

### 4.2 — Add CONTRIBUTING.md

```bash
# From repo root

cat > CONTRIBUTING.md <<'EOF'
# Contributing to django-fusion

Thank you for your interest in contributing! This document outlines the process.

## Getting Started

### 1. Clone and Set Up Locally

```bash
git clone https://github.com/mammhoud/django-fusion.git
cd django-fusion
git checkout generic

# Install in editable mode with dev dependencies
pip install -e ".[dev,test]"
```

### 2. Run Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/django_fusion --cov-report=term-missing

# Run a specific test file
pytest tests/test_component_tag.py -v
```

### 3. Check Documentation

```bash
# Verify no broken links in docs/
find docs -name "*.md" | while read f; do
  grep -oE '\(([^)]+\.md)\)' "$f" | sed 's/.*(\(.*\)).*/\1/' | while read link; do
    [ -f "$link" ] || echo "BROKEN: $link (in $f)"
  done
done
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/component-slots` — new feature
- `fix/asset-loading-404` — bug fix
- `docs/quickstart-guide` — documentation
- `chore/update-dependencies` — maintenance

### Commit Messages

Reference doc IDs and prompts where relevant:

```
Add component caching (DF-003, PR-03)

- Implement RoutableComponent.cache() method
- Add LRU cache decorator
- Document in DF-003

Closes #42
```

### PR Description Template

```markdown
## What

Brief summary of changes.

## Why

Motivation or issue being addressed.

## How

Implementation details or approach.

## Testing

How to verify the change works locally.

## Related Docs

- DF-003 (Component System)
- PR-03 (Component caching prompt)
```

## Debugging Tips

### Enable Debug Logging

Set `DJANGO_DEBUG_CONFTEST=1` when running tests:

```bash
DJANGO_DEBUG_CONFTEST=1 pytest tests/ -v
```

This logs additional context and doesn't suppress output (useful for tracking
down import/configuration issues).

### Template Debugging

If a component doesn't render:
1. Check the component is registered: `component_registry._components.keys()`
2. Verify template path: Check `component.Meta.template`
3. Test rendering in Python shell: `render_to_string("path/to/template", {...})`

## Code Style

This project uses:
- **Black** for formatting (if installed)
- **Ruff** for linting
- **Pytest** for testing

```bash
# Format code
black src/django_fusion tests/

# Lint
ruff check src/ tests/

# Test
pytest
```

## Documentation

When adding a feature:
1. Update or create the relevant `DF-0NN` doc
2. Add examples to the doc
3. Link the doc from related files
4. Update `docs/INDEX.md` if adding a new `DF-NNNN` ID

Use the prompt in `PROMPTS.md` that corresponds to your feature.

## Questions?

- Open a [GitHub Discussion](https://github.com/mammhoud/django-fusion/discussions)
- Check [FAQ (DF-014)](./docs/14-faq.md) for common questions
- See [Troubleshooting (DF-013)](./docs/13-troubleshooting.md) for error resolution

---

Happy contributing! 🚀
EOF

# 2. Commit
git add CONTRIBUTING.md
git commit -m "Phase 4: Add CONTRIBUTING.md

Documents setup, testing, commit conventions, and debugging tips
for developers contributing to the library."
```

**Validate:**
- CONTRIBUTING.md explains local dev setup clearly
- Testing instructions are accurate
- Link to docs (DF-0NN IDs) are correct

**Save output to:** `reports/phase-4-contributing-added.txt`

### 4.3 — Add CHANGELOG.md

```bash
# From repo root

cat > CHANGELOG.md <<'EOF'
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete documentation index (DF-000) with numbered structure for stable cross-references
- Getting started guide (DF-001) with installation and first component example
- Architecture overview (DF-002) with Mermaid diagrams
- Component system documentation (DF-003) covering Python-side API
- Component tag reference (DF-004) for template syntax (formerly COMPONENT_TAG.md)
- Routing documentation (DF-005) for Site/Application/Viewset patterns
- Forms and tables integration (DF-006)
- Configuration guide (DF-007)
- API reference (DF-008)
- Health check documentation (DF-009)
- Wagtail integration (DF-010)
- Best practices (DF-011)
- Integration examples (DF-012)
- Troubleshooting guide (DF-013)
- FAQ (DF-014)
- Viewflow comparison (DF-015)
- LICENSE file (MIT)
- CONTRIBUTING.md for developers
- CI workflow (.github/workflows/tests.yml)

### Fixed
- Fixed documentation index (docs/INDEX.md) — no more dead links
- Removed broken symlink at repo root
- Updated install paths for standalone repository
- Fixed AGENTS.md and PROMPTS.md to use repo-relative paths

### Changed
- Restructured docs/ to use numbered filenames (DF-0NN) for stable cross-references
- README.md now explains standalone pip installation vs. development clone
- Legacy docs (COMPONENT_TAG.md, VIEWFLOW_MAPPING.md) redirected to new numbered names

### Deprecated
- docs/DOCUMENTATION_MAP.md — superseded by docs/INDEX.md (DF-000)

### Removed
- Empty doc stub directories
- Broken symlink (django-fusion) at repo root

---

## [0.1.0] — 2024-[MM-DD]

Initial public release.

### Features
- Component system (RoutableComponent, FragmentComponent)
- Routing helpers (Site, Application, Viewset, route)
- Form/table mixins (FormMixin, TableMixin, FormTableMixin)
- Caching (CachedManager)
- Health checks (HealthCheckView)
- Wagtail integration (blocks, snippets, viewsets)
- Component tag ({% comp %})
- Template tag loading and resolution
- HTMX fragment detection

---

See [docs/INDEX.md](./docs/INDEX.md) for documentation.
EOF

# 2. Commit
git add CHANGELOG.md
git commit -m "Phase 4: Add CHANGELOG.md (Keep a Changelog format)

Initial changelog seeded with unreleased changes from this execution phase.
Maintainers should update for each release."
```

**Validate:**
- CHANGELOG.md follows Keep a Changelog format
- Entries reference DF-NNNN doc IDs where applicable

**Save output to:** `reports/phase-4-changelog-added.txt`

### 4.4 — Update pyproject.toml for Publishing

```bash
# From repo root

# 1. Backup current pyproject.toml
cp pyproject.toml pyproject.toml.bak

# 2. Update [project] section
python3 <<'PYEOF'
import toml

with open("pyproject.toml") as f:
    config = toml.load(f)

# Ensure [project] section exists
if "project" not in config:
    config["project"] = {}

project = config["project"]

# Add missing metadata
project["license"] = {"text": "MIT"}
project["readme"] = "README.md"
project["authors"] = [
    {"name": "Structa Cloud Team", "email": "dev@structa.cloud"}
]
project["classifiers"] = [
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "Framework :: Django :: 4.2",
    "Framework :: Django :: 5.0",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

# Add repository URLs
if "urls" not in project:
    project["urls"] = {}
project["urls"]["Homepage"] = "https://github.com/mammhoud/django-fusion"
project["urls"]["Repository"] = "https://github.com/mammhoud/django-fusion.git"
project["urls"]["Documentation"] = "https://github.com/mammhoud/django-fusion/tree/generic/docs"
project["urls"]["Issues"] = "https://github.com/mammhoud/django-fusion/issues"

# Write back
with open("pyproject.toml", "w") as f:
    toml.dump(config, f)

print("✅ pyproject.toml updated with publishing metadata")
PYEOF

# 3. Verify the update
echo "=== Updated [project] section ===" && \
  grep -A 30 '^\[project\]' pyproject.toml

# 4. Commit
git add pyproject.toml
git commit -m "Phase 4: Update pyproject.toml for PyPI publishing

Add license, readme, authors, classifiers, and repository URLs.
Library is now ready to publish to PyPI."
```

**Validate:**
- `pyproject.toml` has `license`, `readme`, `authors`, `classifiers` fields
- Repository URLs are correct
- No syntax errors (test with `python -c "import tomllib; tomllib.loads(open('pyproject.toml').read())"`)

**Save output to:** `reports/phase-4-pyproject-updated.txt`

### 4.5 — Add GitHub Workflow for CI

```bash
# From repo root

mkdir -p .github/workflows

cat > .github/workflows/tests.yml <<'EOF'
name: Tests

on:
  push:
    branches: [generic]
  pull_request:
    branches: [generic]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        django-version: ["4.2", "5.0"]

    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install "Django~=${{ matrix.django-version }}"
          pip install -e ".[test]"

      - name: Run tests
        run: |
          pytest --cov=src/django_fusion --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
          fail_ci_if_error: false
EOF

# 2. Commit
git add .github/workflows/tests.yml
git commit -m "Phase 4: Add GitHub Actions CI workflow

Runs pytest on Python 3.11–3.12, Django 4.2–5.0.
Uploads coverage to Codecov.

Tests run on every push/PR to generic branch."
```

**Validate:**
- `.github/workflows/tests.yml` exists and is valid YAML
- Workflow runs on `generic` branch (not `main`)
- Python and Django versions match `pyproject.toml`

**Save output to:** `reports/phase-4-ci-workflow-added.txt`

---

## PHASE 5: Documentation String Audit & API Reference (45–90 min)

**Goal:** Ensure all public classes/functions have docstrings, and generate API reference (DF-008).

### 5.1 — Audit Public Symbols for Missing Docstrings

```bash
# From repo root

python3 <<'PYEOF'
import ast
import os
from pathlib import Path

def find_undocumented(root_dir, exclude_test=True):
    """Find public functions/classes without docstrings."""
    undocumented = []
    
    for path in Path(root_dir).rglob("*.py"):
        if exclude_test and "test" in str(path):
            continue
        
        try:
            with open(path) as f:
                tree = ast.parse(f.read())
        except SyntaxError:
            continue
        
        for node in ast.walk(tree):
            # Check top-level classes and functions
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                # Skip private/magic
                if node.name.startswith("_"):
                    continue
                
                # Check for docstring
                docstring = ast.get_docstring(node)
                if not docstring:
                    undocumented.append((path, node.name, type(node).__name__))
    
    return undocumented

# Run audit
results = find_undocumented("src/django_fusion")

if results:
    print("=== Undocumented Public Symbols ===")
    for path, name, kind in sorted(results):
        print(f"  {path}: {kind} {name}")
else:
    print("✅ All public symbols have docstrings")

# Save for Phase 5.2
with open("reports/undocumented-symbols.txt", "w") as f:
    for path, name, kind in results:
        f.write(f"{path}: {kind} {name}\n")
PYEOF
```

**Validate & Save:**
- List all undocumented symbols in `reports/undocumented-symbols.txt`
- Use this list in Phase 5.2 to prioritize docstring additions

**Save output to:** `reports/phase-5-docstring-audit.txt`

### 5.2 — Add Missing Docstrings (Prioritized)

For each undocumented symbol in `reports/undocumented-symbols.txt`:

```bash
# Example: add docstring to a class

# 1. Identify the class/function location
grep -n "class ComponentRegistry" src/django_fusion/comp/registry.py

# 2. Edit the file and add a docstring
cat src/django_fusion/comp/registry.py | head -40
# (Add docstring to the class definition)

# 3. After updating all undocumented symbols, commit
git add src/
git commit -m "Phase 5: Add missing docstrings to public API

Documented all public classes/functions per API reference (DF-008) requirements.
Symbols documented:
  - ComponentRegistry
  - RoutableComponent
  - FragmentComponent
  - [... etc]

Closes undocumented-symbols audit."
```

This is a mechanical but important task. Focus on the most commonly-used classes first (ComponentRegistry, RoutableComponent, FragmentComponent).

**Validate:**
- Re-run the docstring audit; undocumented count should be 0 or very small

**Save output to:** `reports/phase-5-docstrings-added.txt`

### 5.3 — Generate API Reference (DF-008)

Use the **PR-07** prompt from the companion doc §3.8, or generate programmatically:

```bash
# From repo root

python3 <<'PYEOF'
import ast
import inspect
from pathlib import Path

# Canonical imports from AGENTS.md (manually copied here for reference)
canonical_paths = [
    "src/django_fusion/comp/routes",
    "src/django_fusion/comp/generic",
    "src/django_fusion/projects/handlers",
    "src/django_fusion/projects/managers",
    "src/django_fusion/projects/models",
    "src/django_fusion/projects/services",
    "src/django_fusion/web/views",
    "src/django_fusion/comp/loaders",
    "src/django_fusion/projects/middlewares",
    "src/django_fusion/comp/cache",
]

# Generate markdown for each canonical path
output = ["# API Reference (DF-008)\n"]

for path in canonical_paths:
    output.append(f"\n## `{path}`\n")
    
    # Find .py files in this path
    path_obj = Path(path)
    if not path_obj.exists():
        output.append(f"> Module not found: {path}\n")
        continue
    
    for py_file in path_obj.glob("*.py"):
        if py_file.name.startswith("_"):
            continue
        
        # Extract public classes and functions
        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())
        except SyntaxError:
            continue
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                docstring = ast.get_docstring(node) or "[No docstring]"
                output.append(f"\n### `{node.name}`\n\n{docstring}\n")
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                docstring = ast.get_docstring(node) or "[No docstring]"
                output.append(f"\n### `{node.name}()`\n\n{docstring}\n")

# Write output
with open("docs/08-api-reference.md", "w") as f:
    f.write("\n".join(output))

print(f"✅ Generated docs/08-api-reference.md with {len(output)} sections")
PYEOF

# Commit
git add docs/08-api-reference.md
git commit -m "Phase 5: Generate API reference (DF-008)

Programmatically extracted docstrings from all public symbols
in canonical import paths (from AGENTS.md).

DF-008: docs/08-api-reference.md"
```

**Validate:**
- `docs/08-api-reference.md` exists and contains real class/function signatures
- No '[No docstring]' entries, or if present, flag those symbols for manual docstring addition

**Save output to:** `reports/phase-5-api-reference-generated.txt`

---

## PHASE 6: Testing & Quality Assurance (30–60 min)

**Goal:** Ensure all tests pass and coverage is acceptable.

### 6.1 — Run Full Test Suite Locally

```bash
# From repo root

# 1. Run all tests
pytest --verbose --tb=short

# 2. Generate coverage report
pytest --cov=src/django_fusion --cov-report=term-missing --cov-report=html

# 3. Check coverage threshold (e.g., 80%)
coverage report --fail-under=80 || echo "Coverage below threshold"

# 4. View HTML report
open htmlcov/index.html  # macOS
# or: xdg-open htmlcov/index.html  # Linux
```

**Validate:**
- All tests pass (0 failures)
- Coverage is above 80% (or whatever target is set)
- No unexpected deprecation warnings

**Save output to:** `reports/phase-6-test-suite.txt`

### 6.2 — Verify Documentation Links

```bash
# Check that all doc references are valid

python3 <<'PYEOF'
import re
from pathlib import Path

broken = []

for doc_file in Path("docs").glob("*.md"):
    with open(doc_file) as f:
        content = f.read()
    
    # Find all markdown links
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, url in links:
        # Skip external URLs
        if url.startswith("http"):
            continue
        
        # Check if file exists
        target = Path("docs") / url
        if not target.exists():
            broken.append((doc_file, url, text))

if broken:
    print("=== Broken Documentation Links ===")
    for doc_file, url, text in broken:
        print(f"  {doc_file}: [{text}]({url})")
else:
    print("✅ All documentation links are valid")
PYEOF
```

**Validate:**
- No broken links in docs/
- All `DF-NNNN` IDs in docs/INDEX.md point to real files

**Save output to:** `reports/phase-6-doc-links-check.txt`

### 6.3 — Verify Package Can Be Installed

```bash
# From a temporary directory (to test without local imports)

cd /tmp
python -m venv test_env
source test_env/bin/activate

# Install from the repo
pip install /path/to/django-fusion

# Import and check basic functionality
python3 <<'PYEOF'
import django_fusion
print(f"✅ django_fusion imported successfully")
print(f"   Version: {getattr(django_fusion, '__version__', 'unknown')}")

# Import key modules
from django_fusion.comp.routes import RoutableComponent
from django_fusion.core.managers import CachedManager
from django_fusion.health.views import HealthCheckView

print("✅ All key modules import without errors")
PYEOF

# Clean up
deactivate
rm -rf test_env
```

**Validate:**
- Package installs successfully
- No import errors on core modules

**Save output to:** `reports/phase-6-package-install-test.txt`

---

## PHASE 7: Library Push & Release (30–45 min)

**Goal:** Push all changes to GitHub and tag a new release.

### 7.1 — Prepare Release Commit

```bash
# From repo root

# 1. Verify all changes are staged
git status

# 2. Final review of CHANGELOG.md
cat CHANGELOG.md | head -50

# 3. Update version in __init__.py (if there's a version string)
# Example: __version__ = "0.2.0"
grep -rn "__version__" src/django_fusion/ | head -5

# 4. Create a final "ready for release" commit
git add -A
git commit -m "Release: v0.2.0 — Full documentation & hygiene pass

### Features
- Complete documentation index (DF-000) and 15 doc files (DF-001–DF-015)
- License (MIT), CONTRIBUTING.md, CHANGELOG.md
- GitHub Actions CI (.github/workflows/tests.yml)
- Updated pyproject.toml for PyPI publishing
- Fixed standalone repo paths (removed monorepo references)

### Fixes
- Fixed documentation index — no dead links
- Removed broken symlink
- Added missing docstrings to public API
- Generated API reference from source

### Quality
- All tests passing (coverage > 80%)
- All documentation links valid
- Package installs and imports without errors

See CHANGELOG.md for details.

Closes django-fusion-enhancements.md full execution."
```

**Validate:**
- Commit message is clear and references both enhancements and specific fixes
- All files are staged (git status clean)

**Save output to:** `reports/phase-7-release-commit.txt`

### 7.2 — Push to generic Branch

```bash
# From repo root

# Requires GITHUB_TOKEN set in .env or env var

# 1. Verify token is available
if [ -z "$GITHUB_TOKEN" ]; then
  echo "❌ GITHUB_TOKEN not set"
  exit 1
fi

# 2. Dry-run first
echo "=== Dry-run: what would be pushed ===" && \
  git push --dry-run origin generic 2>&1 | head -30

# 3. Actual push
git push origin generic

# 4. Verify push succeeded
git ls-remote origin refs/heads/generic | head -1
```

**Validate:**
- Push completes without errors
- Remote commit matches local (same SHA-1)

**Save output to:** `reports/phase-7-push-generic.txt`

### 7.3 — Create Release Tag (Optional)

```bash
# From repo root

# 1. Create an annotated tag
git tag -a v0.2.0 -m "Release v0.2.0

Full documentation, project hygiene, and PyPI publishing readiness.

See CHANGELOG.md for detailed changes."

# 2. Push the tag
git push origin v0.2.0

# 3. Verify on GitHub
echo "✅ Tag pushed. See: https://github.com/mammhoud/django-fusion/releases"
```

**Validate:**
- Tag appears on GitHub Releases page
- Release notes are auto-populated from tag message

**Save output to:** `reports/phase-7-release-tag.txt`

---

## PHASE 8: PyPI Publishing (Optional, requires PyPI account)

**Goal:** Publish the library to PyPI so users can `pip install django-fusion`.

### 8.1 — Build Distribution Packages

```bash
# From repo root

# 1. Install build tools
pip install build twine

# 2. Build sdist (source) and wheel (binary)
python -m build

# 3. Check output
ls -lh dist/
# Should show:
#   django_fusion-0.2.0-py3-none-any.whl
#   django_fusion-0.2.0.tar.gz
```

**Validate:**
- Both `.whl` and `.tar.gz` files exist
- File sizes are reasonable (not bloated)

**Save output to:** `reports/phase-8-build.txt`

### 8.2 — Test Publish to PyPI Test Server (optional, but recommended)

```bash
# 1. Get a PyPI test account at https://test.pypi.org/

# 2. Store credentials in ~/.pypirc or use token
#    (See PyPI docs for authentication methods)

# 3. Upload to test server
twine upload --repository testpypi dist/*

# 4. Test installation from test server
pip install -i https://test.pypi.org/simple/ django-fusion==0.2.0
```

**Validate:**
- Test upload succeeds
- Package is installable from test server

**Save output to:** `reports/phase-8-test-pypi.txt`

### 8.3 — Publish to PyPI Production

```bash
# 1. Upload to production PyPI
twine upload dist/*

# 2. Verify on PyPI
echo "✅ Published. See: https://pypi.org/project/django-fusion/"

# 3. Test installation from production
pip install django-fusion==0.2.0
```

**Validate:**
- Upload succeeds
- Package appears on pypi.org/project/django-fusion/
- Installation works: `pip install django-fusion`

**Save output to:** `reports/phase-8-pypi-published.txt`

---

## PHASE 9: Documentation Finalization & Archive (15–30 min)

**Goal:** Archive all reports and prepare for future iterations.

### 9.1 — Create Execution Summary

```bash
# From repo root

cat > reports/EXECUTION-SUMMARY.md <<'EOF'
# Full Execution Summary — django-fusion

**Date:** [execution date]
**Branch:** generic
**Version:** v0.2.0 (released to PyPI)
**Duration:** [total time across all phases]

## Phases Completed

- ✅ Phase 0: Baseline Audit
- ✅ Phase 1: Docs Index & Consolidation
- ✅ Phase 2: Root-level File Cleanup
- ✅ Phase 3: Documentation Creation (DF-001–DF-015)
- ✅ Phase 4: Project Hygiene (LICENSE, CONTRIBUTING, CI)
- ✅ Phase 5: API Reference & Docstrings
- ✅ Phase 6: Testing & QA
- ✅ Phase 7: Push & Release Tag
- ✅ Phase 8: PyPI Publishing
- ✅ Phase 9: Finalization

## Key Achievements

1. **Documentation restructured**: 15 files (DF-001–DF-015) with stable IDs
2. **Project hygiene**: Added LICENSE (MIT), CONTRIBUTING.md, CHANGELOG.md
3. **CI/CD ready**: GitHub Actions workflow for testing on Python 3.11–3.12, Django 4.2–5.0
4. **API documented**: Auto-generated API reference from docstrings
5. **PyPI published**: Library available via `pip install django-fusion`

## Files Changed

- Added: 15 doc files (docs/01-*.md through 15-*.md)
- Added: LICENSE, CONTRIBUTING.md, CHANGELOG.md, .github/workflows/tests.yml
- Removed: Broken symlink, empty stub dirs
- Updated: README.md, AGENTS.md, PROMPTS.md, pyproject.toml
- Archived: docs/DOCUMENTATION_MAP.md → docs/legacy/

## Quality Metrics

- Tests: All passing (0 failures)
- Coverage: > 80%
- Documentation: All links valid, no dead references
- Package: Installs successfully from PyPI

## Next Steps for Maintainers

1. Monitor GitHub Issues for questions about new docs
2. Update DF-0NN docs as features are added/changed
3. Maintain DF-NNNN → PR-NN mapping for reproducibility
4. Plan Phase 2: library improvements (additional features, optimizations)

---

See `reports/` for detailed phase logs.
EOF

git add reports/EXECUTION-SUMMARY.md
git commit -m "Phase 9: Add execution summary for django-fusion v0.2.0"
```

### 9.2 — Update CHANGELOG.md with Release Date

```bash
# Update [Unreleased] section to [0.2.0] with date

sed -i 's/## \[Unreleased\]/## [0.2.0] — 2024-[MM-DD]/' CHANGELOG.md

git add CHANGELOG.md
git commit -m "Phase 9: Backfill release date in CHANGELOG.md"
```

### 9.3 — Create Maintenance Guide

```bash
# Create a guide for future maintainers

cat > MAINTENANCE.md <<'EOF'
# Maintenance Guide — django-fusion

## Making Updates

### Adding a New Feature

1. Create a branch: `feature/my-feature`
2. Implement the feature in `src/django_fusion/`
3. Add tests in `tests/`
4. Run `pytest` to verify
5. If adding a new module/class, update the relevant `DF-0NN` doc
6. Update `CHANGELOG.md` under `[Unreleased]` section
7. Create a PR with reference to the relevant `DF-NNNN` and `PR-NN` IDs
8. After merge, bump version in `src/django_fusion/__init__.py`

### Releasing a New Version

1. Update version in `src/django_fusion/__init__.py` (e.g., `__version__ = "0.3.0"`)
2. Update `CHANGELOG.md`: change `[Unreleased]` to `[0.3.0] — YYYY-MM-DD`
3. Commit: `git commit -m "Release: v0.3.0"`
4. Tag: `git tag -a v0.3.0 -m "Release v0.3.0\n\n[changelog summary]"`
5. Push: `git push origin generic && git push origin v0.3.0`
6. Publish to PyPI: `python -m build && twine upload dist/*`

### Documentation

All documentation uses the `DF-NNNN` numbering system:
- `DF-000`: docs/INDEX.md (the map)
- `DF-001–015`: Individual doc files

When **updating a doc**:
1. Edit the file (e.g., docs/03-component-system.md)
2. Reference the PR that prompted the change in the commit (e.g., "Updates to DF-003 per PR-03")
3. Ensure all code examples are current (pull from source, not old docs)

When **adding a doc**:
1. Get the next free `DF-NNNN` ID from docs/INDEX.md
2. Create the file (e.g., docs/16-new-topic.md)
3. Add a row to docs/INDEX.md with status 🟡 TODO
4. Update the row to ✅ Exists once the content is complete
5. Commit referencing the new ID

### Testing

- Run `pytest` locally before pushing
- CI will run on all PRs (GitHub Actions)
- Keep coverage above 80%

### Code Style

- Format: `black src/ tests/`
- Lint: `ruff check src/ tests/`
- Test: `pytest --cov=src/django_fusion`

---

For contributor guidelines, see `CONTRIBUTING.md`.
EOF

git add MAINTENANCE.md
git commit -m "Phase 9: Add MAINTENANCE.md for future maintainers"
```

### 9.4 — Final Checklist

```bash
# Verify everything is in order

cat > reports/FINAL-CHECKLIST.md <<'EOF'
# Final Checklist — django-fusion Full Execution

Before considering this execution complete, verify:

## Documentation
- [ ] `docs/INDEX.md` (DF-000) exists and is complete
- [ ] All DF-0NN files referenced in INDEX exist (no 🟡 TODO marked as ✅ Exists)
- [ ] All documentation links are valid (`grep -rn "\.md"` finds no 404s)
- [ ] docs/COMPONENT_TAG.md and VIEWFLOW_MAPPING.md redirect to new numbered files

## Project Files
- [ ] `README.md` shows `pip install django-fusion` (not monorepo paths)
- [ ] `LICENSE` exists and is the correct open-source license
- [ ] `CONTRIBUTING.md` explains dev setup and testing
- [ ] `CHANGELOG.md` has release notes for v0.2.0
- [ ] `pyproject.toml` has license, readme, authors, classifiers, repository URLs
- [ ] `.github/workflows/tests.yml` exists and runs on generic branch
- [ ] `MAINTENANCE.md` guides future maintainers

## Code Quality
- [ ] All tests pass: `pytest` returns 0 failures
- [ ] Coverage > 80%: `pytest --cov` report is above threshold
- [ ] No import errors: `python -c "import django_fusion; from django_fusion.comp.routes import *"`
- [ ] Docstrings complete: No undocumented public symbols (or documented in Phase 5.2)
- [ ] API reference generated: `docs/08-api-reference.md` exists with real docstrings

## Repository State
- [ ] On `generic` branch
- [ ] No uncommitted changes: `git status` is clean
- [ ] All changes pushed: `git ls-remote origin refs/heads/generic` shows latest commit
- [ ] Release tag created: `git tag -l | grep v0.2.0`

## PyPI (if published)
- [ ] `python -m build` produces `.whl` and `.tar.gz` files
- [ ] `pip install django-fusion` installs successfully from PyPI
- [ ] https://pypi.org/project/django-fusion/ shows v0.2.0

## Submodule Status (if in monorepo)
- [ ] `applications/libs/django-fusion` is on `generic` branch
- [ ] Submodule points to correct commit (verified with `git submodule status`)
- [ ] No divergence from remote

---

If all items are checked, the execution is complete and the library is production-ready.

**Signed off by:** [maintainer name]  
**Date:** [date]
EOF

cat reports/FINAL-CHECKLIST.md
```

---

## QUICK REFERENCE: All Phase Outputs

To find reports from any phase:

```bash
ls -1 reports/phase-*.txt reports/*.md
```

Key summary files:
- `reports/EXECUTION-SUMMARY.md` — Overall status
- `reports/FINAL-CHECKLIST.md` — Sign-off criteria
- `docs/INDEX.md` — Living documentation map (DF-000)

---

## Troubleshooting

**Phase fails at docs creation?**
- Verify source modules exist in `src/django_fusion/`
- Use the PR-NN prompts from `django-fusion-enhancements.md` §3 as guidance
- Ask an AI agent to generate content from the prompt specification

**Tests fail?**
- Check `pytest` output for import/configuration errors
- Verify Django is installed: `python -c "import django; print(django.__version__)"`
- Run `DJANGO_DEBUG_CONFTEST=1 pytest tests/ -v` for extra logging (see CONTRIBUTING.md)

**PyPI publish fails?**
- Check credentials in `~/.pypirc` or `TWINE_TOKEN` env var
- Verify version number in `pyproject.toml` matches tag
- Try test server first (Phase 8.2) to debug

---

**Document version:** 1.0  
**Last updated:** [date]  
**Maintainer:** [name/team]
