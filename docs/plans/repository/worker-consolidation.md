# Worker Consolidation Plan
> **Tags:** #worker #celery #consolidation

> Goal: replace the three per-site Celery worker containers (`lms-worker`,
> `ctc-worker`, `vresume-worker`) with **one** shared worker subscribed to all
> three queues, while preserving per-site isolation at the queue level.

## Current state (monorepo, July 2026)

Each of the three sites defines its own worker service in a per-site
`docker-compose.yml`:

| Site          | Web service           | Worker service    | Celery queue |
| ------------- | --------------------- | ----------------- | ------------ |
| `lms`    | `lms-web`             | `lms-worker`      | `lms`   |
| `ctc-research`| `ctc-research-website`| `ctc-worker`      | `ctc-research`|
| `vresume`     | `vresume-web`         | `vresume-worker`  | `vresume`    |

`applications/compose/docker-compose.tasks.yml` also defines a separate `*-worker` set
(`ctc-research-worker`, `lms-worker`, `vresume-worker`) used for the
global `make deploy-tasks` target — these are duplicated work-decls and go
away in Phase 4.

All three sites already share:
- Postgres on `postgres:5432` (separate logical DBs: `db_structa`, `db_ctc`, `vresume`).
- Redis on `default-redis:6379` (logical DBs `/0` cache, `/1` broker, `/2` results).
- Celery image (`projects/compose/Dockerfile` with `PROJECT_PATH=…`).
- `tasks.celery:app` module.

The broker is already shared — consolidating the worker process is safe.

## Target state (one shared worker)

A single container named `shared-worker` running:

```
celery -A tasks.celery:app worker --loglevel=info -Q lms,ctc-research,vresume --hostname=shared-worker@%h
```

subscribed to all three queues simultaneously. The image re-uses
`projects/compose/Dockerfile` with a new build arg `WORKER_MODE=shared` that copies
`projects/<site>/www/` for every site into one image under `/app/<site>/`.

Per-site isolation is preserved **at the queue level** — a buggy task on one
site still cannot poll another site's queue, since `task_routes`
(`projects/configs/base/celery.py`) already pins each `@shared_task` to the
`settings.CELERY_TASK_DEFAULT_QUEUE` of the importing site.

## Server-request → queue mapping

This is the canonical "what HTTP request lands on which queue" table. It
governs `task_routes` and the consolidated-worker subscription.

| Source domain / app | HTTP request origin | Site `DJANGO_SITE` | Celery queue | Representative tasks (current) |
| --- | --- | --- | --- | --- |
| `structa.cloud`, `*.structa.cloud` | LMS web handlers (`POST /learning/...`, `POST /api/...`) | `lms` | `lms` | `enrollment.send_welcome`, `certificate.render_pdf`, `invoice.refresh` |
| `ctc-research.com`, `*.ctc-research.com` | Research web handlers + scheduled scrapers | `ctc-research` | `ctc-research` | `scraper.run_weekly`, `report.compile_monthly`, `arch.snapshot` |
| `vresume.structa.cloud` | VResume web/API handlers (resume upload, PDF parse, share link) | `vresume` | `vresume` | `resume.parse_ai`, `pdf.render`, `link.share_token` |

The routing happens automatically based on the importing site's
`CELERY_TASK_DEFAULT_QUEUE`. The shared-worker `-Q lms,ctc-research,vresume`
flag means it picks every queue; the **task name** alone decides which one
gets it because each site's `tasks/` subpackage is built into the same image.

### Settings per-site (inside the shared worker)

The worker process starts under one `DJANGO_SETTINGS_MODULE`, so credentials
for all three sites must be readable. Convention (no rename required):

| Site         | Env var (kept)        | Notes |
| ------------ | --------------------- | ----- |
| `lms`   | `DB_NAME_LMS`, `LMS_DEMO_HOST`, `STRIPE_KEY_LMS` (if used) | Already namespaced at compose level |
| `ctc-research` | `DB_NAME_CTC`, `CTC_RESEARCH_HOST`              | Same           |
| `vresume`    | `DB_NAME_VRESUME`, `VRESUME_HOST`               | Same           |

If a site-specific value sits in `projects/<site>/settings/` rather than env, the
worker image must `python -m importlib` each site on startup. Using env vars
keeps multi-DB routing trivial.

### Multi-database config inside the single worker

