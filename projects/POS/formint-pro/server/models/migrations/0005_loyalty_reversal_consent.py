from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pos_full", "0004_menu_versions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loyaltytransaction",
            name="transaction_type",
            field=models.CharField(
                choices=[
                    ("earn", "Earn"),
                    ("redeem", "Redeem"),
                    ("adjust", "Adjustment"),
                    ("expire", "Expiry"),
                    ("reversal", "Reversal"),
                ],
                default="earn",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="customer",
            name="marketing_consent",
            field=models.BooleanField(
                default=False,
                help_text="Customer consented to marketing communications (GDPR).",
            ),
        ),
        migrations.AddField(
            model_name="customer",
            name="consent_granted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
