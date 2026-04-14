"""
Migration: Move FormSubmission model to django-grep package.

Uses SeparateDatabaseAndState so the database table is untouched;
only Django's model registry is updated to reflect the new location.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("handlers", "0003_authemailtemplate"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],  # no DB changes — table stays as-is
            state_operations=[
                migrations.DeleteModel(name="FormSubmission"),
            ],
        )
    ]
