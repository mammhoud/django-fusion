# Active project closeout - 2026-08-11

> **Status:** Audit complete
> **Scope:** Active Structa Cloud projects and their current framework/deployment plans
> **Branch:** `generic`

## Purpose

This closeout reconciles the earlier Fusion migration, fixture, Docker, proxy,
API, and frontend follow-ups with the repository's current canonical layout.
It is an audit record, not a claim that every historical roadmap item is
implemented.

## Canonical project boundaries

| Product | Canonical path | Former boundary | Closeout status |
|---|---|---|---|
| Precis LMS | `projects/precis/precis-lms/` | `projects/precis-lms/` | Active and deployed |
| Landing-Fusion | `projects/precis/landi/` | CMS-Fusion landing slice | Active |
| CTC Research | `projects/precis/precis-ctc/` | `projects/precis-ctc/` | Active (standalone research site) |
| Syntara | `projects/syntara/` | Cypercloud | Active |
| Formints | `projects/formints/` | POS edition workspace | Active |
| Forge POS | `projects/formints/formint-community/` (was `projects/pos/forge-pos/`, then `formint-community/`) | POS desktop edition | Migrated/removed |
| django-fusion | `libs/django-fusion/` | Shared Fusion framework | Active |

Retired names remain in migration evidence and compatibility documentation.
New code and new plans must use the canonical paths above.

## Verified follow-up work

### Precis LMS deployment

- Backend and frontend images built successfully from `projects/precis/precis-lms/`.
- `precis-lms-backend` became healthy with zero restarts.
- PostgreSQL, Redis, worker, and Traefik services were running.
- Direct and Traefik-routed responses returned HTTP 200 for:
  - `/api/fusion/health`
  - `/api/fusion/health/`
  - `/api/pages/`
  - `/api/courses/`
  - `/api/blog/`
  - `/courses/`
  - `/about/`
  - `/contact/`
- API responses contained database-backed page and course records, including
  `all-courses`, `fusion_render_first`, `show_in_nav`, and the Research Ethics
  course catalog entry.
- The fixture command now distinguishes the safe default from the explicit
  canonical legacy dump:
  - default `--dry-run`: no implicit fixture load;
  - `--category canonical`: previews `assets/fixtures/dump-data.json`;
  - `--fixture dump-data.json`: explicit single-file operation.
- The canonical JSON fixture parsed successfully with 178 entries.
- Focused API and fixture tests passed: **77 passed**.

The historical dump is not loaded automatically because its documented model
labels are legacy data. Production data remains the source of truth for the
running deployment.

### Framework and rendering review

The repository skills audit used:

- `.agents/skills/documentation`
- `.agents/skills/deployment-documentation`
- `.agents/skills/redesign-existing-projects`
- `.agents/skills/design-taste-frontend`

Applied conclusions:

- Keep project-specific branding and content in the project, not in
  `django-fusion`.
- Preserve one canonical import path and avoid compatibility re-exports.
- Keep loading, empty, error, focus, reduced-motion, and dark-mode states in
  frontend contracts.
- Preserve semantic navigation, footer, metadata, and fixture-backed content.
- Do not add a new UI library merely to satisfy a stale plan. Validate the
  current Astro + HTMX + Alpine stack first.
- Keep deployment documentation tied to the actual Docker and Traefik service
  names, ports, health checks, and rollback path.

## Plan disposition

| Plan family | Disposition | Reason |
|---|---|---|
| CMS/LMS migration plans | Superseded core migration record | Runtime moved to Precis and Landing-Fusion |
| CMS Next.js/FlyonUI roadmap | Superseded historical proposal | The active frontend is Astro, not Next.js |
| Assets/templates cleanup | Core work complete; deployment details retained | Remaining media concerns belong to deployment runbooks |
| django-fusion Webpack plan | Active | Project webpack integration remains a framework roadmap item |
| django-fusion Tasks/MCP and LLM/MCP plans | Planned | No claim of provider/task-layer completion is made here |
| Formint edition/POS plans | Active | Product work remains in the canonical Formints/POS plans |
| Legacy and migrated plans | Read-only evidence | Do not delete or treat as current implementation scope |

## Explicitly not marked complete

The following remain planned or require separate product approval:

- FlyonUI migration from the retired Next.js frontend.
- Full public-page browser coverage for the former LMS frontend.
- Unified task/MCP provider integrations in django-fusion.
- Full shared-proxy production rollout beyond the verified local Traefik path.
- POS edition roadmap items and tenant/cloud work.
- Treebeard manager modernization warnings that require an upstream/library
  compatibility decision.

## Validation commands

```bash
# Precis backend
cd projects/precis/precis-lms
uv run python backend/manage.py check
uv run pytest backend/tests/test_api_smoke.py \
  backend/tests/test_fixture_content.py \
  backend/tests/test_fixture_data.py -q --tb=short

# Precis frontend
cd projects/precis/precis-lms/frontend
npm run check
npm run build

# Landing-Fusion backend/frontend
cd projects/precis/landi/backend && make check && make test
cd ../frontend && npm run check && npm run build

# Repository documentation hygiene
cd /home/structa.cloud
python applications/scripts/check_markdown_links.py
```

## Related

- [`../README.md`](../README.md)
- [`../document-lifecycle.md`](../document-lifecycle.md)
- [`../deletion-manifest.md`](../deletion-manifest.md)
- [`../../../projects/precis/precis-lms/README.md`](../../../projects/precis/precis-lms/README.md)
- [`../../../projects/precis/landi/README.md`](../../../projects/precis/landi/README.md)
- [`../../../libs/django-fusion/CHANGELOG.md`](../../../libs/django-fusion/CHANGELOG.md)
