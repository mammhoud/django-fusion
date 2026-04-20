"""
Management command: setup_wagtail_home
======================================
Ensures the Wagtail default site's root page is set to the first
live HomePage instance. Creates a default site record if none exists.

Usage:
    python com setup_wagtail_home
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Set Wagtail root page to HomePage and configure default site"

    def handle(self, *args, **options):
        try:
            from wagtail.models import Page, Site

            from www.apps.content.models.pages.home import HomePage

            with transaction.atomic():
                # Find or create a HomePage
                home = HomePage.objects.filter(live=True).first()

                if not home:
                    self.stdout.write(self.style.WARNING(
                        "No live HomePage found. Skipping root page setup."
                    ))
                    return

                # Get or create the default site
                site = Site.objects.filter(is_default_site=True).first()

                if site:
                    if site.root_page_id != home.pk:
                        site.root_page = home
                        site.save()
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ Updated default site root page → '{home.title}' (pk={home.pk})"
                        ))
                    else:
                        self.stdout.write(self.style.SUCCESS(
                            f"✅ Default site already points to '{home.title}'"
                        ))
                else:
                    from django.conf import settings as django_settings
                    hostname = getattr(django_settings, "WAGTAILADMIN_BASE_URL", "localhost")
                    hostname = hostname.replace("https://", "").replace("http://", "").rstrip("/")
                    Site.objects.create(
                        hostname=hostname,
                        port=80,
                        root_page=home,
                        is_default_site=True,
                        site_name=getattr(django_settings, "WAGTAIL_SITE_NAME", "CTC Hub"),
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Created default site with root page '{home.title}'"
                    ))

        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"❌ setup_wagtail_home failed: {exc}"))
