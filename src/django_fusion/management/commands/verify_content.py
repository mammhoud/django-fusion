"""
verify_content management command
====================================
Generate a markdown report of all published Wagtail pages, documenting
their translated fields after population.

Usage:
    uv run python manage.py verify_content
    uv run python manage.py verify_content --output docs/added_content.md
"""

import sys
from pathlib import Path
from typing import Any

from django.core.management.base import CommandError
from django_fusion.management.commands.base import BaseCommand

# ---------------------------------------------------------------------------
# Helpers (ported from base-dir verify_content.py)
# ---------------------------------------------------------------------------

def _get_field_value(obj, field_name: str) -> str:
    """Safely retrieve a field value as a string."""
    try:
        val = getattr(obj, field_name)
        if hasattr(val, "as_list"):  # StreamField
            return str([str(b) for b in val])
        if hasattr(val, "source"):  # RichText
            return val.source
        return str(val)
    except Exception:  # noqa: BLE001
        return "N/A"


def _write_page_report(f, page) -> None:
    """Write a single page's fields to the report file."""
    from django.db import models
    from wagtail.fields import StreamField
    f.write(
        f"### Page: {page.title} "
        f"(ID: {page.id}, Type: {type(page).__name__})\n"
    )
    f.write(f"- **Slug**: {page.slug}\n")
    f.write(f"- **SEO Title**: {page.seo_title}\n")
    f.write(f"- **Search Description**: {page.search_description}\n")

    _SKIP_FIELDS = {
        "title", "slug", "seo_title", "search_description",
        "path", "depth", "numchild", "url_path",
    }

    model = type(page)
    for field in model._meta.get_fields():
        if isinstance(
            field,
            (
                models.CharField,
                models.TextField,
                models.IntegerField,
                models.BooleanField,
            ),
        ):
            if field.name in _SKIP_FIELDS:
                continue
            f.write(
                f"- **{field.verbose_name} ({field.name})**: "
                f"{_get_field_value(page, field.name)}\n"
            )

        elif isinstance(field, StreamField):
            f.write(f"- **{field.verbose_name} ({field.name})**: (StreamField)\n")
            sf_val = getattr(page, field.name)
            for block in sf_val:
                f.write(f"  - Block: {block.block_type}\n")
                if hasattr(block.value, "items"):
                    for k, v in block.value.items():
                        f.write(f"    - {k}: {str(v)[:100]}...\n")
                else:
                    f.write(f"    - Value: {str(block.value)[:100]}...\n")

    f.write("\n---\n\n")


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = "Generate a markdown report of all published Wagtail pages"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--output",
            default="docs/added_content.md",
            help="Output file path (default: docs/added_content.md)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        output_path = Path(options["output"])

        self.stdout.write(
            self.style.MIGRATE_HEADING("\n📝 Generating Added Content Report...\n")
        )

        # Ensure parent directory exists
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise CommandError(
                f"Could not create output directory '{output_path.parent}': {exc}"
            ) from exc

        from wagtail.models import Locale, Page

        locales = Locale.objects.all()
        if not locales.exists():
            raise CommandError(
                "No locales found in the database. "
                "Ensure the site is initialised before running this command."
            )

        errors: list[str] = []

        try:
            with output_path.open("w", encoding="utf-8") as f:
                f.write("# Added Content Verification Report\n\n")
                f.write(
                    "This report documents all pages and their translated fields "
                    "after population.\n\n"
                )

                for locale in locales:
                    f.write(f"## LOCALE: {locale.language_code}\n\n")
                    pages = Page.objects.filter(locale=locale).specific()

                    page_count = 0
                    for page in pages:
                        if page.depth <= 2:
                            # Skip root and home-redirect stubs
                            continue
                        try:
                            _write_page_report(f, page)
                            page_count += 1
                        except Exception as exc:  # noqa: BLE001
                            msg = (
                                f"Failed to write report for page "
                                f"'{page.title}' (ID: {page.id}): {exc}"
                            )
                            self.stderr.write(self.style.ERROR(f"  ✗  {msg}"))
                            errors.append(msg)

                    self.stdout.write(
                        f"  📄 Locale '{locale.language_code}': {page_count} page(s) documented."
                    )

        except OSError as exc:
            raise CommandError(
                f"Could not write report to '{output_path}': {exc}"
            ) from exc

        if errors:
            self.stderr.write(
                self.style.ERROR(
                    f"\n{len(errors)} error(s) occurred while generating the report. "
                    "Review the messages above."
                )
            )
            sys.exit(1)

        self.stdout.write(
            self.style.SUCCESS(f"\n✨ Report generated at {output_path}")
        )
