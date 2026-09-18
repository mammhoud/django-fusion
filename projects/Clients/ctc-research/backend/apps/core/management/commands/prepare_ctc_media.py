"""Prepare the CTC Research archive media pack for website use.

The command is intentionally separate from ``load_data``: it copies files and
writes a manifest, but never touches the database or loads a fixture.

Usage::

    python manage.py prepare_ctc_media --dry-run
    python manage.py prepare_ctc_media
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError
from django.utils.text import slugify
from django_fusion.management.commands.base import BaseCommand


ALLOWED_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".mp4", ".png", ".svg", ".webp"}
EXCLUDED_NAMES = {"appmap.log"}


class Command(BaseCommand):
    help = "Copy the CTC archive media pack into the shared website media tree."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Report planned copies without writing files.")
        parser.add_argument("--overwrite", action="store_true", help="Replace files already present in the destination.")
        parser.add_argument("--source", type=Path, help="Override the archive source directory.")

    @staticmethod
    def _manifest_path() -> Path:
        configured = getattr(settings, "CTC_MEDIA_MANIFEST_PATH", None)
        return Path(configured) if configured else Path(settings.BASE_DIR) / "assets" / "fixtures" / "ctc-research-media.json"

    @staticmethod
    def _safe_output_name(source: Path) -> str:
        stem = slugify(source.stem) or "asset"
        return f"{stem}{source.suffix.lower()}"

    def handle(self, **options):
        manifest_path = self._manifest_path()
        if not manifest_path.exists():
            raise CommandError(f"CTC media manifest not found: {manifest_path}")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        default_source = Path(getattr(settings, "CTC_MEDIA_SOURCE_DIR", Path(settings.MEDIA_ROOT) / "media"))
        source_dir = (options.get("source") or default_source).resolve()
        content_dir = Path(
            getattr(settings, "CTC_MEDIA_CONTENT_DIR", Path(settings.MEDIA_ROOT) / "ctc-content")
        ).resolve()
        dump_dir = Path(
            getattr(settings, "CTC_MEDIA_DUMP_IMAGE_DIR", Path(settings.MEDIA_ROOT) / "original_images")
        ).resolve()
        dry_run = options["dry_run"]
        overwrite = options["overwrite"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n📦 prepare_ctc_media — CTC archive media\n"))
        self.stdout.write(f"  Source: {source_dir}")
        self.stdout.write(f"  Website copy: {content_dir}")
        self.stdout.write(f"  Dump-compatible image aliases: {dump_dir}")
        self.stdout.write(f"  Dry-run: {'✅' if dry_run else '❌'}")

        if not source_dir.is_dir():
            raise CommandError(f"Archive source directory does not exist: {source_dir}")

        planned: list[tuple[Path, Path]] = []
        for source in sorted(source_dir.iterdir(), key=lambda item: item.name.lower()):
            if not source.is_file() or source.name in EXCLUDED_NAMES or source.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            planned.append((source, content_dir / self._safe_output_name(source)))

        aliases = manifest.get("dump_aliases", {})
        for dump_name, source_name in aliases.items():
            source = source_dir / source_name
            if source.is_file():
                planned.append((source, dump_dir / Path(dump_name).name))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠ missing dump source: {source_name}"))

        if not dry_run:
            content_dir.mkdir(parents=True, exist_ok=True)
            dump_dir.mkdir(parents=True, exist_ok=True)
            for source, destination in planned:
                if destination.exists() and not overwrite:
                    continue
                shutil.copy2(source, destination)

            runtime_manifest = {
                **manifest,
                "prepared_from": str(source_dir),
                "website_copy_dir": str(content_dir),
                "dump_image_dir": str(dump_dir),
                "prepared_files": [destination.name for _, destination in planned],
            }
            (content_dir / "manifest.json").write_text(
                json.dumps(runtime_manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        self.stdout.write(self.style.SUCCESS(f"\n✅ Planned {len(planned)} file operations."))
        if dry_run:
            self.stdout.write(self.style.WARNING("No files were changed. Run without --dry-run to prepare the media pack."))
        else:
            self.stdout.write(self.style.SUCCESS("Website assets and dump-compatible aliases are ready."))
            self.stdout.write("Database fixtures were not loaded.")
