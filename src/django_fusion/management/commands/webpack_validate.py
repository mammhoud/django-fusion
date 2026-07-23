"""
Validate (and optionally rebuild) the webpack ``bundles.json`` for the
current site.

Replaces the inline ``webpack-validate`` block in each site's Makefile.
Reads ``STATS_FILE`` from ``settings.WEBPACK_LOADER['DEFAULT']`` so it
automatically picks up the per-site path configured in
``configs/base/assets.py`` — no hard-coded ``$(SITE_NAME)`` in the
command.

Usage:
    python manage.py webpack_validate            # validate only
    python manage.py webpack_validate --rebuild # validate; rebuild on miss/invalid
    python manage.py webpack_validate --strict  # exit non-zero on any failure
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import CommandError

from django_fusion.management.commands.base import BaseCommand


class Command(BaseCommand):
    help = "Validate the webpack bundles.json for the current site."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help="If the bundle is missing or invalid, run `make assets-setup` to rebuild.",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with non-zero status on any failure (CI-friendly).",
        )

    def handle(self, *args, **options) -> None:
        stats_file = self._get_stats_file()
        if stats_file is None:
            msg = (
                "WEBPACK_LOADER['DEFAULT']['STATS_FILE'] is not configured. "
                "Set it in settings or via configs/base/assets.py."
            )
            self.stdout.write(self.style.ERROR(f"✗ {msg}"))
            if options["strict"]:
                raise CommandError(msg)
            return

        stats_path = Path(stats_file)
        if not stats_path.exists():
            self.stdout.write(self.style.WARNING(f"⚠ {stats_file} not found."))
            if options["rebuild"]:
                self._rebuild()
            elif options["strict"]:
                raise CommandError(f"bundles.json missing at {stats_file}")
            return

        try:
            with stats_path.open(encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            self.stdout.write(self.style.WARNING(f"⚠ bundles.json is invalid: {exc}"))
            if options["rebuild"]:
                self._rebuild()
            elif options["strict"]:
                raise CommandError(f"bundles.json invalid: {exc}")
            return

        chunks = (payload or {}).get("chunks") or {}
        bundle_count = len(chunks)
        chunk_count = sum(len(c) for c in chunks.values() if isinstance(c, list))
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Webpack bundles valid — {bundle_count} bundles, {chunk_count} chunks at {stats_file}"
            )
        )

    def _get_stats_file(self) -> str | None:
        webpack_cfg = getattr(settings, "WEBPACK_LOADER", {}) or {}
        default = webpack_cfg.get("DEFAULT") or {}
        return default.get("STATS_FILE") or os.environ.get("WEBPACK_STATS_FILE")

    def _rebuild(self) -> None:
        self.stdout.write(self.style.NOTICE("→ Running `make assets-setup` to rebuild…"))
        try:
            subprocess.run(["make", "assets-setup"], check=True, cwd=os.getcwd())
        except subprocess.CalledProcessError as exc:
            raise CommandError(f"`make assets-setup` failed with exit code {exc.returncode}") from exc
        except FileNotFoundError as exc:
            raise CommandError(
                "`make` not found on PATH. Install GNU make or run the npm build manually."
            ) from exc
