import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("crm", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomFieldDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("object_type", models.CharField(choices=[("company", "Company"), ("contact", "Contact"), ("deal", "Deal"), ("campaign", "Campaign"), ("post", "Post")], max_length=30)),
                ("key", models.SlugField(max_length=80)),
                ("label", models.CharField(max_length=120)),
                ("field_type", models.CharField(choices=[("text", "Text"), ("textarea", "Long text"), ("number", "Number"), ("boolean", "Boolean"), ("date", "Date"), ("url", "URL"), ("email", "Email"), ("select", "Select"), ("multi_select", "Multi-select")], max_length=20)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("required", models.BooleanField(default=False)),
                ("options", models.JSONField(blank=True, default=list)),
                ("validation", models.JSONField(blank=True, default=dict)),
                ("position", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_custom_fields", to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="custom_field_definitions", to="core.workspace")),
            ],
            options={"ordering": ["object_type", "position", "label"]},
        ),
        migrations.AddConstraint(
            model_name="customfielddefinition",
            constraint=models.UniqueConstraint(fields=("workspace", "object_type", "key"), name="uniq_custom_field_workspace_object_key"),
        ),
        migrations.AddIndex(
            model_name="customfielddefinition",
            index=models.Index(fields=["workspace", "object_type", "is_active"], name="crm_customf_workspa_b3290f_idx"),
        ),
    ]
