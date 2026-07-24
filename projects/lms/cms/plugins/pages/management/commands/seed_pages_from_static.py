"""
Data migration command to seed Wagtail CMS pages from STATIC_PAGES.

Run once to migrate hardcoded page content from
``plugins.pages.content.STATIC_PAGES`` into live Wagtail Page objects.

Usage::

    python manage.py seed_pages_from_static  [--dry-run]  [--force]
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page, Locale


class Command(BaseCommand):
    help = "Seed Wagtail Page objects from STATIC_PAGES content."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would be created without saving.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing pages with the same slug.",
        )
        parser.add_argument(
            "--lang",
            default=None,
            help="Seed only a specific language code (e.g., 'fr').",
        )

    def handle(self, *args, **options):
        from plugins.pages.content import STATIC_PAGES, STATIC_PAGE_TRANSLATIONS
        from www.content.models.pages import (
            HomePage,
            AboutPage,
            FaqPage,
            PrivacyPage,
            ContactPage,
        )

        dry_run = options["dry_run"]
        force = options["force"]
        lang_filter = options.get("lang")

        # Map slugs to Page model classes
        PAGE_MODELS = {
            "home": HomePage,
            "about-us": AboutPage,
            "faq": FaqPage,
            "privacy": PrivacyPage,
            "contact": ContactPage,
        }

        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stderr.write("No root Wagtail page found. Run migrations first.")
            return

        created = 0
        skipped = 0

        # ── Seed English (base) pages ──
        if lang_filter is None or lang_filter == "en":
            for slug, data in STATIC_PAGES.items():
                page_model = PAGE_MODELS.get(slug)
                if page_model is None:
                    self.stdout.write(f"  Skipping unknown slug: {slug}")
                    skipped += 1
                    continue

                existing = Page.objects.filter(slug=slug, depth__gt=1).first()
                if existing and not force:
                    self.stdout.write(f"  Exists: {slug} (pk={existing.pk}) — skipping")
                    skipped += 1
                    continue
                elif existing and force:
                    existing.delete()
                    self.stdout.write(f"  Deleted existing: {slug}")

                if dry_run:
                    self.stdout.write(f"  [DRY-RUN] Would create {page_model.__name__}(slug='{slug}')")
                    created += 1
                    continue

                page = page_model(
                    title=data["title"],
                    slug=slug,
                    seo_title=data.get("seo", {}).get("title", data["title"]),
                    seo_description=data.get("seo", {}).get("description", ""),
                )
                root.add_child(instance=page)

                # Populate StreamField blocks
                blocks = data.get("blocks", [])
                if blocks:
                    page.body = [
                        (b["type"], b)
                        for b in blocks
                        if b["type"] in dict(page.body.stream_block.child_blocks)
                    ]
                    page.save()

                self.stdout.write(
                    self.style.SUCCESS(f"  Created {page_model.__name__}(slug='{slug}', pk={page.pk})")
                )
                created += 1

        # ── Seed translations ──
        if lang_filter is None:
            for lang_code, lang_pages in STATIC_PAGE_TRANSLATIONS.items():
                if lang_code == "en":
                    continue
                locale = Locale.objects.filter(language_code=lang_code).first()
                if locale is None:
                    self.stdout.write(f"  Locale '{lang_code}' not found — skipping translations for this language")
                    continue

                for slug, data in lang_pages.items():
                    english_page = Page.objects.filter(slug=slug, depth__gt=1).first()
                    if english_page is None:
                        self.stdout.write(f"  No English page with slug='{slug}' — skipping {lang_code} translation")
                        continue

                    existing = english_page.get_translation(locale)
                    if existing and not force:
                        self.stdout.write(f"  Translation exists: {slug} ({lang_code}) — skipping")
                        skipped += 1
                        continue

                    if dry_run:
                        self.stdout.write(f"  [DRY-RUN] Would create translation for '{slug}' in {lang_code}")
                        created += 1
                        continue

                    translated = english_page.copy_for_translation(locale)
                    translated.title = data.get("title", translated.title)
                    translated.seo_title = data.get("seo", {}).get("title", translated.title)
                    translated.seo_description = data.get("seo", {}).get("description", "")
                    translated.save()

                    blocks = data.get("blocks", [])
                    if blocks:
                        translated.body = [
                            (b["type"], b)
                            for b in blocks
                            if b["type"] in dict(translated.body.stream_block.child_blocks)
                        ]
                        translated.save()

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  Created translation: {slug} ({lang_code}, pk={translated.pk})"
                        )
                    )
                    created += 1

        self.stdout.write(self.style.SUCCESS(f"\nDone: {created} created, {skipped} skipped."))
