# Active Monorepo Consolidation — 2026-08-14

> **Status:** Implementation complete — environment-dependent deployment gates remain
> **Owner:** Repository / infrastructure
> **Scope:** shared tasks, aggregate Make workflows, Nx JavaScript orchestration, Coder dev-workspace, AppFlowy

## Decision record

- Precis remains an active product at `projects/precis/precis-lms/`.
- Precis/LMS is **not** a shared-worker tenant: its background queues,
  scheduler, and task package are excluded from shared task discovery.
- A single infrastructure-owned `shared-worker` consumes Dramatiq actors and a
  separate APScheduler process registers `django-fusion` cron tasks.
- Active product task packages are imported by filesystem project paths through
  `FUSION_TASK_PROJECT_PATHS`; the worker does not guess a product from the
  default Django site.
- The Coder template is now `applications/templates/dev-workspace/` and must
  be used with workspace name `dev` because the proxy routes stable container
  names.
- AFFiNE is the shared proxy application and uses the shared PostgreSQL
  service through `common` and `warehouse-net`; FileGator has been removed.
- The root JavaScript layer is orchestrated by Nx. Product-local npm/pnpm
  manifests remain authoritative for dependency installation.

## Completed in this change

### Shared task runtime

- `django_fusion.tasks.TaskRegistry.autodiscover()` now accepts configured
  dotted modules and filesystem project paths.
- `FUSION_TASK_PROJECT_PATHS` and `FUSION_TASK_MODULES` are supported without
  importing a product's settings module.
- The Dramatiq backend declares discovered actors in the worker process and
  uses `DRAMATIQ_BROKER_URL` / `REDIS_URL` when no explicit Fusion broker is
  configured.
- `applications/docker-compose.tasks.yml` runs `rundramatiq` plus
  `python -m django_fusion.tasks.scheduler`; Celery Beat is no longer used by
  this stack.
- The shared worker mounts active task packages from Landing-Fusion, Loop-CRM,
  and Formint Cloud. Precis/LMS task paths are intentionally absent.
- Product workers, shared actors, and the former Temporal campaign flow now live
  under each product's `backend/plugins/workers/` boundary and use Dramatiq;
  Precis campaign onboarding/batch work is in `campaign_tasks.py`.

### Aggregate workflows

- `projects/Makefile` aggregate checks, project iteration, population, health,
  and full-site loops no longer include LMS.
- `docker-deploy-websites` deploys active Landing-Fusion and Loop-CRM only.
- Explicit `WEBSITE=precis-lms` maintenance commands remain available.

### Nx baseline

- Root `package.json` and `nx.json` define the Nx workspace contract.
- Explicit `project.json` targets cover all discovered JavaScript package
  projects, including package-specific `build`, `check`/`typecheck`, and
  `test` commands without replacing local scripts.
- Product package managers remain unchanged; `npm run install:projects` is the
  documented convenience install for the currently supported frontend groups.
- Nx project discovery was verified with 17 projects; `npm run check` reaches
  package checks rather than reporting an empty task graph.

### Coder / AppFlowy

- `dev-stack` was renamed to `dev-workspace`.
- The former Blinko container and its database configuration are deprecated and
  removed from the active workspace path.
- The template now provisions the official AppFlowy Cloud service shape:
  GoTrue, AppFlowy Cloud API, AppFlowy Web, and private MinIO storage.
- AppFlowy reuses the shared PostgreSQL service on `warehouse-net` and the
  authenticated Redis service on `common`; no AppFlowy service publishes a
  host port.
- AppFlowy and code-server are authenticated Coder apps only. The old
  `blinko.structa.cloud`, `blinko.localhost`, `code.structa.cloud`, and
  `ws.structa.cloud` routes are removed.
- FileGator, its image, data directories, Coder app, and public routes were
  removed from the active infrastructure.
- Template and database README files document network attachment, persistence,
  secret overrides, and the existing-volume caveat.

## Deprecated or removed

| Item | Disposition | Replacement |
|---|---|---|
| LMS queue in shared worker | Removed from worker discovery/queues | Explicit Precis web/product maintenance; no shared LMS worker |
| Celery Beat in shared task stack | Deprecated and removed from Compose command | `django_fusion.tasks.scheduler` (APScheduler) |
| `applications/compose/docker-compose.tasks.yml` | Retired path in current checkout | `applications/docker-compose.tasks.yml` |
| `applications/templates/dev-stack/` | Renamed | `applications/templates/dev-workspace/` |
| Blinko workspace service | Deprecated and removed | Shared AFFiNE proxy service; FileGator removed |
| Precis Temporal campaign worker | Removed | `plugins.workers.campaign_tasks` Dramatiq actors |
| Historical worker-consolidation Celery target | Superseded documentation | This plan + django-fusion task API |

Historical plans remain read-only evidence until their deletion-manifest gates
are satisfied; no production database or volume is deleted by this change.

## Remaining gates

- Complete the full Nx check/build/test sweep after installing dependencies for
  packages whose local `node_modules` are absent. Current targeted checks reach
  the tasks, while Formint packages still report existing source/configuration
  errors and one purchase frontend lacks its Astro CLI locally.
- Validate the renamed Terraform template with `terraform fmt` / Coder template
  validation in an environment that has the Coder and Docker providers.
- Initialize or migrate existing PostgreSQL volumes so the `appflowy` role and
  database exist; do not force-reinitialize a shared volume automatically.
- Validate shared-worker startup with active product task imports and Redis
  authentication on the target Docker host.
- Resolve namespace collisions if two active products expose the same top-level
  Python `apps` package in one worker process; prefer explicit unique task
  module paths for those products.

## Validation record

Passed in this change:

```bash
npx nx show projects                 # 17 JavaScript projects discovered
npx nx run precis-landing:check
npx nx run loop-crm:check
npx nx run fusion-js:check
uv run pytest libs/django-fusion/tests/test_tasks.py tests/websites/test_shared_tasks.py -q
# Read-only Compose validation; no services were started or migrated.
docker compose -f applications/docker-compose.tasks.yml config -q
git diff --check  # task-related paths
```

Environment-dependent follow-up:

```bash
npm install                         # root Nx dependencies, if not present
npm run check
npm run build
cd projects && make check-all
```

The aggregate Nx commands are wired and reach all configured package targets;
full execution remains dependent on each package's local dependencies and
current source health.
