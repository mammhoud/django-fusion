from django.db import migrations

WORKFLOW_TEMPLATES = (
    {
        "slug": "invoice-dunning",
        "name": "Chase an overdue invoice",
        "module": "finance",
        "description": "Mark a past-due invoice overdue, notify the contact, and schedule a follow-up.",
        "trigger": "invoice.due_date_passed",
        "actions": ["mark_invoice_overdue", "send_email", "create_follow_up_task"],
    },
    {
        "slug": "payment-received",
        "name": "Attribute a received payment",
        "module": "finance",
        "description": "Refresh campaign revenue and alert RevOps when a payment lands.",
        "trigger": "payment.created",
        "actions": ["update_campaign_roi", "notify_revops"],
    },
    {
        "slug": "pos-revenue-reconciled",
        "name": "Reconcile POS revenue",
        "module": "pos",
        "description": "Bridge an ingested Formint POS sale into the finance trend.",
        "trigger": "pos_sale.ingested",
        "actions": ["reconcile_pos_sale", "notify_revops"],
    },
    {
        "slug": "contact-nurture",
        "name": "Welcome a new contact",
        "module": "crm",
        "description": "Assign ownership and send a welcome note when a contact arrives.",
        "trigger": "contact.created",
        "actions": ["assign_owner", "send_email"],
    },
)


def seed_workflow_templates(apps, schema_editor):
    definition = apps.get_model("core", "WorkflowDefinition")
    for template in WORKFLOW_TEMPLATES:
        definition.objects.update_or_create(
            workspace=None,
            slug=template["slug"],
            defaults={**template, "status": "active"},
        )


def unseed_workflow_templates(apps, schema_editor):
    definition = apps.get_model("core", "WorkflowDefinition")
    definition.objects.filter(
        workspace__isnull=True,
        slug__in=[template["slug"] for template in WORKFLOW_TEMPLATES],
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0007_workspace_external_ref_workspace_source")]

    operations = [migrations.RunPython(seed_workflow_templates, unseed_workflow_templates)]