```python
# configs/settings_shared.py (Phase 1)
DATABASES = {
  'default': env.db_for('LMS'),
  'ctc':     env.db_for('CTC'),
  'vresume': env.db_for('VRESUME'),
}
DATABASE_ROUTERS = ['configs.routers.SiteRouter']
```

The worker reads `DJANGO_SITE` from env and binds the right DB alias as
`default` for that task's processing path. Cross-site reads (e.g. an admin
report) use the explicit alias.

## Migration — 4 phases with rollback guard

### Phase 1 — Code prep (no runtime change)
1. Add `projects/configs/settings_shared.py` with the multi-DB dict + SiteRouter.
2. Update `projects/webpack/` and `applications/scripts/` (if they build shared-worker image) — no behaviour change.
3. Add `applications/compose/docker-compose.shared-worker.yml` with `shared-worker` service (initially stopped).
4. Add new entry in `CELERY_TASK_ROUTES` only if a task name collides across sites (verify with `rg -n '@shared_task' projects/`).

### Phase 2 — Parallel deploy (safe to roll back)
1. `docker compose -f applications/compose/docker-compose.shared-worker.yml up -d --build shared-worker`
2. Confirm shared-worker is processing — `docker logs shared-worker | grep "ready"` should list all three queues.
3. Existing `lms-worker`, `ctc-worker`, `vresume-worker` continue running in parallel. Tasks are now delivered to **either** worker (no double processing because Celery uses an ack protocol — first acker wins).

### Phase 3 — Cut over (rolling, with rollback window)
1. Stop the slowest per-site worker first to keep latency predictable:
   - `docker stop vresume-worker`
   - monitor queue for 10 min: `redis-cli -n 1 LLEN vresume`
   - if backlog keeps growing → rollback (restart vresume-worker)
2. Same for `ctc-worker` → `lms-worker`.
3. After per-site workers are stopped, keep them *defined* in their compose files for ≥7 days so rollback is a one-liner.

### Phase 4 — Cleanup
1. Comment out per-site worker services in `projects/lms/docker-compose.yml`, `projects/ctc-research/docker-compose.yml`, `projects/VResume/docker-compose.yml`.
2. Delete `applications/compose/docker-compose.tasks.yml`'s three duplicate worker entries (or replace with one import).
3. Update root `Makefile` `deploy-tasks` target to point at `applications/compose/docker-compose.shared-worker.yml`.
4. Update `projects/Makefile` `docker-redeploy-with-worker` to **also** restart `shared-worker`.

## Rollback guard (one-command)

If the shared-worker misbehaves at any phase, restore per-site workers:

```bash
for s in vresume ctc-research lms; do
  docker compose -f projects/$s/docker-compose.yml up -d --no-deps $(make -C core -s DOCKER_WORKER=${s}-worker show-config 2>/dev/null || echo ${s}-worker)
done
docker stop shared-worker
```

In practice the recipe is the reverse of Phase 3: restart the stopped
per-site worker. Celery rebalanced tasks are immediately pulled by it.

## Validation per phase

Each phase exits with these gates:

| Phase | Gate | Command |
| --- | --- | --- |
| 1 | Settings loads OK | `docker run --rm structa-shared-worker python -c "import configs.settings_shared; print('ok')"` |
| 2 | All 3 queues visible | `docker logs shared-worker 2>&1 | rg "ready" | rg -c "lms|ctc-research|vresume"` |
| 2 | Tasks delivered | `docker exec shared-worker celery -A tasks.celery:app inspect ping -d celery@lms` |
| 3 | Queue draining | `redis-cli -n 1 LLEN lms ctc-research vresume` |
| 3 | No error spike | `docker logs shared-worker --since 10m | rg -c ERROR` (must be ≤ baseline) |
| 4 | One worker only | `docker ps --filter name=worker` returns exactly 1 |

## Resource budget (estimate)

| Aspect | Before | After |
| --- | --- | --- |
| Worker processes | 3 Python interpreters (~150 MiB each ≈ 450 MiB) | 1 Python interpreter (~180 MiB) |
| Idle CPU | ~3 × 1% = 3% | ~1 × 1% = 1% |
| Image storage | 3 per-site images (`lms-worker:latest`, …) | 1 shared image |

## Out of scope (not changed by this plan)

- The Django **web** tier — each site still has its own web service.
- The Postgres / Redis tier — DBs stay separate on a shared server.
- Frontend asset builds — those are static, not async tasks.
- The RQ worker script (`applications/compose/rqworker-start`) — orthogonal; can be folded in later if RQ is no longer needed in addition to Celery.
