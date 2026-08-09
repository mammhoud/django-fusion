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
import logging
import os

from django.conf import settings
from django.core.management.base import CommandError
from django_fusion.management.commands.base import BaseCommand
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Set Wagtail root page to HomePage, configure site domain and English locale"

    def handle(self, *args, **options):
        try:
            self._run()
        except Exception as exc:
            logger.exception("setup_wagtail_home failed")
            raise CommandError("Unable to configure the Wagtail home site") from exc

    def _run(self):
        from wagtail.models import Page, Site

        with transaction.atomic():
            # ── 1. Ensure every configured content locale exists ─────────────
            # The archived CTC fixture contract includes six locales. Keeping
            # this repair step here makes a partially restored database safe to
            # boot without changing any fixture primary keys.
            locale_en = self._ensure_locales()

            # ── 2. Find the English home page (direct child of root) ─────────
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
                    site_name=getattr(settings, "WAGTAIL_SITE_NAME", "LMS Fusion"),
                )
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Created default site: {hostname} → '{home.title}'"
                ))

            # ── 6. Set page locale to English ─────────────────────────────────
            if hasattr(home, "locale") and home.locale != locale_en:
                home.locale = locale_en
                home.save(update_fields=["locale"])
                self.stdout.write(self.style.SUCCESS("✅ Set home page locale to English"))

    def _ensure_locales(self):
        """Create all configured Wagtail locales and return the English one."""
        from wagtail.models import Locale

        configured_codes = tuple(
            dict.fromkeys(code for code, _label in settings.LANGUAGES)
        )
        locales = {}
        for code in configured_codes:
            locale, created = Locale.objects.get_or_create(language_code=code)
            locales[code] = locale
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created {code} locale")
                )

        return locales.get("en") or locales[configured_codes[0]]

    def _find_home_page(self):
        """
        Find the real home page — the first live depth=2 page that is NOT
        the default Wagtail 'Welcome to your new Wagtail site!' page.
        Prefers English locale (locale_id=1).
        Falls back to any live depth=2 page.
        If no suitable HomePage exists, create one under the root page.
        """
        from wagtail.models import Page, Site
        from apps.content.models.pages.home import HomePage

        WAGTAIL_DEFAULT_TITLE = "Welcome to your new Wagtail site!"

        # Try the English project-specific HomePage first. This prevents a
        # translated home page from becoming the default site's root merely
        # because it happens to sort first in the tree.
        home = HomePage.objects.filter(
            live=True,
            depth=2,
            locale__language_code="en",
        ).first()
        if home:
            return home

        # Keep compatibility with older databases that have not attached a
        # locale to their custom home page yet.
        home = HomePage.objects.filter(live=True, depth=2).first()
        if home:
            return home

        # No HomePage yet — remove the default welcome page first, then create
        # a HomePage under the root page.
        self.stdout.write(self.style.WARNING(
            "⚠️  No HomePage found — creating a default HomePage under the root page"
        ))

        # Remove the default Wagtail welcome page to free the 'home' slug.
        # Prefer deleting the current default site's root page when it is a
        # plain Wagtail Page (not a HomePage). Fall back to the legacy welcome
        # page title only when no default site exists yet.
        # Fetch the root node *after* deletion so treebeard's numchild state
        # stays in sync and add_child() can compute the new path correctly.
        welcome_page = None
        default_site = Site.objects.filter(is_default_site=True).first()
        if default_site and default_site.root_page:
            root_page = default_site.root_page.specific
            if not isinstance(root_page, HomePage):
                welcome_page = default_site.root_page
        if welcome_page is None:
            welcome_page = Page.objects.filter(
                depth=2, title=WAGTAIL_DEFAULT_TITLE
            ).first()

        if welcome_page:
            welcome_page.delete()
            self.stdout.write(self.style.SUCCESS(
                "✅ Removed default Wagtail welcome page"
            ))

        root = Page.get_first_root_node()

        home = HomePage(
            title="Home",
            slug="home",
            live=True,
            show_in_menus=True,
            head=[],
            summary=[],
            CTA=[],
            contact_form=[],
        )
        root.add_child(instance=home)
        home.save_revision().publish()

        return home

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
                domain = "www.lms-fusion.com"
        return domain
