# Tenant settings JSON column — per-tenant identity-layer overrides
# (signup gate, social provider keys, login redirect, branch adapter aliases).
# Read by apps.core.auth_adapters / services.tenant_providers.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_branchsettings_tenant_domain'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenant',
            name='settings',
            field=models.JSONField(blank=True, default=dict, verbose_name='settings'),
        ),
    ]
