"""
Migration: add proxy models for payment admin views.

PaymentTransaction, PaymentRefund, and PaymentWebhookLog are all proxy
models over Enrollment — they share the same DB table and require no
schema changes, only a Django model-state entry.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("alliance", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PaymentTransaction",
            fields=[],
            options={
                "proxy": True,
                "verbose_name": "Payment Transaction",
                "verbose_name_plural": "Payment Transactions",
                "indexes": [],
                "constraints": [],
            },
            bases=("alliance.enrollment",),
        ),
        migrations.CreateModel(
            name="PaymentRefund",
            fields=[],
            options={
                "proxy": True,
                "verbose_name": "Payment Refund",
                "verbose_name_plural": "Payment Refunds",
                "indexes": [],
                "constraints": [],
            },
            bases=("alliance.enrollment",),
        ),
        migrations.CreateModel(
            name="PaymentWebhookLog",
            fields=[],
            options={
                "proxy": True,
                "verbose_name": "Payment Webhook Log",
                "verbose_name_plural": "Payment Webhook Logs",
                "indexes": [],
                "constraints": [],
            },
            bases=("alliance.enrollment",),
        ),
    ]
