# django-fusion — Enhancement & Documentation Recovery Plan

Repo: [mammhoud/django-fusion](https://github.com/mammhoud/django-fusion) (default branch: `generic`)
Reviewed: file tree, `README.md`, `AGENTS.md`, `PROMPTS.md`, `QUICKSTART.md`, `pyproject.toml`, `src/django_fusion/__init__.py`, everything under `docs/`.

## TL;DR

The code is large and clearly organized (`analyzer/`, `comp/`, `projects/`, `contrib/`, `health/`, `infrastructure/`, `site/`, `wagtail/`, `web/`, 37 test modules), but the **documentation layer is almost entirely aspirational**. `docs/INDEX.md` and `docs/DOCUMENTATION_MAP.md` list ~25 documents and mark most of them "✅ Complete" — but only **5 of those files actually exist** in `docs/`. Every entry-point file (`README.md`, `AGENTS.md`, `PROMPTS.md`, `QUICKSTART.md`) links to docs that 404. That's the single highest-leverage fix available. Alongside it, the repo is missing standard OSS hygiene (license, CI, contributing guide, changelog) and has a leftover monorepo artifact (a broken symlink at the repo root) that will confuse anyone who clones it standalone.

---

## 1. Critical findings

### 1.1 Documentation references ~20 files that don't exist
`docs/` contains only:
- `INDEX.md`
- `DOCUMENTATION_MAP.md`
- `COMPONENT_TAG.md`
- `COMPONENT_CASE_STUDIES.md`
- `VIEWFLOW_MAPPING.md`
- `legacy-django-grep/django-grep-overview.md`

But `INDEX.md`, `DOCUMENTATION_MAP.md`, `AGENTS.md`, `PROMPTS.md`, and `QUICKSTART.md` collectively link to: `GETTING_STARTED.md`, `ARCHITECTURE_OVERVIEW.md`, `COMPONENT_SYSTEM.md`, `ROUTING_SYSTEM.md`, `TEMPLATE_STRUCTURE.md`, `FORMS_TABLES_INTEGRATION.md`, `ANALYZER_MODULE.md`, `TEMPLATE_TRACKING.md`, `API_REFERENCE.md`, `CONFIGURATION.md`, `NAMESPACE_REFERENCE.md`, `INTEGRATION_EXAMPLES.md`, `BEST_PRACTICES.md`, `WEBSITES_VRESUME.md`, `WEBSITES_CTC.md`, `WEBSITES_LMS.md`, `FAQ.md`, `TROUBLESHOOTING.md`, `CONTRIBUTING.md`, `TEMPLATE_COMPONENTS_INDEX.md`, `COMPONENT_ANALYZER.md`, `FRAGMENT_COMPONENTS.md`, `HEALTH.md`, `WAGTAIL_INTEGRATION.md`, `EXAMPLES_FORMS.md`, `EXAMPLES_TABLES.md`.

`DOCUMENTATION_MAP.md` goes further and self-certifies coverage tables ("Getting Started — ✅ Complete", "Architecture — ✅ Complete", "Configuration — ✅ Complete") for files that are not in the repo. This is worse than having no docs at all — it actively misleads a new contributor (or an AI coding agent following `AGENTS.md`) into believing reference material exists when it doesn't. Anyone using `AGENTS.md` as a system prompt for an AI agent will send that agent chasing dead links.

### 1.2 Broken root-level artifact
A file named `django-fusion` at the repo root is a **broken symbolic link** pointing to `/app/libs/django-fusion` — clearly a leftover from wherever this package was extracted out of a monorepo. It serves no purpose in a standalone repo and will show up as a broken link/error for anyone who clones and inspects the tree.

### 1.3 README doesn't match the actual scope of the package
`README.md` is 18 lines and describes 3 features (cached managers, one middleware, "smart loader decorator"). `src/django_fusion/__init__.py`'s docstring describes 9 top-level modules and dozens of submodules (component system with props/slots/HTMX, Wagtail integration, allauth adapters, Dynaconf multi-env config, health checks, an analyzer/scanner app, Pydantic response schemas, and more). A visitor reading only the README has no idea this is a full "mini-framework" on top of Django — undersells the project and gives no path into the real capability surface.

### 1.4 Install instructions assume a monorepo path that doesn't exist in this repo
`README.md` says `pip install -e application/libs/django-fusion`, and `AGENTS.md`/`PROMPTS.md` reference paths like `application/libs/django-fusion/docs/...`. In this standalone repo, the package root *is* the repo root (`pyproject.toml`, `src/django_fusion/` live at top level) — there is no `application/libs/django-fusion` directory here. These docs were written for the internal Structa Cloud monorepo and not adapted for the public extraction.

### 1.5 No project hygiene files
- No `LICENSE` — a public repo with no license is "all rights reserved" by default; nobody can legally use/fork/contribute to it as intended.
- No CI (`.github/workflows/`) — 37 test files exist under `tests/` (`pytest` is even configured in `pyproject.toml`) but nothing runs them automatically on push/PR.
- No `CONTRIBUTING.md` (despite being linked from `docs/INDEX.md`).
- No `CHANGELOG.md` — version is pinned at `0.1.0` with no way to see what changed between commits/releases.
- No lint/format config (ruff/black/isort) or pre-commit hooks, despite a codebase this size.
- `pyproject.toml` has no `license`, `readme`, `authors`, `classifiers`, or `urls` (`Homepage`/`Repository`) fields — not PyPI-publish-ready as-is.

### 1.6 Minor
- Default branch is `generic`, not `main`/`master` — unusual and worth a one-line explanation somewhere (or renaming) so newcomers aren't confused about which branch is canonical.
- No badges (build status, license, PyPI, coverage) on the README — cheap signal of project health that's currently absent.

---

## 2. Recommended priorities

| Priority | Item | Why |
|---|---|---|
| P0 | Reconcile `docs/INDEX.md` + `docs/DOCUMENTATION_MAP.md` with reality (write the missing files or delete the dead links) | Actively misleading right now; breaks `AGENTS.md`-driven AI workflows and human onboarding alike |
| P0 | Remove the broken `django-fusion` symlink | Trivial fix, visibly broken |
| P0 | Add `LICENSE` | Legal prerequisite for reuse/contribution |
| P1 | Add CI (`.github/workflows/tests.yml`) running the existing `pytest` suite | Tests exist and are unused — free safety net |
| P1 | Rewrite root `README.md` to reflect actual scope + fix the install path | First impression / onboarding |
| P1 | Add `CONTRIBUTING.md` | Already promised by `docs/INDEX.md` |
| P2 | Add `CHANGELOG.md`, PyPI-readiness metadata in `pyproject.toml`, badges | Polish, not blocking |
| P2 | Add lint/format config + pre-commit | Maintainability |

---

## 3. Prompt library

These are ready-to-paste prompts (for Claude, another AI coding agent, or a human writer) to close each gap. They follow the same `Prompt / Expected Input / Expected Output / Doc References` shape already used in the repo's own `PROMPTS.md`, so they can be appended there directly.

### 3.1 Fix the documentation index (do this first)

> **Prompt:** Audit `docs/INDEX.md` and `docs/DOCUMENTATION_MAP.md` against the actual contents of `docs/`. For every linked file that does not exist, either (a) generate it from the real source in `src/django_fusion/` and `tests/`, or (b) remove the link and its row from every table until the doc is written. Do not leave any entry marked "✅ Complete" for a file that isn't present. Re-run the audit after each new doc lands so the index stays truthful.
>
> **Expected Input:** `docs/INDEX.md`, `docs/DOCUMENTATION_MAP.md`, current `docs/` file listing.
> **Expected Output:** A diff where every link resolves, and status columns match reality.

### 3.2 Generate `docs/GETTING_STARTED.md`

> **Prompt:** Write a `docs/GETTING_STARTED.md` for django-fusion aimed at a developer setting up the package for the first time in a fresh Django project (not the Structa Cloud monorepo). Cover: install (`pip install django-fusion` and the editable/local path variant), minimum `INSTALLED_APPS`/`MIDDLEWARE` additions required for `django_fusion.core.middlewares.component_error` and `django_fusion.health`, one minimal `Site`/`Application`/`Viewset` example from `django_fusion.comp.routes`, and how to render a first `{% comp %}` component. Base all code on the real classes in `src/django_fusion/comp/routes/` and `src/django_fusion/comp/templatetags/` — do not invent APIs. Target 10 minutes reading time, matching the estimate already promised in `docs/INDEX.md`.
>
> **Expected Input:** `src/django_fusion/comp/routes/`, `src/django_fusion/comp/templatetags/`, `src/django_fusion/health/`, `QUICKSTART.md` (for tone/format).
> **Expected Output:** `docs/GETTING_STARTED.md`.

### 3.3 Generate `docs/ARCHITECTURE_OVERVIEW.md`

> **Prompt:** Write `docs/ARCHITECTURE_OVERVIEW.md` explaining how django-fusion's modules relate: `comp` (component system + routing), `core` (models/managers/services/middlewares — the foundation layer), `site` (auth, context processors, pagination), `web` (allauth adapters, view mixins), `wagtail` (CMS integration), `contrib` (admin/cache/debug/privacy add-ons), `infrastructure` (management commands, locale, scripts), `analyzer` (template/component scanner), `health` (health-check endpoints). Use the module docstring in `src/django_fusion/__init__.py` as the source of truth for the module list and one-line descriptions, then expand each into 2-4 sentences plus a "when would I touch this" note. Include one architecture diagram (Mermaid) showing request flow from URLconf → `Site`/`Application`/`Viewset` → `RoutableComponent`/`FragmentComponent` → `{% comp %}` template rendering.
>
> **Expected Input:** `src/django_fusion/__init__.py`, `AGENTS.md` (package architecture tree), `src/django_fusion/comp/routes/`.
> **Expected Output:** `docs/ARCHITECTURE_OVERVIEW.md` with a Mermaid diagram.

### 3.4 Generate `docs/COMPONENT_SYSTEM.md` and reconcile with `docs/COMPONENT_TAG.md`

> **Prompt:** `docs/COMPONENT_TAG.md` already documents the `{% comp %}` tag syntax (props/slots/vars/attrs) in detail and compares it to django-bird/django-cotton. Write a complementary `docs/COMPONENT_SYSTEM.md` that documents the *Python side*: `RoutableComponent`, `FragmentComponent`, `FragmentDetector`/`FragmentDetectionMixin`, the component registry (`django_fusion.comp.registry`), and `register_default_partials()`. Explain component lifecycle (registration → template resolution cascade → render → HTMX fragment detection) and link out to `COMPONENT_TAG.md` for template-tag syntax rather than duplicating it. Base everything on `src/django_fusion/comp/registry.py`, `src/django_fusion/comp/routes/`, and `src/django_fusion/comp/loaders/`.
>
> **Expected Input:** `src/django_fusion/comp/registry.py`, `src/django_fusion/comp/routes/`, `src/django_fusion/comp/loaders/`, `docs/COMPONENT_TAG.md`.
> **Expected Output:** `docs/COMPONENT_SYSTEM.md`, cross-linked with `COMPONENT_TAG.md`.

### 3.5 Generate `docs/ROUTING_SYSTEM.md`

> **Prompt:** Write `docs/ROUTING_SYSTEM.md` documenting `Site`, `Application`, `AppMenuMixin`, `Viewset`/`BaseViewset`/`ViewsetMeta`, `Route`/`route`, `menu_path`, `IndexViewMixin`, `viewprop`, and the `ModelViewset` family (`BaseModelViewset`, `ModelViewset`, `ReadonlyModelViewset`) plus the CRUD mixins (`ListBulkActionsMixin`, `CreateViewMixin`, `UpdateViewMixin`, `DeleteViewMixin`, `DetailViewMixin`). For each, give the canonical import from `AGENTS.md`, a one-paragraph purpose statement, and a minimal runnable example wiring a model into a `www/urls.py`. Cross-reference `docs/VIEWFLOW_MAPPING.md` for readers coming from django-material/viewflow.
>
> **Expected Input:** `src/django_fusion/comp/routes/`, `AGENTS.md` (canonical import table), `docs/VIEWFLOW_MAPPING.md`.
> **Expected Output:** `docs/ROUTING_SYSTEM.md`.

### 3.6 Generate `docs/FORMS_TABLES_INTEGRATION.md`

> **Prompt:** `QUICKSTART.md` at the repo root already covers `FormMixin`/`TableMixin`/`FormTableMixin` in "30-second setup" form and links to `docs/FORMS_TABLES_INTEGRATION.md` as the "full API reference" — but that file doesn't exist. Write it: expand every method table in `QUICKSTART.md` (`get_form_name()`, `get_table_headers()`, etc.) into full signatures with parameters, return types, and override examples pulled from the real mixin source. Add a section on the template resolution cascade (site-specific → shared assets → generic fallback → django-fusion default) with a worked example for both a form and a table. Do not restate `QUICKSTART.md` verbatim — QUICKSTART stays the fast path, this is the deep reference it points to.
>
> **Expected Input:** `QUICKSTART.md`, `src/django_fusion/comp/routes/` (mixin source), `src/django_fusion/comp/forms/`.
> **Expected Output:** `docs/FORMS_TABLES_INTEGRATION.md`.

### 3.7 Generate `docs/CONFIGURATION.md`

> **Prompt:** Write `docs/CONFIGURATION.md` covering every Django setting django-fusion reads or requires, sourced from `src/django_fusion/config/conf.py`, `conf_utils.py`, `constants.py`, and `dynaconf_loader.py`. Include: required `INSTALLED_APPS` entries, middleware ordering constraints (especially where `component_error` and privacy/language middlewares must sit relative to Django's own), the Dynaconf multi-environment YAML setup, and cache backend requirements for `django_fusion.comp.cache`. Present as a settings reference table (setting name, default, type, purpose) followed by a fully worked example `settings.py` snippet.
>
> **Expected Input:** `src/django_fusion/config/`, `src/django_fusion/comp/cache.py`, `src/django_fusion/projects/middlewares/`.
> **Expected Output:** `docs/CONFIGURATION.md`.

### 3.8 Generate `docs/API_REFERENCE.md`

> **Prompt:** Generate an API reference for django-fusion's public surface, organized by the canonical import paths already listed in `AGENTS.md` (`comp.routes`, `comp.generic`, `core.handlers`, `core.managers`, `core.models`, `core.services`, `web.views`, `comp.loaders`, `core.middlewares`, `core.cache`). For each public class/function, extract its docstring and signature directly from source (do not paraphrase behavior you haven't read) and list under the matching heading. Flag anything exported without a docstring as `TODO: needs docstring` instead of guessing its behavior.
>
> **Expected Input:** All modules listed in `AGENTS.md`'s "Canonical Import Paths" section.
> **Expected Output:** `docs/API_REFERENCE.md`, plus a follow-up list of undocumented public symbols for the maintainers to fill in.

### 3.9 Generate `docs/HEALTH.md`

> **Prompt:** Write `docs/HEALTH.md` documenting `HealthCheckView`, `DatabaseHealthView`, and `AssetsHealthView` from `django_fusion.health`. Cover the `include(health_urls)` wiring already sketched in `PROMPTS.md`, expected JSON response shape for healthy/unhealthy states, HTTP status codes returned, and example Docker `HEALTHCHECK` and Kubernetes liveness/readiness probe configs pointing at the endpoint.
>
> **Expected Input:** `src/django_fusion/health/views.py`, `src/django_fusion/health/urls.py`, `PROMPTS.md` (existing health-check prompt).
> **Expected Output:** `docs/HEALTH.md`.

### 3.10 Generate `docs/WAGTAIL_INTEGRATION.md`

> **Prompt:** Write `docs/WAGTAIL_INTEGRATION.md` covering `django_fusion.wagtail.blocks`, `.snippets`, and `.viewsets`. Include a worked example of adding a custom StreamField block (matching the `CallToActionBlock` example already sketched in `PROMPTS.md`) and registering a snippet/viewset. Cross-link from `PROMPTS.md`'s existing "Adding a Wagtail StreamField Block" entry, which already points here.
>
> **Expected Input:** `src/django_fusion/wagtail/`, `PROMPTS.md`.
> **Expected Output:** `docs/WAGTAIL_INTEGRATION.md`.

### 3.11 Generate `docs/TROUBLESHOOTING.md` and `docs/FAQ.md`

> **Prompt:** Write `docs/TROUBLESHOOTING.md` and `docs/FAQ.md` by mining `tests/` for the edge cases the maintainers already cared enough about to test — e.g. `tests/test_conftest_debug_is_quiet.py` (the `DJANGO_DEBUG_CONFTEST=1` opt-in documented in `pyproject.toml`), `tests/test_django_settings_configure_contract.py`, `tests/test_component_tag.py`, `tests/test_register_include_path_render_equivalence.py`. For each test module, ask "what real-world confusion was this guarding against?" and turn that into a Q&A entry or troubleshooting symptom→cause→fix entry. This grounds the FAQ in actual historical pain points instead of generic Django advice.
>
> **Expected Input:** `tests/` (all modules), `pyproject.toml` (pytest config comments).
> **Expected Output:** `docs/TROUBLESHOOTING.md`, `docs/FAQ.md`.

### 3.12 Generate `docs/BEST_PRACTICES.md` and `docs/INTEGRATION_EXAMPLES.md`

> **Prompt:** Using `docs/COMPONENT_CASE_STUDIES.md` (22 components, 9 cross-cutting recipes) as the raw material, extract the recurring patterns into two documents: `docs/BEST_PRACTICES.md` (prescriptive dos/don'ts — naming conventions, when to use `FragmentComponent` vs `RoutableComponent`, caching guidance, security notes for the privacy middleware) and `docs/INTEGRATION_EXAMPLES.md` (narrative walkthroughs building one feature end-to-end: model → viewset → component → template → test). Do not duplicate the case studies verbatim; synthesize the *pattern*, and link back to the relevant case study for full code.
>
> **Expected Input:** `docs/COMPONENT_CASE_STUDIES.md`, `tests/test_osoul_components.py`, `tests/test_forms_tables_chain.py`.
> **Expected Output:** `docs/BEST_PRACTICES.md`, `docs/INTEGRATION_EXAMPLES.md`.

### 3.13 Prune or migrate the remaining ghost links

> **Prompt:** For every doc still listed in `docs/DOCUMENTATION_MAP.md`'s "Legacy/Deprecated" section (`COMPONENT_CACHE.md`, `COMPONENT_CACHE_QUICKSTART.md`, `PACKAGES.md`, `TEMPLATES.md`, `environments.md`, `packages.md`, `templates.md`, `websites.md`, `model-views-and-htmx-fragments.md`) and the three `WEBSITES_*.md` site guides: decide per-file whether it (a) still applies to this standalone extraction and should be written, or (b) was monorepo/site-specific and should be deleted from the index. Do not silently keep dead links "for later" — either write a stub with a clear "not yet written, tracked in issue #N" note, or remove the row.
>
> **Expected Input:** `docs/DOCUMENTATION_MAP.md` legacy section.
> **Expected Output:** Updated `docs/DOCUMENTATION_MAP.md` with no unexplained dead links.

### 3.14 Fix the root README

> **Prompt:** Rewrite `README.md` to: (1) give a one-paragraph description of django-fusion as a component/routing/CMS toolkit for Django + Wagtail, not just "cached managers + one middleware + a decorator" — pull the real module list from `src/django_fusion/__init__.py`; (2) fix the install instructions so they work for this standalone repo (`pip install -e .` from the repo root, plus the monorepo-style path as an alternative for Structa Cloud consumers); (3) add a "Documentation" section linking to `docs/INDEX.md`; (4) add build/license/PyPI badges once CI and LICENSE exist (§3.15, §3.16).
>
> **Expected Input:** `src/django_fusion/__init__.py`, `pyproject.toml`, current `README.md`.
> **Expected Output:** Updated `README.md`.

### 3.15 Add CI

> **Prompt:** Add `.github/workflows/tests.yml` that installs the package with the `test` extra (`pip install -e .[test]`) and runs `pytest` on push and PR against the `generic` branch, across the Python versions implied by `requires-python = ">=3.11"` in `pyproject.toml` (3.11, 3.12, at minimum). Fail the build on any test failure. Add a status badge to `README.md` once the workflow exists.
>
> **Expected Input:** `pyproject.toml` (`[project.optional-dependencies] test`, `[tool.pytest.ini_options]`).
> **Expected Output:** `.github/workflows/tests.yml`.

### 3.16 Add LICENSE, CONTRIBUTING.md, CHANGELOG.md

> **Prompt:** Add a `LICENSE` file (confirm the intended license with the maintainer — MIT or Apache-2.0 are the common defaults for a Django helper library; do not guess and commit a license the maintainer didn't choose). Add `CONTRIBUTING.md` covering local dev setup (`pip install -e .[test]`, `pytest`), the `DJANGO_DEBUG_CONFTEST=1` diagnostic flag already documented in `pyproject.toml`'s comments, and PR expectations. Add `CHANGELOG.md` seeded with a `0.1.0` entry summarizing current functionality, following Keep a Changelog format for future entries.
>
> **Expected Input:** `pyproject.toml`, maintainer confirmation of license choice.
> **Expected Output:** `LICENSE`, `CONTRIBUTING.md`, `CHANGELOG.md`.

### 3.17 Clean up the broken symlink and monorepo-path references

> **Prompt:** Delete the broken `django-fusion` symlink at the repo root (currently points to `/app/libs/django-fusion`, which doesn't exist in this repo). Search the whole repo for hardcoded `application/libs/django-fusion` path references (`README.md`, `AGENTS.md`, `PROMPTS.md`, `QUICKSTART.md` all have them) and either make them relative to repo root, or clearly label them as "path shown is for the Structa Cloud monorepo; in the standalone repo, drop the `application/libs/django-fusion/` prefix."
>
> **Expected Input:** Full repo grep for `application/libs/django-fusion` and for the symlink itself.
> **Expected Output:** Symlink removed; path references corrected or annotated.

### 3.18 Tighten `pyproject.toml` for publishing

> **Prompt:** Update `pyproject.toml`'s `[project]` table to add `readme = "README.md"`, `license = {text = "<chosen license>"}`, `authors`, `classifiers` (Framework :: Django, Development Status, Python versions), and `[project.urls]` with `Homepage`/`Repository` pointing at the GitHub repo. Add a `dev` optional-dependency group covering `ruff` (or `black`+`isort`+`flake8`) and `pre-commit`, and commit a matching `.pre-commit-config.yaml` and lint config (`ruff.toml` or `[tool.ruff]` in `pyproject.toml`).
>
> **Expected Input:** Current `pyproject.toml`, LICENSE decision from §3.16.
> **Expected Output:** Updated `pyproject.toml`, `.pre-commit-config.yaml`, lint config.

---

## 4. Unified doc/prompt/agent structure (numbered, tagged)

This section gives django-fusion a **minimal, numbered directory layout** so every doc, prompt, and agent-facing file maps 1:1 to a stable ID (`DF-0NN` for docs, `PR-NN` for prompts, `AG-000` for the agent file). Use these IDs in commit messages, PR titles, and cross-links so references survive file renames.

### 4.1 Target `docs/` tree — minimal dir count, flat, one `legacy/` escape hatch

```
docs/
├── INDEX.md                     # DF-000 — map only, no duplicated content
├── 01-getting-started.md        # DF-001
├── 02-architecture.md           # DF-002
├── 03-component-system.md       # DF-003 (Python side)
├── 04-component-tag.md          # DF-004 (renamed from COMPONENT_TAG.md — template-tag syntax)
├── 05-routing.md                # DF-005
├── 06-forms-and-tables.md       # DF-006
├── 07-configuration.md          # DF-007
├── 08-api-reference.md          # DF-008
├── 09-health.md                 # DF-009
├── 10-wagtail-integration.md    # DF-010
├── 11-best-practices.md         # DF-011
├── 12-integration-examples.md   # DF-012 (absorbs COMPONENT_CASE_STUDIES.md content)
├── 13-troubleshooting.md        # DF-013
├── 14-faq.md                    # DF-014
├── 15-viewflow-mapping.md       # DF-015 (renamed from VIEWFLOW_MAPPING.md)
└── legacy/                      # anything not worth rewriting goes here with a banner, not deleted silently
```
`WEBSITES_*.md` deliberately excluded — those describe *consumer* sites, not the library, and belong in each consuming site's own docs (see the ceptor-ai companion document).

### 4.2 Root-level agent/prompt files

```
/
├── AGENTS.md       # AG-000 — canonical import paths + package map; links to DF-002, DF-003, DF-005
├── PROMPTS.md      # PR-000 — index of numbered prompts
├── QUICKSTART.md   # QS-000 — fast path only; deep dives link to DF-006
```

`PROMPTS.md` entries should carry a `Doc IDs:` line instead of loose file paths:

```markdown
## PR-01 — Add a ModelViewset
**Prompt:** ...
**Doc IDs:** AG-000, DF-005
**Related Tags:** ModelViewset, Application, CRUD
```

Mapping this document's §3 prompts onto that numbering:

| Prompt ID | Source | Produces | Doc IDs touched |
|---|---|---|---|
| PR-01 | §3.2 | Getting started guide | DF-001 |
| PR-02 | §3.3 | Architecture overview | DF-002 |
| PR-03 | §3.4 | Component system doc | DF-003, DF-004 |
| PR-04 | §3.5 | Routing doc | DF-005, DF-015 |
| PR-05 | §3.6 | Forms & tables doc | DF-006 |
| PR-06 | §3.7 | Configuration doc | DF-007 |
| PR-07 | §3.8 | API reference | AG-000, DF-008 |
| PR-08 | §3.9 | Health doc | DF-009 |
| PR-09 | §3.10 | Wagtail integration doc | DF-010 |
| PR-10 | §3.11 | Troubleshooting + FAQ | DF-013, DF-014 |
| PR-11 | §3.12 | Best practices + examples | DF-011, DF-012 |
| PR-12 | §3.13 | Legacy pruning | DF-000 |
| PR-13 | §3.14 | README rewrite | — |
| PR-14 | §3.15 | CI workflow | — |
| PR-15 | §3.16 | LICENSE/CONTRIBUTING/CHANGELOG | — |
| PR-16 | §3.17 | Symlink + path cleanup | — |
| PR-17 | §3.18 | pyproject.toml publishing metadata | — |

### 4.3 Usage guide & remarks convention

- **Before writing any doc**, read the source module it documents — never paraphrase from another doc's memory of the code. This repo already has one round of docs that drifted from reality (§1.1); don't repeat it.
- **When adding a doc**, assign the next free `DF-0NN`, add a row to `docs/INDEX.md`, and only mark it "complete" once the content actually exists — never ahead of time (the exact mistake in the current `DOCUMENTATION_MAP.md`).
- **When adding a prompt**, assign the next free `PR-NN` in `PROMPTS.md` and list the `Doc IDs` it produces/updates, so prompt → doc → source is traceable.
- **Code hints**: every code block in a `DF-0NN` file should be trimmed from real source under `src/django_fusion/`, with the source path noted in a comment above the block (e.g. `# src/django_fusion/comp/routes/viewset.py`) so it can be verified against drift.
- **Remarks convention**: put gotchas in a one-line `> Remark:` blockquote directly under the relevant code example (ordering requirements, version constraints, HTMX-only behavior) instead of burying them in prose — this mirrors how `pyproject.toml`'s own comments already flag the `DJANGO_DEBUG_CONFTEST` gotcha.

---

## 5. Suggested execution order

1. §3.17 (remove symlink), §3.1 (stop the doc index from lying) — both are near-zero-risk, immediate credibility fixes.
2. §3.16 (LICENSE) — unblocks everything else legally.
3. §3.15 (CI) — cheap, and every doc/code PR after this benefits from it.
4. §3.14 (README rewrite) — now that install path and license are correct.
5. §3.2–3.12 in the order listed — `GETTING_STARTED` and `ARCHITECTURE_OVERVIEW` first since everything else links back to them; the rest can be parallelized across contributors since they're independent files.
6. §3.13 (prune legacy ghost links) once the active set above is stable.
7. §3.18 (publishing polish) whenever there's appetite to actually cut a PyPI release.

---

## 6. Scope note: what this document does not cover

This document is code/documentation-only and assumes read access to the public repo. It does not attempt to run `make push`/`make push-libs`, deploy anything, or inspect live server logs — see the companion document `ceptor-ai-enhancements.md` for the monorepo that actually owns deployment, and its scope note for why those actions need to be run by someone with the repo's `GITHUB_TOKEN` and server access, not by an assistant with only public, read-only access.
