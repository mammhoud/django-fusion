from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pos_full", "0003_kitchen_stations"),
    ]

    operations = [
        migrations.CreateModel(
            name="MenuVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.PositiveIntegerField(default=1)),
                ("locale", models.CharField(default="en", help_text="BCP 47 locale code, e.g. en, ar, fr", max_length=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("published", "Published"),
                            ("archived", "Archived"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                (
                    "preview_token",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Secret token that gates unauthenticated preview of a draft.",
                        max_length=64,
                    ),
                ),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_synced", models.BooleanField(db_index=True, default=False)),
                ("synced_at", models.DateTimeField(blank=True, null=True)),
                (
                    "sync_status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("synced", "Synced"),
                            ("failed", "Failed"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("menu", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="versions", to="pos_full.menu")),
            ],
            options={
                "db_table": "full_menu_versions",
                "ordering": ["-version", "locale"],
                "unique_together": {("menu", "version", "locale")},
            },
        ),
    ]
