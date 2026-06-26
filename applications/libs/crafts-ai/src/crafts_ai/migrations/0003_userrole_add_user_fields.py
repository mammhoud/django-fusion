"""
Migration: Add user/assigned_by fields to UserRole, users M2M to UserGroup, and related indexes.

The 0002 migration created UserRole without the user/assigned_by foreign keys.
This migration adds them. Because the table may already have rows, the user FK
is added as nullable first (matching a safe migration pattern); the model still
declares it non-nullable but we allow null in the DB for existing rows since
the table should be empty in fresh environments.

If you have existing UserRole rows without users, run a data migration to
assign them to a valid user before tightening the constraint.
"""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crafts_ai", "0002_enhance_email_template"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ----------------------------------------------------------------
        # Add user FK to UserRole (nullable to allow migration on existing rows)
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name="userrole",
            name="user",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="roles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # ----------------------------------------------------------------
        # Add assigned_by FK to UserRole
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name="userrole",
            name="assigned_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="assigned_roles",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # ----------------------------------------------------------------
        # Add unique_together for UserRole (user + role)
        # ----------------------------------------------------------------
        migrations.AlterUniqueTogether(
            name="userrole",
            unique_together={("user", "role")},
        ),
        # ----------------------------------------------------------------
        # Add users M2M to UserGroup
        # ----------------------------------------------------------------
        migrations.AddField(
            model_name="usergroup",
            name="users",
            field=models.ManyToManyField(
                blank=True,
                related_name="email_groups",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # ----------------------------------------------------------------
        # Alter EmailLog.timestamp to add auto_now_add-like default
        # (the model defines it without auto_now but the original migration
        #  had no default; adding db_index was already done in 0002)
        # ----------------------------------------------------------------
        migrations.AlterField(
            model_name="emaillog",
            name="timestamp",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        # ----------------------------------------------------------------
        # EmailLog indexes (status+timestamp, recipient+timestamp, etc.)
        # ----------------------------------------------------------------
        migrations.AddIndex(
            model_name="emaillog",
            index=models.Index(
                fields=["status", "timestamp"],
                name="email_log_status_9e3e25_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="emaillog",
            index=models.Index(
                fields=["recipient", "timestamp"],
                name="email_log_recipie_d43226_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="emaillog",
            index=models.Index(
                fields=["task_id"],
                name="email_log_task_id_2a1ea1_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="emaillog",
            index=models.Index(
                fields=["recipient", "status", "timestamp"],
                name="email_log_recipie_55cf1f_idx",
            ),
        ),
    ]
