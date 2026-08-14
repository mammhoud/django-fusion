"""Point stored SiteSettings header CTA at the real contact page.

Rows created before the ``nav_cta_url`` default changed still carry the
legacy ``/#cta`` anchor, which dead-ends on any page without a CTA section
(``APPEND_SLASH`` is off, so no silent redirect). Rewrite them to the live
contact page; the reverse restores the legacy value for downgrades.
"""

from django.db import migrations

LEGACY = "/#cta"
CURRENT = "/contact/"


def update_nav_cta(apps, schema_editor):
    SiteSettings = apps.get_model("content", "SiteSettings")
    SiteSettings.objects.filter(nav_cta_url=LEGACY).update(nav_cta_url=CURRENT)


def restore_nav_cta(apps, schema_editor):
    SiteSettings = apps.get_model("content", "SiteSettings")
    SiteSettings.objects.filter(nav_cta_url=CURRENT).update(nav_cta_url=LEGACY)


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0008_alter_sitesettings_nav_cta_url"),
    ]

    operations = [
        migrations.RunPython(update_nav_cta, restore_nav_cta),
    ]
