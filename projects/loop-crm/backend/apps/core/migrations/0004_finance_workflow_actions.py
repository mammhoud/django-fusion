from django.db import migrations


def add_finance_action(apps, schema_editor):
    definition = apps.get_model("core", "WorkflowDefinition")
    definition.objects.filter(slug="deal-won", workspace__isnull=True).update(
        actions=[
            "recalculate_attribution",
            "update_campaign_roi",
            "create_invoice",
            "notify_revops",
        ]
    )


def remove_finance_action(apps, schema_editor):
    definition = apps.get_model("core", "WorkflowDefinition")
    definition.objects.filter(slug="deal-won", workspace__isnull=True).update(
        actions=["recalculate_attribution", "update_campaign_roi", "notify_revops"]
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0003_workflow_index_names")]

    operations = [migrations.RunPython(add_finance_action, remove_finance_action)]
