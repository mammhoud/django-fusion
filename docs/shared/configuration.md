# Shared — Configuration Reference

> **Port:** 5080 | **Aliases:** shared, shared-worker, shared-scheduler, tasks

## Site Registration

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  www:
    port: 5080
    path: www
    aliases: [shared, shared-worker, shared-scheduler, tasks]
```

## Key Files

| File | Purpose |
|------|---------|
| `www/settings.py` | Django settings for sentinel site |
| `www/worker/celery.py` | Celery app bootstrap + beat scheduler |
| `www/worker/tasks.py` | Celery task definitions (heartbeat) |
| `www/worker/email.py` | Dramatiq email actors |
| `www/worker/content.py` | Dramatiq content management |
| `www/worker/modules.py` | Task module registry |
| `www/worker/runtime.py` | `configure_django_for_website()` |
| `www/ci/utils.py` | CI/CD preflight utilities |

## Environment

| Variable | Required | Purpose |
|----------|:--------:|---------|
| `DB_NAME` | — | Database for sentinel site (default: db_ctc) |
| `DRAMATIQ_PROCESSES` | — | Dramatiq worker processes |
| `DRAMATIQ_QUEUES` | — | Queue names (comma-separated) |

## Related

| Resource | Path |
|----------|------|
| Shared README | [`README.md`](README.md) |
| Shared methods | [`shared-methods.md`](shared-methods.md) |
| LMS shared-www | [`../lms/shared-integration.md`](../lms/shared-integration.md) |
| Infrastructure | [`../../infrastructure/worker-stack.md`](../../infrastructure/worker-stack.md) |
