# Changelog

## 2026-07-01 — docs cross-link sweep + CI gates

### docs: fix every broken relative cross-link in legacy READMEs

- `core/libs/django-fusion/docs/legacy-django-fusion/README.md`
  - Line 65: stale `venv/libs/…` path corrected to `../../README.md`
  - Line 71: `[ceptor-ai](../ceptor-ai/)` corrected to `[ceptor-ai](../../../ceptor-ai/)`
  - Line 73: removed broken `[django-fusion](../django-fusion/)` (target `docs/django-fusion/` absent)
  - Renamed "Related Packages" → "Related Package" (singular — the monorepo has exactly two libs)
- `core/libs/ceptor-ai/docs/legacy-django-rseal/README.md`
  - Line 77: `../../../venv/libs/ceptor-ai/README.md` → `../../README.md`
  - Line 80: `../django-fusion/` → `../../../django-fusion/`
  - Line 81: removed duplicate broken link with stale "Testing infrastructure" description
- `core/libs/django-fusion/docs/legacy-django-grep/hypothesis.md`
  - Line 57: removed dead `[Auth Testing](../auth/testing.md)` link
- `core/libs/django-fusion/docs/legacy-django-fusion/django-allauth.md`
  - Lines 24, 50: removed dead `[Auth Adapter](../auth/adapter.md)` and `[Auth Templates](../auth/templates.md)` links
- `core/libs/ceptor-ai/docs/legacy-ceptor-ai/README.md`
  - Quick Start: stale `CraftsClient` → `CeptorClient` (matching actual `ceptor_ai.chat.client` API)
  - `ChatBubble(client=client)` → `ChatBubble(server_url=…)` (matching actual constructor kwarg)
  - Install extras: `openai`, `anthropic`, `faker` → `mcp`, `test` (matching `pyproject.toml` `[project.optional-dependencies]`)

### feat: CI gates for docs validation

- **`core/scripts/check_markdown_links.py`** — validates every Markdown filesystem-relative link + HTTP HEAD (stdlib-only, Python 3.11+ for tomllib). Exit 0 clean / 1 broken / 2 bad interpreter.
- **`core/scripts/check_extras_in_docs.py`** — validates every `uv add "pkg[extras]"` / `pip install "pkg[extras]"` line against the corresponding `pyproject.toml` `[project.optional-dependencies]`. Exit 0 clean / 1 drift / 2 bad interpreter.
- **`.github/workflows/deploy-ci.yml`** — added `markdown-links` job (Python 3.11, runs `check_markdown_links.py`) triggered on `core/libs/**/*.md` changes. Deleted the now-redundant standalone `.github/workflows/check-links.yml`.
- **`.github/workflows/check-extras.yml`** — runs `check_extras_in_docs.py` (Python 3.11) on PRs touching `core/libs/**/*.md`, `**/pyproject.toml`, or the script itself.

### feat: test scaffolding

- `core/libs/django-fusion/tests/django_grep/test_ceptor_ai/conftest.py` — wires `apps/libs/ceptor-ai/src` onto `sys.path` for the renamed `test_ceptor_ai.py`.
- `core/libs/django-fusion/tests/test_register_include_path_render_equivalence.py` — lights-up test confirming render equivalence across `{% include %}`, `{% comp "path" /%}`, and `{% comp name /%}`.

### fix: `_LazyIncludeTemplate.template` returns inner `django.template.Template`

- `core/libs/django-fusion/src/django_fusion/comp/registry.py` — fixed `_LazyIncludeTemplate.template` to return the inner `django.template.Template` (matching the layer that has `.nodelist`) instead of the outer `DjangoTemplate` wrapper. All four consumer sites (`Component.nodelist`, `Component.path`, `Component.source`, `BoundComponent.render`) now converge through the same path the eager `from_name` resolution always used.

### rename: legacy codenames → actual package names

- `test_nawaai/` → `test_ceptor_ai/`, `legacy_crafts_ai/` → `legacy_ceptor_ai/`, `legacy-crafts-ai/` → `legacy-ceptor-ai/` (directories)
- Removed empty `ceptor-ai/crafts-ai/` dir (the only empty dir in libs)
- 13 source files swept: `nawaai` → `ceptor-ai`, `crafts_ai`/`craftsai`/`crafts-ai`/`crafts.ai` → `ceptor_ai`/`ceptor-ai`

## 2026-06-30 — template reorganization, settings inlining, test fixes

See commit `10aa572d`.
