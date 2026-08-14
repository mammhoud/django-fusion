import decimal

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0003_workflow_index_names"),
        ("crm", "0002_custom_field_definitions"),
        ("marketing", "0002_alter_post_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=40)),
                ("currency", models.CharField(default="USD", max_length=3)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("issued", "Issued"), ("partially_paid", "Partially paid"), ("paid", "Paid"), ("overdue", "Overdue"), ("void", "Void")], default="draft", max_length=20)),
                ("issued_on", models.DateField(default=django.utils.timezone.localdate)),
                ("due_on", models.DateField()),
                ("subtotal", models.DecimalField(decimal_places=2, max_digits=15, validators=[MinValueValidator(decimal.Decimal("0.00"))])),
                ("tax", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), max_digits=15, validators=[MinValueValidator(decimal.Decimal("0.00"))])),
                ("total", models.DecimalField(decimal_places=2, default=decimal.Decimal("0.00"), editable=False, max_digits=15)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="invoices", to="crm.company")),
                ("contact", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="invoices", to="crm.contact")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_invoices", to=settings.AUTH_USER_MODEL)),
                ("deal", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="invoices", to="crm.deal")),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to="core.workspace")),
            ],
            options={"ordering": ["-issued_on", "-created_at"]},
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15, validators=[MinValueValidator(decimal.Decimal("0.01"))])),
                ("paid_on", models.DateField(default=django.utils.timezone.localdate)),
                ("method", models.CharField(choices=[("bank_transfer", "Bank transfer"), ("card", "Card"), ("cash", "Cash"), ("other", "Other")], default="bank_transfer", max_length=20)),
                ("reference", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_payments", to=settings.AUTH_USER_MODEL)),
                ("invoice", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="payments", to="finance.invoice")),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="core.workspace")),
            ],
            options={"ordering": ["-paid_on", "-created_at"]},
        ),
        migrations.CreateModel(
            name="RevenueEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("deal_won", "Deal won"), ("expansion", "Expansion"), ("renewal", "Renewal"), ("refund", "Refund")], default="deal_won", max_length=20)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15, validators=[MinValueValidator(decimal.Decimal("0.00"))])),
                ("recognized_on", models.DateField(default=django.utils.timezone.localdate)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("campaign", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="revenue_events", to="marketing.campaign")),
                ("deal", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="revenue_events", to="crm.deal")),
                ("invoice", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="revenue_events", to="finance.invoice")),
                ("workspace", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="revenue_events", to="core.workspace")),
            ],
            options={"ordering": ["-recognized_on", "-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="invoice",
            constraint=models.UniqueConstraint(fields=("workspace", "number"), name="uniq_invoice_workspace_number"),
        ),
        migrations.AddConstraint(
            model_name="revenueevent",
            constraint=models.UniqueConstraint(fields=("workspace", "deal", "kind"), name="uniq_revenue_event_deal_kind"),
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["workspace", "status"], name="finance_inv_workspa_0f5b31_idx"),
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["workspace", "due_on"], name="finance_inv_workspa_24d5cc_idx"),
        ),
        migrations.AddIndex(
            model_name="payment",
            index=models.Index(fields=["workspace", "paid_on"], name="finance_pay_workspa_9c2f60_idx"),
        ),
        migrations.AddIndex(
            model_name="revenueevent",
            index=models.Index(fields=["workspace", "recognized_on"], name="finance_rev_workspa_8f0f90_idx"),
        ),
        migrations.AddIndex(
            model_name="revenueevent",
            index=models.Index(fields=["workspace", "campaign"], name="finance_rev_workspa_ef5a5f_idx"),
        ),
    ]
