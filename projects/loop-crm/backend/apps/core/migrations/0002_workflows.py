import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

WORKFLOW_TEMPLATES = (
    {
        "slug": "lead-capture",
        "name": "Route a new lead",
        "module": "crm",
        "description": "Assign ownership and create the first sales follow-up when a contact arrives.",
        "trigger": "contact.created",
        "actions": ["assign_owner", "create_activity", "notify_sales"],
    },
    {
        "slug": "content-approval",
        "name": "Approve scheduled content",
        "module": "marketing",
        "description": "Move submitted posts through review before they enter the publishing queue.",
        "trigger": "post.submitted_for_review",
        "actions": ["request_approval", "notify_marketing_manager"],
    },
    {
        "slug": "publish-and-attribute",
        "name": "Publish and create touchpoint",
        "module": "marketing",
        "description": "Record the published interaction and refresh its performance metrics.",
        "trigger": "post.published",
        "actions": ["publish_to_channels", "record_touchpoint", "refresh_analytics"],
    },
    {
        "slug": "deal-won",
        "name": "Close the revenue loop",
        "module": "attribution",
        "description": "Recalculate influence and update campaign revenue when a deal is won.",
        "trigger": "deal.stage_changed:closed_won",
        "actions": ["recalculate_attribution", "update_campaign_roi", "notify_revops"],
    },
)


def seed_workflow_templates(apps, schema_editor):
    definition = apps.get_model("core", "WorkflowDefinition")
    for template in WORKFLOW_TEMPLATES:
        definition.objects.update_or_create(
            workspace=None,
            slug=template["slug"],
            defaults={
                **template,
                "status": "active",
            },
        )


def unseed_workflow_templates(apps, schema_editor):
    definition = apps.get_model("core", "WorkflowDefinition")
    definition.objects.filter(
        workspace__isnull=True,
        slug__in=[template["slug"] for template in WORKFLOW_TEMPLATES],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowDefinition",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=120)),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("module", models.CharField(default="workspace", max_length=40)),
                ("trigger", models.CharField(max_length=120)),
                ("trigger_config", models.JSONField(blank=True, default=dict)),
                ("actions", models.JSONField(default=list)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("active", "Active"), ("paused", "Paused"), ("archived", "Archived")], default="draft", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_workflows", to=settings.AUTH_USER_MODEL)),
                ("workspace", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="workflow_definitions", to="core.workspace")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="WorkflowRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("queued", "Queued"), ("running", "Running"), ("succeeded", "Succeeded"), ("failed", "Failed"), ("cancelled", "Cancelled")], default="queued", max_length=20)),
                ("trigger_payload", models.JSONField(blank=True, default=dict)),
                ("result", models.JSONField(blank=True, default=dict)),
                ("error", models.TextField(blank=True)),
                ("queued_at", models.DateTimeField(auto_now_add=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("definition", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="runs", to="core.workflowdefinition")),
                ("workspace", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="workflow_runs", to="core.workspace")),
            ],
            options={"ordering": ["-queued_at"]},
        ),
        migrations.AddConstraint(
            model_name="workflowdefinition",
            constraint=models.UniqueConstraint(fields=("workspace", "slug"), name="uniq_workflow_workspace_slug"),
        ),
        migrations.AddIndex(
            model_name="workflowdefinition",
            index=models.Index(fields=["workspace", "status"], name="core_workfl_workspa_05ed9a_idx"),
        ),
        migrations.AddIndex(
            model_name="workflowrun",
            index=models.Index(fields=["workspace", "status"], name="core_workfl_workspa_1c5c99_idx"),
        ),
        migrations.AddIndex(
            model_name="workflowrun",
            index=models.Index(fields=["definition", "queued_at"], name="core_workfl_definit_4b3d1c_idx"),
        ),
        migrations.RunPython(seed_workflow_templates, unseed_workflow_templates),
    ]
