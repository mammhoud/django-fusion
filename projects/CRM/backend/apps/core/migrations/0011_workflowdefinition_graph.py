from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_savedview"),
    ]

    operations = [
        migrations.AddField(
            model_name="workflowdefinition",
            name="graph",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
