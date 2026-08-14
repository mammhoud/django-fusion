from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pos_full", "0001_initial_all_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=3, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("symbol", models.CharField(blank=True, default="", max_length=8)),
                ("exchange_rate", models.DecimalField(decimal_places=6, default=1, max_digits=12)),
                ("is_default", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "full_currencies",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="TaxProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("code", models.CharField(max_length=30, unique=True)),
                ("rate", models.DecimalField(decimal_places=4, default=0, max_digits=6)),
                ("is_default", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "full_tax_profiles",
                "ordering": ["name"],
            },
        ),
    ]
