# 🏗️ Repo Infrastructure Changelog

> Infrastructure and monorepo restructuring changes extracted from the real repo `CHANGELOG.md`.

---

## 2026-07-19 — Infrastructure Restructuring + Documentation

### restructure: `core/` → `projects/` + `libs/` move to repo root

Complete monorepo reorganization for standard conventions:

| Old Path | New Path | Reason |
|----------|----------|--------|
| `core/` | `projects/` | Clearer monorepo project root |
| `core/libs/django-fusion` | `libs/django-fusion` | Libraries at repo root |
| `core/libs/ceptor-ai` | `libs/ceptor-ai` | Standard submodule convention |
| `core/lms-demo/` | `projects/lms/` | Shorter, canonical name |
| `core/VResume/` | `projects/portfolio/` | Descriptive project name |
| `core/tinker/` | `projects/cypercloud/` | New brand for AI customizer |

**Impacts:**
- `.gitmodules` — submodule paths updated accordingly
- `.dockerignore` — all paths updated for new layout
- `.github/workflows/` — working-directory and paths updated
- Root `Makefile` — all directory vars updated (`CORE_DIR := projects`)
- `AGENTS.md` — all canonical paths rewritten

### docs: project documentation overhaul

- All 61+ project READMEs enhanced with consistent structure
- `docs/recent-changes.md` updated with restructuring details
- `docs/features/` updated with POS-KO and edition features
- `docs/_sidebar.md` and `mkdocs.yml` updated for new pages
- All `AGENTS.md` files updated with new canonical paths

---

## 2026-07-01 — Docs Cross-Link Sweep + CI Gates

### docs: fix every broken relative cross-link in legacy READMEs

Fixed broken links across all library documentation:
- `libs/django-fusion/docs/legacy-*/` — 5 links fixed or removed
- `libs/ceptor-ai/docs/legacy-*/` — 3 links fixed, API names corrected
  - `CraftsClient` → `CeptorClient`
  - `ChatBubble(client=…)` → `ChatBubble(server_url=…)`
  - Extras: `openai, anthropic, faker` → `mcp, test`

### feat: CI gates for docs validation

| Script | Purpose |
|--------|---------|
| `application/scripts/check_markdown_links.py` | Validates every Markdown relative + HTTP link |
| `application/scripts/check_extras_in_docs.py` | Validates `pyproject.toml` extras match docs |

### feat: test scaffolding

- `libs/django-fusion/tests/test_register_include_path_render_equivalence.py` — render equivalence across `{% include %}`, `{% comp "path" /%}`, and `{% comp name /%}`
- `libs/django-fusion/tests/django_grep/test_ceptor_ai/` — ceptor-ai integration tests

### fix: `_LazyIncludeTemplate.template`

Fixed to return inner `django.template.Template` (with `.nodelist`) instead of outer `DjangoTemplate` wrapper — all four consumer sites now converge through the same path.

### rename: legacy codenames → actual package names

- `test_nawaai/` → `test_ceptor_ai/`
- `legacy_crafts_ai/` → `legacy_ceptor_ai/`
- `crafts_ai`/`crafts.ai` → `ceptor_ai`/`ceptor-ai`
- 13 source files swept, empty `ceptor-ai/crafts-ai/` dir removed

---

## 2026-06-30 — Template Reorganization + Settings Inlining

### template cleanup

- **Deduplicated 60+ template files** — consolidated `errors/`, `newsletter/`, `privacy/`, `mfa/` into `plugins/` equivalents
- **Merged `LMS/` → `lms/`** (Linux case-sensitivity fix)
- **Consolidated `email/` unique files** into `plugins/emails/`
- **Kept `emails/` and `components/pagination/`** as backwards-compatible mirrors (117+ `render_to_string("emails/...")` references)

### settings inlining

Per-site Django settings inlined with Dynaconf — each site has its own `configs/settings.yml` + `settings.development.yml` + `settings.production.yml`.

---

## Related

| Topic | Path |
|-------|------|
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
| POS changelog | [`pos.md`](pos.md) |
| Libs changelog | [`libs.md`](libs.md) |
| Infrastructure | [`../infrastructure/`](../infrastructure/) |
