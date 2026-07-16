"""Registers a 30-second celery-beat heartbeat schedule.

Lives in the `pages` Django app (the cookiecutter-rename successor of
the original `content` app). Path: `core/ctc-research/www/core/content/`
is the on-disk directory; the app *label* used in migration tuples is
`pages` because of the rename in step 0002.

Why here, not `www/migrations/`?
--------------------------------
Cookiecutter-Django rewires `django.contrib.sites`'s `MIGRATION_MODULES`
to point at `core/<site>/www/migrations/`. Django therefore classifies
ANY file dropped in `www/migrations/` as belonging to the `sites` app —
not `www`. Auto-discovery of `django_celery_beat` PeriodicTask rows
depends on a real app label, so we need a directory whose parent IS in
`INSTALLED_APPS`. Cookiecutter renames `www.core.content` → `pages` in
migration 0002 (see `0002_rename_content_con_form_id_…_and_more.py`),
so we list it as `pages` here.

Idempotent: re-running this migration updates the same PeriodicTask
in place — matches the cookiecutter `update_or_create` pattern at
`www/migrations/0003_set_site_domain_and_name.py`.

Reversible: rollback deletes the PeriodicTask row and best-effort
cleans up any orphaned 30-second `IntervalSchedule` that no other
PeriodicTask references. Safe no-op when VResume isn't deployed and
its schedules don't share the 30-second window.

Verification after `python manage.py migrate pages`:

    docker exec ctc-research-website python manage.py shell -c \\
        "from django_celery_beat.models import PeriodicTask; \\
         print(PeriodicTask.objects.get(name='structa.beat.heartbeat').task)"

Expected output: `www.worker.tasks.heartbeat`. Then `make deploy-tasks`
restarts shared-scheduler; log volume should rise every 30s in
`shared-scheduler` and `shared-worker`; `/app/logs/celery_beat_heartbeat.txt`
will hold the most recent UTC ISO timestamp.
"""

from django.db import migrations


# Public name (visible in django_celery_beat admin + logs); namespaced
# with `structa.beat.` so it never collides with VResume's already-inlined
# entries (process-scheduled-campaigns, cleanup-old-campaigns, …).
HEARTBEAT_NAME = "structa.beat.heartbeat"
# Task registered via @shared_task(name=…) at
# core/ctc-research/www/worker/tasks.py.
HEARTBEAT_TASK = "www.worker.tasks.heartbeat"
# Routed to the ctc-research Celery worker (ctc-worker container) which
# is the only Celery consumer in the stack. Each per-site `*-worker`
# compose service runs `celery -A www.worker.celery:app worker
# --queues=<site-name>`, so we target ctc-research for the heartbeat;
# swapping DJANGO_SITE would require reprocessing through the ctc-
# research DB. shared-worker is Dramatiq-only — it cannot consume
# Celery-dispatched tasks regardless of queue arg overlap.
HEARTBEAT_QUEUE = "ctc-research"
# 30 s is short enough that log-volume rise is observable within one
# `make deploy-tasks` probe cycle (default ~30 s wait + 30 s first fire
# = ~60 s total) and long enough not to flood logs.
HEARTBEAT_INTERVAL_SECONDS = 30


def _add_heartbeat(apps, schema_editor):
    """Insert / update the PeriodicTask row idempotently."""
    IntervalSchedule = apps.get_model("django_celery_beat", "IntervalSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")

    schedule, _ = IntervalSchedule.objects.get_or_create(
        every=HEARTBEAT_INTERVAL_SECONDS,
        period="seconds",
    )
    PeriodicTask.objects.update_or_create(
        name=HEARTBEAT_NAME,
        defaults={
            "task": HEARTBEAT_TASK,
            "interval": schedule,
            "queue": HEARTBEAT_QUEUE,
            "enabled": True,
            "description": (
                "Smoke-test heartbeat. Fired every 30s by "
                "shared-scheduler; writes an INFO log line + a "
                "marker file at /app/logs/celery_beat_heartbeat.txt "
                "so beat liveness is observable end-to-end."
            ),
        },
    )


def _remove_heartbeat(apps, schema_editor):
    """Delete the PeriodicTask and best-effort cleanup its IntervalSchedule.

    Only deletes the IntervalSchedule if no other PeriodicTask references
    it — VResume's per-site schedules may use the same 30-second window,
    so we never want to nuke a shared one.
    """
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    IntervalSchedule = apps.get_model("django_celery_beat", "IntervalSchedule")

    PeriodicTask.objects.filter(name=HEARTBEAT_NAME).delete()

    for interval in IntervalSchedule.objects.filter(
        every=HEARTBEAT_INTERVAL_SECONDS, period="seconds"
    ):
        # periodictask_set is the reverse FK from PeriodicTask.interval.
        if not interval.periodictask_set.exists():
            interval.delete()


class Migration(migrations.Migration):
    """Register the heartbeat schedule; reversible cleanup on rollback."""

    dependencies = [
        # Same-app chain. The cookiecutter rename in 0002 changed the app
        # label `content` -> `pages`; the previous migration alters a
        # couple of StreamFields (no schema change, just index tweaks).
        (
            "pages",
            "0003_alter_aboutpage_facts_alter_aboutpage_head_and_more",
        ),
        # django_celery_beat needs its PeriodicTask + IntervalSchedule
        # tables created before we touch them.
        ("django_celery_beat", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(_add_heartbeat, reverse_code=_remove_heartbeat),
    ]
