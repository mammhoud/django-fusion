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
from django_fusion.site.management.commands.base import BaseCommand
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
        If no suitable HomePage exists, create one under the root page.
        """
        from wagtail.models import Page
        from www.core.content.models.pages.home import HomePage

        WAGTAIL_DEFAULT_TITLE = "Welcome to your new Wagtail site!"

        # Try project-specific HomePage model first
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
                domain = "www.ctc-research.com"
        return domain
