#!/usr/bin/env python3
"""
seed_static_pages — Migrate STATIC_PAGES content into Wagtail CMS pages.

Reads the STATIC_PAGES dictionary from www/api/pages.py and creates or updates
corresponding Wagtail pages (HomePage, AboutPage, ContactPage) with mapped
StreamField content.

NOTE: The block structure in STATIC_PAGES (hero, stats, faq_groups, etc.) differs
from the Wagtail page model blocks (slider, features, about, testimonials, etc.).
The mapping is approximate — created pages are primarily for Wagtail admin editing
and SEO. The frontend API at /apis/pages/<slug>/ continues to read from STATIC_PAGES
(www/api/pages.py) which is the canonical source.

Pages without dedicated Wagtail models (faq, privacy) use STATIC_PAGES exclusively
and are skipped by this command.

Usage:
    uv run python manage.py seed_static_pages
    uv run python manage.py seed_static_pages --dump
    uv run python manage.py seed_static_pages --reset --dump

Options:
    --dump       Dump Wagtail page fixture JSON files after seeding
    --reset      Delete existing seeded pages and recreate
    --dry-run    Show what would be done without making changes
"""

import json
import os
from datetime import datetime
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction


# ── Import canonical page data ──────────────────────────────────────
def _get_static_pages():
    """Lazy-import STATIC_PAGES from the pages API module."""
    from www.api.pages import STATIC_PAGES as _sp
    return _sp


