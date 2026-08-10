"""``generate_skeleton_manifest`` — build-time skeleton manifest generator.

Produces a static ``skeleton-manifest.json`` that the Astro build can
consume at compile time so every page ships with its skeleton order
pre-computed (no runtime scanner overhead).

Usage::

    python manage.py generate_skeleton_manifest \\
        --output backend/assets/static/skeleton-manifest.json \\
        --page pages/home.html \\
        --page blog/index.html \\
        --page pricing/index.html

Output shape::

    {
      "pages": {
        "pages/home.html": {
          "title": "Home",
          "skeletons": [
            {"variant": "hero-section", "component": "blocks/hero.html", "order": 0},
            {"variant": "stats-row", "component": "sections/stats.html", "order": 1}
          ]
        }
      },
      "components": {
        "blocks/hero.html": {
          "skeleton": "hero-section",
          "css": ["/static/bundles/hero.css"],
          "js": ["/static/bundles/hero.js"]
        }
      }
    }
"""

from __future__ import annotations

import json
from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from django_fusion.management.commands.base import BaseCommand


def _format_bytes(n: float) -> str:
    """Human-readable byte size."""
    if n < 1024:
        return f"{n:.0f} B"
    elif n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    else:
        return f"{n / (1024 * 1024):.1f} MB"


class Command(BaseCommand):
    help = "Generate a static skeleton manifest JSON for the Astro build."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--output",
            type=str,
            required=True,
            help="Path to write the skeleton-manifest.json file.",
        )
        parser.add_argument(
            "--page",
            action="append",
            dest="pages",
            default=[],
            help=(
                "Template path to include in the manifest. "
                "Repeat for multiple pages (e.g. --page pages/home.html --page blog/index.html)."
            ),
        )
        parser.add_argument(
            "--budget",
            type=int,
            default=None,
            help=(
                "Emit a component-level bundle budget report. "
                "Specify the per-component CSS+JS budget in bytes "
                "(e.g. --budget 50000 for 50 KB)."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        output_path = Path(options["output"])
        page_paths: list[str] = options["pages"] or []

        if not page_paths:
            self.log_warning(
                "No --page arguments provided. "
                "Use --page <template_path> to specify pages to include."
            )
            # Write an empty manifest so the build doesn't fail
            self._write_manifest(output_path, {"pages": {}, "components": {}})
            return

        self.log_info(
            f"Generating skeleton manifest for {len(page_paths)} page(s) ..."
        )

        from django_fusion.fragments.skeleton.resolver import SkeletonResolver

        resolver = SkeletonResolver()

        pages: dict[str, Any] = {}
        components: dict[str, Any] = {}

        for page_path in page_paths:
            entries = resolver.resolve_page_skeleton(page_path)

            normalised = resolver._normalise_path(page_path)
            pages[normalised] = {
                "title": Path(page_path).stem.replace("_", " ").title(),
                "skeletons": [
                    {
                        "variant": e.variant,
                        "component": e.component_path,
                        "order": e.order,
                        "props": e.props,
                        "skeleton_config": e.skeleton_config,
                    }
                    for e in entries
                ],
            }

            # Collect per-component metadata for the component→asset map
            for entry in entries:
                if entry.component_path not in components:
                    components[entry.component_path] = {
                        "skeleton": entry.variant,
                        "css": [],
                        "js": [],
                    }

            self.log_success(
                f"  {normalised}: {len(entries)} component(s)"
            )

        # ── enrich with webpack deps when available ─────────────
        try:
            from django_fusion.core.assets.component_map import ComponentAssetMap
            asset_map = ComponentAssetMap()
            for comp_path, comp_data in components.items():
                entry = asset_map.get_component_assets(comp_path)
                if entry:
                    comp_data["css"] = entry.css_deps
                    comp_data["js"] = entry.js_deps
            self.log_info("Webpack dependencies resolved for component map.")
        except Exception:
            self.log_warning(
                "Webpack stats not available — component CSS/JS arrays are empty."
            )

        # ── Budget report (Phase 6.3) ───────────────────────────
        budget_limit = options.get("budget")
        if budget_limit is not None:
            self._print_budget_report(components, budget_limit)

        manifest: dict[str, Any] = {
            "pages": pages,
            "components": components,
        }

        self._write_manifest(output_path, manifest)

        total_components = len(components)
        total_skeletons = sum(
            len(p["skeletons"]) for p in pages.values()
        )
        self.log_success(
            f"Manifest written to {output_path} "
            f"({len(pages)} pages, {total_components} components, "
            f"{total_skeletons} skeleton entries)."
        )

    def _print_budget_report(
        self,
        components: dict[str, Any],
        budget_limit: int,
    ) -> None:
        """Print a component-level bundle budget report to stdout."""
        import os

        lines: list[tuple[str, float, float, float, str]] = []

        for comp_path, comp_data in sorted(components.items()):
            css_bytes = 0.0
            js_bytes = 0.0

            for css_url in comp_data.get("css", []):
                css_bytes += self._estimate_file_size(css_url)
            for js_url in comp_data.get("js", []):
                js_bytes += self._estimate_file_size(js_url)

            total = css_bytes + js_bytes
            status = (
                "\u2705 OK"
                if total <= budget_limit
                else f"\u26a0\ufe0f  OVER ({_format_bytes(total - budget_limit)})"
            )
            lines.append((comp_path, css_bytes, js_bytes, total, status))

        if not lines:
            self.log_info("No components to report.")
            return

        self.stdout.write("")
        self.stdout.write(
            f"{'Component':<40} {'CSS':>10} {'JS':>10} {'Total':>10}   Budget    Status"
        )
        self.stdout.write("-" * 100)

        for path, css, js, total, status in lines:
            self.stdout.write(
                f"{path:<40} {_format_bytes(css):>10} {_format_bytes(js):>10} "
                f"{_format_bytes(total):>10}   {_format_bytes(budget_limit):>7}   {status}"
            )

        over = sum(1 for _, _, _, t, _ in lines if t > budget_limit)
        self.stdout.write("")
        self.log_info(
            f"Budget report: {len(lines)} components, "
            f"{over} over budget ({_format_bytes(budget_limit)})."
        )

    @staticmethod
    def _estimate_file_size(url: str) -> int:
        """Estimate the filesystem size of a generated asset.

        Tries to resolve the URL to a static file path.  Falls back
        to 0 when the file is not on disk (e.g. CDN-hosted assets).
        """
        try:
            from django.conf import settings
            static_root = getattr(settings, "STATIC_ROOT", None)
            if static_root:
                # Strip /static/ prefix and resolve
                rel = url.replace("/static/", "").lstrip("/")
                candidate = Path(static_root) / rel
                if candidate.is_file():
                    return candidate.stat().st_size
        except Exception:
            pass
        return 0

    @staticmethod
    def _write_manifest(output_path: Path, data: dict[str, Any]) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )
