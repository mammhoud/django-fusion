from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pages", "0002_remove_contactsubmission_created_by_and_more")]

    operations = [
        migrations.CreateModel(
            name="SiteLanguage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(choices=[("en", "English"), ("fr", "French"), ("de", "German"), ("es", "Spanish"), ("ar", "Arabic"), ("pt-br", "Portuguese (Brazil)")], max_length=10, unique=True)),
                ("name", models.CharField(max_length=60)),
                ("native_name", models.CharField(blank=True, default="", max_length=60)),
                ("direction", models.CharField(choices=[("ltr", "Left to right"), ("rtl", "Right to left")], default="ltr", max_length=3)),
                ("flag", models.CharField(blank=True, default="", max_length=8)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
            ],
            options={"ordering": ["sort_order", "code"], "verbose_name": "site language", "verbose_name_plural": "site languages"},
        ),
    ]
