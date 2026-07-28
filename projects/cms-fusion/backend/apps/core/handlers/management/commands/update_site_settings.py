"""
update_site_settings management command
=========================================
Update GlobalSettings with logo image and social link data.

Ports logic from base-dir ``update_footer_settings.py``.

Usage:
    uv run python manage.py update_site_settings --logo-path /path/to/logo.png
    uv run python manage.py update_site_settings --logo-path /path/to/logo.png \\
        --social-json '[{"platform":"facebook","username":"ctcresearch",...}]'
    uv run python manage.py update_site_settings --logo-path /path/to/logo.png \\
        --social-json /path/to/social_links.json
"""

import json
import sys
from pathlib import Path
from typing import Any

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django_fusion.site.management.commands.base import BaseCommand


class Command(BaseCommand):
    help = "Update GlobalSettings with logo image and social link data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--logo-path",
            required=True,
            help="Path to logo image file",
        )
        parser.add_argument(
            "--social-json",
            default=None,
            help="JSON string or file path for social links (list of dicts with platform, username, profile_url, etc.)",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        from wagtail.images.models import Image

        from apps.core.domain.models.settings.settings import GlobalSettings

        logo_path = Path(options["logo_path"])
        social_json: str | None = options["social_json"]

        # ------------------------------------------------------------------
        # Resolve GlobalSettings
        # ------------------------------------------------------------------
        gs = GlobalSettings.objects.first()
        if not gs:
            raise CommandError(
                "GlobalSettings not found. "
                "Ensure the site is initialised before running this command."
            )

        errors: list[str] = []

        # ------------------------------------------------------------------
        # Logo
        # ------------------------------------------------------------------
        if not logo_path.exists():
            msg = f"Logo file not found: {logo_path}"
            self.stderr.write(self.style.WARNING(f"⚠️  {msg}"))
            errors.append(msg)
        else:
            try:
                with open(logo_path, "rb") as f:
                    image = Image.objects.create(
                        title="Fusion CMS Logo",
                        file=File(f, name=logo_path.name),
                    )
                gs.logo = image
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Logo uploaded and updated: {image.id}")
                )
            except Exception as exc:  # noqa: BLE001
                msg = f"Failed to upload logo: {exc}"
                self.stderr.write(self.style.ERROR(f"✗  {msg}"))
                errors.append(msg)

        # ------------------------------------------------------------------
        # Social links
        # ------------------------------------------------------------------
        if social_json is not None:
            social_data = _resolve_social_json(social_json)
            try:
                gs.social_links = [("link", d) for d in social_data]
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Social links updated ({len(social_data)} entries)."
                    )
                )
            except Exception as exc:  # noqa: BLE001
                msg = f"Failed to set social links: {exc}"
                self.stderr.write(self.style.ERROR(f"✗  {msg}"))
                errors.append(msg)

        # ------------------------------------------------------------------
        # Persist
        # ------------------------------------------------------------------
        try:
            gs.save()
            self.stdout.write(self.style.SUCCESS("✅ GlobalSettings saved."))
        except Exception as exc:  # noqa: BLE001
            msg = f"Failed to save GlobalSettings: {exc}"
            self.stderr.write(self.style.ERROR(f"✗  {msg}"))
            errors.append(msg)

        if errors:
            self.stderr.write(
                self.style.ERROR(
                    f"\n{len(errors)} error(s) occurred. Review the messages above."
                )
            )
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("\n✨ Site settings update complete."))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_social_json(value: str) -> list[dict]:
    """Parse *value* as a JSON string or a path to a JSON file.

    Returns a list of social-link dicts.
    Raises ``CommandError`` on parse failure.
    """
    # Try treating it as a file path first
    candidate = Path(value)
    if candidate.exists():
        try:
            text = candidate.read_text(encoding="utf-8")
        except OSError as exc:
            raise CommandError(f"Could not read social JSON file: {exc}") from exc
    else:
        text = value

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CommandError(
            f"Invalid JSON for --social-json: {exc}. "
            "Provide a valid JSON array or a path to a JSON file."
        ) from exc

    if not isinstance(data, list):
        raise CommandError(
            "--social-json must be a JSON array of social-link objects, "
            f"got {type(data).__name__}."
        )

    return data
