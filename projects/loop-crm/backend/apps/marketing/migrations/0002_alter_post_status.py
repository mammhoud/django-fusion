from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("marketing", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("pending_approval", "Pending approval"),
                    ("approved", "Approved"),
                    ("scheduled", "Scheduled"),
                    ("publishing", "Publishing"),
                    ("published", "Published"),
                    ("failed", "Failed"),
                ],
                default="draft",
                max_length=20,
            ),
        )
    ]
