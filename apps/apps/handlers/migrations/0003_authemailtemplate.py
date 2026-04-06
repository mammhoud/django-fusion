import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("handlers", "0002_service_content_alter_organization_company_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuthEmailTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("template_type", models.CharField(
                    choices=[
                        ("registration_confirmation", "Registration Confirmation"),
                        ("signin_success", "Sign-In Success"),
                    ],
                    max_length=50,
                    verbose_name="Template Type",
                )),
                ("subject", models.CharField(max_length=255, verbose_name="Subject")),
                ("body_html", wagtail.fields.RichTextField(verbose_name="Body (HTML)")),
                ("body_text", models.TextField(
                    help_text="Used as fallback for email clients that do not render HTML.",
                    verbose_name="Body (Plain Text)",
                )),
                ("is_active", models.BooleanField(default=False, verbose_name="Active")),
            ],
            options={
                "verbose_name": "Auth Email Template",
                "verbose_name_plural": "Auth Email Templates",
            },
        ),
    ]
