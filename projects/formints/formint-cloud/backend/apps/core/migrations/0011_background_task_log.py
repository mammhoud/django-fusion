"""Create the shared django-fusion BackgroundTaskLog table.

``django_fusion.models.tasks.BackgroundTaskLog`` declares
``app_label = "shared"`` and ``db_table = "grep_background_task_log"``, but the
``shared`` app is not installed in formint-cloud, so Django's migration
machinery never generates the table. The Dramatiq task backend dual-writes this
shared audit trail (alongside the website-local ``core.TaskExecution`` record),
so the table must be materialized by a product migration (same pattern as
loop-crm's ``core.0006_background_task_log``).
"""

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_taskexecution"),
    ]

    # SeparateDatabaseAndState: the CreateModel lives only in database
    # operations so Django's model state never registers a phantom
    # ``core.BackgroundTaskLog`` (the real model belongs to the uninstalled
    # ``shared`` app label). Without this, ``makemigrations`` would propose
    # deleting the table.
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.CreateModel(
                    name="BackgroundTaskLog",
                    fields=[
                        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                        ("job_id", models.CharField(blank=True, db_index=True, max_length=255, null=True)),
                        ("task_name", models.CharField(db_index=True, max_length=255)),
                        ("queue_name", models.CharField(default="default", max_length=100)),
                        ("backend", models.CharField(blank=True, default="dramatiq", max_length=50)),
                        ("status", models.CharField(choices=[("queued", "Queued"), ("started", "Started"), ("finished", "Finished"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("retrying", "Retrying")], default="queued", max_length=20)),
                        ("args", models.JSONField(blank=True, default=list)),
                        ("kwargs", models.JSONField(blank=True, default=dict)),
                        ("result", models.JSONField(blank=True, null=True)),
                        ("error_message", models.TextField(blank=True, null=True)),
                        ("error_traceback", models.TextField(blank=True, null=True)),
                        ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                        ("started_at", models.DateTimeField(blank=True, null=True)),
                        ("completed_at", models.DateTimeField(blank=True, null=True)),
                        ("retry_count", models.IntegerField(default=0)),
                        ("max_retries", models.IntegerField(default=3)),
                        ("scheduled_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                        ("is_scheduled", models.BooleanField(default=False)),
                        ("site_id", models.IntegerField(blank=True, db_index=True, null=True)),
                        ("app_label_field", models.CharField(blank=True, default="", max_length=100)),
                    ],
                    options={
                        "verbose_name": "Background Task Log",
                        "verbose_name_plural": "Background Task Logs",
                        "db_table": "grep_background_task_log",
                        "ordering": ["-created_at"],
                        "indexes": [
                            models.Index(fields=["status", "-created_at"], name="grep_bg_status_created_idx"),
                            models.Index(fields=["task_name", "-created_at"], name="grep_bg_task_created_idx"),
                            models.Index(fields=["queue_name", "status"], name="grep_bg_queue_status_idx"),
                        ],
                    },
                ),
            ],
            state_operations=[],
        ),
    ]
