"""Seed EditorialSettings from the SHOP_EDITORIAL settings payload.

The settings value was the source of truth before Wagtail site settings took
over. Copy it into the first site's EditorialSettings row so the admin shows
the live content and /fusion/editorial/ serves the DB (settings remains the
fallback only when the streams are empty).
"""

import uuid

from django.conf import settings as django_settings
from django.db import migrations


def seed_editorial(apps, schema_editor):
    EditorialSettings = apps.get_model("cms", "EditorialSettings")
    Site = apps.get_model("wagtailcore", "Site")
    site = Site.objects.order_by("pk").first()
    if site is None or EditorialSettings.objects.exists():
        return
    editorial = getattr(django_settings, "SHOP_EDITORIAL", {})
    craft = [
        {"type": "panel", "value": panel, "id": uuid.uuid4().hex}
        for panel in editorial.get("craft", [])
    ]
    voices = [
        {"type": "voice", "value": voice, "id": uuid.uuid4().hex}
        for voice in editorial.get("voices", [])
    ]
    EditorialSettings.objects.create(site=site, craft=craft, voices=voices)


class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0002_editorialsettings"),
    ]

    operations = [
        migrations.RunPython(seed_editorial, migrations.RunPython.noop),
    ]
