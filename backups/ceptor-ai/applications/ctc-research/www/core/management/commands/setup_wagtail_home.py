"""
Management command: setup_wagtail_home
======================================
Run after loaddata to:
  1. Set the Wagtail default site's root page to the first live HomePage.
  2. Set the site domain from WAGTAILADMIN_BASE_URL / SITE_DOMAIN env.
  3. Ensure the English locale exists and is active.
  4. Create a default site record if none exists.

Usage:
    python manage.py setup_wagtail_home
"""
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Set Wagtail root page to HomePage, configure site domain and English locale"

    def handle(self, *args, **options):
        try:
            self._run()
        except Exception as exc:
            self.stderr.write(self.style.WARNING(f"⚠️  setup_wagtail_home skipped: {exc}"))

    def _run(self):
        from wagtail.models import Locale, Page, Site

        with transaction.atomic():
            # ── 1. Ensure English locale ──────────────────────────────────────
            locale_en, created = Locale.objects.get_or_create(language_code="en")
            if created:
                self.stdout.write(self.style.SUCCESS("✅ Created English locale"))

            # ── 2. Find the home page (first live child of root, depth=2) ─────
            home = self._find_home_page()
            if not home:
                self.stdout.write(self.style.WARNING(
                    "⚠️  No live HomePage found — skipping root page setup"
                ))
                return

            # ── 3. Ensure home page is at depth=2 (direct child of root) ──────
            root = Page.objects.filter(depth=1).first()
            if root and home.get_parent().pk != root.pk:
                self.stdout.write(self.style.WARNING(
                    f"⚠️  Home page '{home.title}' is not a direct child of root"
                ))

            # ── 4. Resolve site hostname ──────────────────────────────────────
            hostname = self._resolve_hostname()

            # ── 5. Configure the default site ────────────────────────────────
            site = Site.objects.filter(is_default_site=True).first()
            if site:
                changed = False
                if site.root_page_id != home.pk:
                    site.root_page = home
                    changed = True
                if site.hostname != hostname:
                    site.hostname = hostname
                    changed = True
                if changed:
                    site.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Updated site → hostname={hostname}, root='{home.title}'"
                    ))
                else:
                    self.stdout.write(self.style.SUCCESS(
                        f"✅ Site already configured: {hostname} → '{home.title}'"
                    ))
            else:
                Site.objects.create(
                    hostname=hostname,
                    port=443,
                    root_page=home,
                    is_default_site=True,
                    site_name=getattr(settings, "WAGTAIL_SITE_NAME", "CTC Research"),
                )
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Created default site: {hostname} → '{home.title}'"
                ))

            # ── 6. Set page locale to English ─────────────────────────────────
            if hasattr(home, "locale") and home.locale != locale_en:
                home.locale = locale_en
                home.save(update_fields=["locale"])
                self.stdout.write(self.style.SUCCESS("✅ Set home page locale to English"))

    def _find_home_page(self):
        """
        Find the real home page — the first live depth=2 page that is NOT
        the default Wagtail 'Welcome to your new Wagtail site!' page.
        Prefers English locale (locale_id=1).
        Falls back to any live depth=2 page.
        """
        from wagtail.models import Page

        WAGTAIL_DEFAULT_TITLE = "Welcome to your new Wagtail site!"

        # Try project-specific HomePage model first
        for model_path in [
            "www.core.content.models.pages.home.HomePage",
            "www.core.content.models.HomePage",
            "www.apps.content.models.pages.home.HomePage",
        ]:
            try:
                module, cls = model_path.rsplit(".", 1)
                import importlib
                mod = importlib.import_module(module)
                HomePageClass = getattr(mod, cls)
                home = HomePageClass.objects.filter(live=True, depth=2).first()
                if home:
                    return home
            except Exception:
                continue

        # Prefer English (locale_id=1), skip the default welcome page
        home = (
            Page.objects
            .filter(live=True, depth=2, locale_id=1)
            .exclude(title=WAGTAIL_DEFAULT_TITLE)
            .order_by("path")
            .first()
        )
        if home:
            return home

        # Any live depth=2 page that isn't the welcome page
        home = (
            Page.objects
            .filter(live=True, depth=2)
            .exclude(title=WAGTAIL_DEFAULT_TITLE)
            .order_by("path")
            .first()
        )
        if home:
            return home

        # Last resort: keep startup idempotent on a freshly migrated database by
        # using Wagtail's generated welcome page until real content fixtures are
        # loaded.
        return Page.objects.filter(live=True, depth=2).order_by("path").first()

    def _resolve_hostname(self):
        """Resolve hostname from env or settings."""
        # Prefer explicit env var
        domain = os.environ.get("SITE_DOMAIN", "")
        if not domain:
            base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "")
            domain = base_url.replace("https://", "").replace("http://", "").rstrip("/")
        if not domain:
            domain = os.environ.get("ALLOWED_HOSTS", "localhost").split(",")[0].strip()
            if domain in ("*", ""):
                domain = "www.ctc-research.com"
        return domain
