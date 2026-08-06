from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pos_full", "0001_initial_all_models"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersettings",
            name="fusion_render_mode",
            field=models.CharField(
                choices=[
                    ("default", "Default (settings)"),
                    ("fusion", "Fusion render-first"),
                    ("data", "Data APIs"),
                ],
                default="default",
                help_text=(
                    "Content-delivery mode: 'Fusion render-first' serves finished "
                    "server HTML, 'Data APIs' serves JSON for the client, 'Default "
                    "(settings)' follows FUSION_RENDER_FIRST_DEFAULT."
                ),
                max_length=10,
            ),
        ),
    ]
