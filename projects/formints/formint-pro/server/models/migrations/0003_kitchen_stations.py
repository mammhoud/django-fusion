from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pos_full", "0002_currency_taxprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="KitchenStation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=100, unique=True)),
                (
                    "station_type",
                    models.CharField(
                        choices=[
                            ("expedite", "Expedite"),
                            ("grill", "Grill"),
                            ("fry", "Fry"),
                            ("prep", "Prep"),
                            ("bar", "Bar"),
                            ("pantry", "Pantry"),
                            ("other", "Other"),
                        ],
                        default="expedite",
                        max_length=40,
                    ),
                ),
                (
                    "category_keywords",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Comma-separated category name keywords used for auto-routing tickets.",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("sort_order", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "full_kitchen_stations",
                "ordering": ["sort_order", "name"],
            },
        ),
        migrations.AddField(
            model_name="kitchenticket",
            name="station",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="tickets",
                to="pos_full.kitchenstation",
                help_text="Station this ticket is routed to.",
            ),
        ),
        migrations.AddField(
            model_name="kitchenticket",
            name="started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="kitchenticket",
            name="ready_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
