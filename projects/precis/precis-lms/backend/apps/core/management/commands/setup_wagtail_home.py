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
from django.db import transaction
from django_fusion.management.commands.base import BaseCommand

logger = logging.getLogger(__name__)


DEFAULT_SITE_LANGUAGES = (
    ("en", "English", "English", "ltr", "🇬🇧"),
    ("sv", "Swedish", "Svenska", "ltr", "🇸🇪"),
    ("fr", "French", "Français", "ltr", "🇫🇷"),
    ("de", "German", "Deutsch", "ltr", "🇩🇪"),
    ("es", "Spanish", "Español", "ltr", "🇪🇸"),
    ("ar", "Arabic", "العربية", "rtl", "🇸🇦"),
    ("pt-br", "Portuguese (Brazil)", "Português (Brasil)", "ltr", "🇧🇷"),
)


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

            # ── 6. Seed editor-managed catalog/settings defaults ─────────────
            self._ensure_site_content(site)

            # ── 7. Set page locale to English ─────────────────────────────────
            if hasattr(home, "locale") and home.locale != locale_en:
                home.locale = locale_en
                home.save(update_fields=["locale"])
                self.stdout.write(self.style.SUCCESS("✅ Set home page locale to English"))

    def _ensure_site_content(self, site):
        """Create safe, idempotent language and branding defaults.

        These are bootstrap records only: ``get_or_create`` never overwrites
        values an editor has already changed in Wagtail. The API can therefore
        use the database catalog immediately after a fixture restore without
        introducing a second source of truth.
        """
        from apps.content.models.languages import SiteLanguage

        for order, (code, name, native_name, direction, flag) in enumerate(
            DEFAULT_SITE_LANGUAGES
        ):
            SiteLanguage.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "native_name": native_name,
                    "direction": direction,
                    "flag": flag,
                    "sort_order": order,
                    "is_active": True,
                },
            )

        try:
            from apps.pages.branding.models import FusionBranding

            FusionBranding.objects.get_or_create(
                pk=1,
                defaults={
                    "site_name": getattr(settings, "FUSION_SITE_NAME", "Fusion LMS"),
                    "company_name": getattr(settings, "FUSION_COMPANY_NAME", "Fusion Inc."),
                    "creator_name": getattr(settings, "FUSION_CREATOR_NAME", "Fusion Team"),
                    "primary_color": getattr(settings, "FUSION_PRIMARY_COLOR", "#00a1b3"),
                    "secondary_color": getattr(settings, "FUSION_SECONDARY_COLOR", "#008080"),
                },
            )
        except Exception:
            # Branding is optional for older restored databases; language
            # records and Wagtail site setup should still complete.
            logger.exception("Unable to seed optional FusionBranding snippet")

        try:
            from apps.content.models.settings import SiteSettings

            SiteSettings.objects.get_or_create(
                site=site,
                defaults={
                    "site_name": getattr(settings, "FUSION_SITE_NAME", "Fusion LMS"),
                    "site_tagline": "Learning that ships.",
                    "footer_description": "A modern learning platform powered by django-fusion.",
                    "footer_copyright": "© 2026 Fusion LMS",
                    "privacy_policy_url": "/privacy/",
                    "terms_of_use_url": "/legal/terms/",
                },
            )
        except Exception:
            # Keep bootstrapping compatible with databases created before the
            # optional settings migration was installed.
            logger.exception("Unable to seed optional SiteSettings")

        self._seed_product_snippets()

        self.stdout.write(self.style.SUCCESS("✅ Site language/settings defaults ready"))

    def _seed_product_snippets(self):
        """Create/update the editor-managed ``Product`` snippet catalog.

        Mirrors precis-landing's ``seed_pages._seed_product_snippets`` so both
        websites share one catalog architecture (language + unified currency).
        Idempotent: existing rows keep editor changes. Each product gets an
        English row plus an Arabic variant row (title-only translation) whose
        ``detail_slug`` points at the canonical product page.
        """
        from apps.content.models.products import Product

        catalog = [
            {
                "slug": "django-fusion",
                "title": "django-fusion",
                "title_ar": "جانغو-فيوجن",
                "category": "library",
                "tagline": "Component system, routing and fragment rendering for every structa.cloud site.",
                "price": "0.00",
                "version": "",
            },
            {
                "slug": "ceptor-ai",
                "title": "ceptor-ai",
                "title_ar": "سيبتور إيه آي",
                "category": "platform",
                "tagline": "AI chat client with a Model Context Protocol (MCP) server.",
                "price": "0.00",
                "version": "",
            },
            {
                "slug": "django-bolt",
                "title": "django-bolt",
                "title_ar": "جانغو بولت",
                "category": "library",
                "tagline": "A high-performance Rust-backed API framework for Django.",
                "price": "0.00",
                "version": "",
            },
            {
                "slug": "vresume",
                "title": "vResume",
                "title_ar": "فيريسوم",
                "category": "platform",
                "tagline": "Cloud-hosted resume builder with modern templates.",
                "price": "29.00",
                "version": "",
            },
            {
                "slug": "forge-pos",
                "title": "Forge POS",
                "title_ar": "فورج بي أو إس",
                "category": "application",
                "tagline": "Desktop point-of-sale application built on Tauri 2 + Rust.",
                "price": "119.00",
                "version": "",
            },
            {
                "slug": "cypercloud",
                "title": "Cypercloud",
                "title_ar": "سايبر كلاود",
                "category": "platform",
                "tagline": "AI chat customizer platform powered by ceptor-ai.",
                "price": "0.00",
                "version": "",
            },
        ]
        try:
            for entry in catalog:
                defaults = {
                    "title": entry["title"],
                    "short_description": entry["tagline"],
                    "category": entry["category"],
                    "language": "en",
                    "price": entry["price"],
                    "version": entry["version"],
                    "is_published": True,
                }
                item, created = Product.objects.get_or_create(slug=entry["slug"], defaults=defaults)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded product snippet {entry['slug']} (en)."))
                ar_defaults = {
                    **defaults,
                    "title": entry["title_ar"],
                    "language": "ar",
                    "slug": f"{entry['slug']}-ar",
                    "detail_slug": entry["slug"],
                }
                ar_item, ar_created = Product.objects.get_or_create(
                    slug=ar_defaults["slug"], defaults=ar_defaults
                )
                if ar_created:
                    self.stdout.write(self.style.SUCCESS(f"Seeded product snippet {entry['slug']} (ar)."))
        except Exception:
            # Products are optional for older restored databases; the rest of
            # the site bootstrap should still complete.
            logger.exception("Unable to seed product snippets")

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
                domain = "www.precis-lms.com"
        return domain