class Command(BaseCommand):
    help = "Seed Wagtail CMS pages with STATIC_PAGES content"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dump", action="store_true",
            help="Dump Wagtail page fixture JSON files after seeding"
        )
        parser.add_argument(
            "--reset", action="store_true",
            help="Delete existing seeded pages and recreate from scratch"
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would be done without making changes"
        )
        parser.add_argument(
            "--fixtures-dir", default=None,
            help="Output directory for fixture files"
        )

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.do_reset = options["reset"]
        self.do_dump = options["dump"]

        # Resolve fixture output directory
        fixture_dir = options.get("fixtures_dir")
        if not fixture_dir:
            site_dir = Path(__file__).resolve().parents[4]  # → cms/
            fixture_dir = str(site_dir / "assets" / "fixtures")
        self.fixture_dir = Path(fixture_dir)

        # Get canonical page data
        self.pages = _get_static_pages()

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "\n🚀  Seeding Wagtail CMS pages from STATIC_PAGES...\n"
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                "NOTE: Block mapping is approximate (STATIC_PAGES → Wagtail StreamField).\n"
                "      The frontend API continues to use STATIC_PAGES as its source.\n"
                "      Pages without Wagtail models (faq, privacy) are skipped.\n"
            )
        )

        # ── Deferred Wagtail imports ─────────────────────────────
        from wagtail.models import Page as WagtailPage, Site, Locale

        from www.core.content.models.pages.about import AboutPage
        from www.core.content.models.pages.contact import ContactPage
        from www.core.content.models.pages.home import HomePage

        self.WagtailPage = WagtailPage
        self.Site = Site
        self.Locale = Locale
        self.HomePage = HomePage
        self.AboutPage = AboutPage
        self.ContactPage = ContactPage

        # ── Locale ───────────────────────────────────────────────
        self.locale, _ = Locale.objects.get_or_create(language_code="en")

        # ── Page tree ────────────────────────────────────────────
        root = WagtailPage.objects.get(depth=1)
        home = self._get_or_create_home(root)

        # ── Seed pages ───────────────────────────────────────────
        results = []
        for slug in ("home", "about-us", "contact", "faq", "privacy"):
            data = self.pages.get(slug)
            if not data:
                results.append((slug, "skip", "Not found in STATIC_PAGES"))
                continue
            if slug == "home":
                results.append(self._populate_home(home, data))
            elif slug in ("about-us", "contact"):
                results.append(self._seed_child_page(home, slug, data))
            else:
                # FAQ and Privacy — no dedicated Wagtail model
                results.append(
                    (slug, "skip", "No dedicated Wagtail page model; uses STATIC_PAGES")
                )

        # ── Site configuration ───────────────────────────────────
        site = self._configure_site(home)

        # ── Report ───────────────────────────────────────────────
        self.stdout.write("")
        for slug, status, detail in results:
            style = {
                "ok": self.style.SUCCESS,
                "skip": self.style.WARNING,
                "err": self.style.ERROR,
            }.get(status, self.style.NOTICE)
            self.stdout.write(style(f"  {status.upper():4s}  /{slug}/  →  {detail}"))

        if not self.dry_run:
            ok_count = sum(1 for _, s, _ in results if s == "ok")
            skip_count = sum(1 for _, s, _ in results if s == "skip")
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✅  {ok_count} page(s) seeded, {skip_count} skipped."
                )
            )
            if site:
                self.stdout.write(
                    f"   Site:  https://{site.hostname}/\n"
                    f"   Admin: /admin/pages/\n"
                )

            if self.do_dump:
                self._dump_fixtures()

    # ── Page tree ────────────────────────────────────────────────────

    def _get_or_create_home(self, root):
        """Find or create the HomePage under root."""
        locale = self.locale
        home_page = self.HomePage.objects.filter(locale=locale).first()
        if home_page:
            self.stdout.write(f"  📄  Found existing HomePage (id={home_page.id})")
            if not self.do_reset:
                return home_page
            self.stdout.write("  🔄  --reset: will recreate HomePage content")

        if self.dry_run:
            self.stdout.write("  📋  Would create HomePage under root")
            return None

        if home_page and self.do_reset:
            home_page.delete()

        data = self.pages.get("home", {})
        home_page = self.HomePage(
            title=data.get("title", "Home"),
            slug="home",
            locale=locale,
        )
        root.add_child(instance=home_page)
        # Will be published after content is populated
        self.stdout.write(f"  ✅  Created HomePage (id={home_page.id})")
        return home_page

    def _seed_child_page(self, parent, slug, data):
        """Create or update a child Wagtail page (AboutPage, ContactPage)."""
        model_map = {
            "about-us": self.AboutPage,
            "contact": self.ContactPage,
        }
        model_class = model_map.get(slug)
        if model_class is None:
            return (slug, "skip", "No Wagtail model for this slug")

        try:
            existing = model_class.objects.get(slug=slug, locale=self.locale)
            if existing and not self.do_reset:
                return (slug, "ok", f"Already exists (id={existing.id}); use --reset")
            if existing and self.do_reset:
                existing.delete()
        except model_class.DoesNotExist:
            existing = None

        if self.dry_run:
            return (slug, "ok", f"Would create {model_class.__name__} under {parent.slug}")

        page = model_class(
            title=data.get("title", slug),
            slug=slug,
            locale=self.locale,
        )
        parent.add_child(instance=page)

        # Populate page-specific content
        if slug == "about-us":
            self._populate_about_page(page, data)
        elif slug == "contact":
            self._populate_contact_page(page, data)

        rev = page.save_revision(log_action=True)
        rev.publish()

        return (slug, "ok", f"Created {model_class.__name__} (id={page.id})")

    # ── Content population ──────────────────────────────────────────

    def _populate_home(self, page, data):
        """Populate HomePage StreamFields from STATIC_PAGES blocks."""
        if self.dry_run:
            return ("home", "ok", "Would populate HomePage content")
        if not page:
            return ("home", "skip", "No HomePage to populate")

        head_blocks = []
        summary_blocks = []
        cta_blocks = []

        for block in data.get("blocks", []):
            btype = block.get("type")
            if btype == "hero":
                head_blocks.append((
                    "slider",
                    [("slide", {
                        "background_image": None,
                        "subtitle": "Welcome",
                        "title": block.get("heading", ""),
                        "video_url": "",
                    })],
                ))
            elif btype == "stats":
                features = []
                for item in block.get("items", []):
                    features.append(("feature", {
                        "icon_class": "flaticon-happy",
                        "image": None,
                        "title": item.get("label", "Stat"),
                        "description": f"{item.get('value', '0')} — {item.get('description', '')}",
                    }))
                if features:
                    head_blocks.append(("features", features))
            elif btype == "section_header":
                summary_blocks.append(("listing_section", {
                    "subtitle": block.get("intro", ""),
                    "title": block.get("heading", ""),
                    "listing_pages": [],
                }))
            elif btype == "cta":
                cta_blocks.append(("why_choose_section", {
                    "subtitle": "Get Started",
                    "title": block.get("heading", "Start Learning Today"),
                    "description": block.get("intro", ""),
                    "highlight_text": "Join Now",
                    "methods": [],
                    "image": None,
                    "button": None,
                }))

        with transaction.atomic():
            if head_blocks:
                page.head = head_blocks
            if summary_blocks:
                page.summary = summary_blocks
            if cta_blocks:
                page.CTA = cta_blocks
            if not page.contact_form:
                page.contact_form = [("contact_form", {})]
            rev = page.save_revision(log_action=True)
            rev.publish()
            page.refresh_from_db()

        return ("home", "ok", f"Populated HomePage (id={page.id})")

    def _populate_about_page(self, page, data):
        """Populate AboutPage StreamFields."""
        head_blocks = []
        facts_blocks = []

        for block in data.get("blocks", []):
            btype = block.get("type")
            if btype == "hero":
                head_blocks.append(("page_title", {
                    "page_title_background": None,
                    "page_title": block.get("heading", "About Us"),
                    "breadcrumb_home_text": "Home",
                }))
            elif btype == "stats":
                counters = []
                for item in block.get("items", []):
                    raw = item.get("value", "0")
                    num = int(raw.replace("+", "").replace("K", "000"))
                    counters.append(("counter", {
                        "icon_class": "flaticon-happy",
                        "number": num,
                        "label": item.get("label", ""),
                    }))
                facts_blocks.append(("about", {
                    "background_image": None,
                    "welcome_text": "About Us",
                    "main_title": "About",
                    "description": "",
                    "years_experience": 5,
                    "experience_description": "<p>Building the future of education</p>",
                    "video_link": "",
                    "gallery": [],
                    "counters": counters,
                }))
            elif btype == "rich_section":
                items = block.get("items", [])
                if items:
                    testimonial_list = [("testimonial", {
                        "content": f"<p>{it.get('text', '')}</p>",
                        "client_photo": None,
                        "client_name": it.get("heading", ""),
                        "client_position": "",
                    }) for it in items]
                    facts_blocks.append(("testimonials", {
                        "subtitle": block.get("heading", ""),
                        "title": "",
                        "background_image": None,
                        "video_url": "",
                        "testimonials": testimonial_list,
                    }))

        with transaction.atomic():
            if head_blocks:
                page.head = head_blocks
            if facts_blocks:
                page.facts = facts_blocks
            rev = page.save_revision(log_action=True)
            rev.publish()
            page.refresh_from_db()

    def _populate_contact_page(self, page, data):
        """Populate ContactPage StreamFields."""
        head_blocks = []
        info_blocks = []
        detail_blocks = []

        for block in data.get("blocks", []):
            btype = block.get("type")
            if btype == "hero":
                head_blocks.append(("page_title", {
                    "page_title_background": None,
                    "page_title": block.get("heading", "Contact Us"),
                    "breadcrumb_home_text": "Home",
                }))
            elif btype == "contact_methods":
                for item in block.get("items", []):
                    ctype = item.get("type", "")
                    if ctype == "email":
                        detail_blocks.append(("email", {
                            "icon_class": "flaticon-email",
                            "title": item.get("label", "Email"),
                            "lines": [item.get("value", "")],
                        }))
                    elif ctype == "phone":
                        detail_blocks.append(("phone", {
                            "icon_class": "flaticon-support-1",
                            "title": item.get("label", "Phone"),
                            "lines": [item.get("value", "")],
                        }))
                    elif ctype == "address":
                        detail_blocks.append(("address", {
                            "icon_class": "flaticon-house",
                            "title": item.get("label", "Address"),
                            "lines": [item.get("value", "")],
                        }))
            elif btype == "form":
                info_blocks.append(("contact_info", {
                    "subtitle": "",
                    "title": block.get("heading", "Send us a message"),
                    "description": "",
                }))

        with transaction.atomic():
            if head_blocks:
                page.head = head_blocks
            if info_blocks:
                page.contact_info = info_blocks
            if detail_blocks:
                page.contact_details = detail_blocks
            if not page.contact_form:
                page.contact_form = [("contact_form", {})]
            rev = page.save_revision(log_action=True)
            rev.publish()
            page.refresh_from_db()

    # ── Site ─────────────────────────────────────────────────────────

    def _configure_site(self, home_page):
        """Ensure the Wagtail Site record points to the seeded HomePage."""
        if self.dry_run or not home_page:
            return None

        site, created = self.Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                "site_name": "LMS Platform",
                "hostname": "localhost",
                "port": 8000,
                "root_page": home_page,
            },
        )
        if not created:
            site.root_page = home_page
            site.hostname = site.hostname or "localhost"
            site.save()
        return site

    # ── Fixture dumping ─────────────────────────────────────────────

    def _dump_fixtures(self):
        """Dump seeded Wagtail pages as fixture JSON files for production loading.

        Produces two files:
          - wagtail_pages.json: full Wagtail page tree via dumpdata
          - static_pages_reference.json: STATIC_PAGES data as reference (for docs/manual loading)
        """
        self.stdout.write("\n📦  Dumping fixtures...")
        self.fixture_dir.mkdir(parents=True, exist_ok=True)

        # 1. Dump Wagtail pages via dumpdata
        try:
            out_path = self.fixture_dir / "wagtail_pages.json"
            with open(out_path, "w", encoding="utf-8") as f:
                call_command(
                    "dumpdata",
                    "wagtailcore.page",
                    "wagtailcore.site",
                    "content.homepage",
                    "content.aboutpage",
                    "content.contactpage",
                    output=f,
                    indent=2,
                    natural_foreign=True,
                )
            self.stdout.write(
                self.style.SUCCESS(f"  ✅  {out_path.name} — {_human_size(out_path)}")
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"  ❌  Failed to dump Wagtail pages: {exc}"))

        # 2. Reference fixture — STATIC_PAGES data as JSON for documentation
        try:
            ref_path = self.fixture_dir / "static_pages_reference.json"
            with open(ref_path, "w", encoding="utf-8") as f:
                json.dump(self.pages, f, ensure_ascii=False, indent=2)
            self.stdout.write(
                self.style.SUCCESS(f"  ✅  {ref_path.name} — {_human_size(ref_path)}")
            )
        except Exception as exc:
            self.stderr.write(
                self.style.ERROR(f"  ❌  Failed to dump reference fixture: {exc}")
            )


def _human_size(path: Path) -> str:
    """Return human-readable file size."""
    size = path.stat().st_size
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"
