"""
``analyze_components_to_webpack`` — scan registered Django templates for
``{% comp %}`` usage and map each component to its corresponding SCSS / JS
entry points, then generate / update a webpack entry configuration and
asset manifest consumed by the ``FUSION_ASSETS`` pipeline.

Phase 3 of the django-fusion webpack integration plan.

Usage::

    python manage.py analyze_components_to_webpack
    python manage.py analyze_components_to_webpack --output-dir static/
    python manage.py analyze_components_to_webpack --generate-entries
    python manage.py analyze_components_to_webpack --dry-run

Output
------
1. ``components-manifest.json`` (or custom ``--output-dir``) — a JSON
   object mapping each component to its SCSS partial, JS entry, and a
   list of all templates that use it::

    {
      "components": {
        "button": {
          "name": "button",
          "module_path": "django_fusion/comp/button",
          "scss": ["django_fusion/comp/button/_button.scss"],
          "js": [],
          "templates": ["components/forms.html", "components/header.html"],
          "usage_count": 2,
          "has_webpack_entry": true
        },
        ...
      },
      "total_components": 10,
      "total_with_scss": 6,
      "total_with_js": 0,
      "templates_scanned": 23,
      "generated_at": "2026-07-28T..."
    }

2. ``entries.generated.json`` (only with ``--generate-entries``) — a list
   of webpack entry objects ready to be merged into ``webpack.config.js``::

    {
      "per-component": {
        "button": "./src/django_fusion/comp/button/_button.scss",
        "card": "./src/django_fusion/comp/card/_card.scss",
        ...
      },
      "vendor": {
        "test": "/node_modules/"
      }
    }

When ``--generate-entries`` is provided the command also writes a
``webpack.entries.js`` file that can be required from the main
``webpack.config.js``.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, final

import django_fusion as _df_mod
from django.conf import settings
from django.core.management.base import CommandParser

from django_fusion.management.commands.base import BaseCommand

# Root of the installed ``django_fusion`` package — works for both
# editable (pip install -e) and installed (pip install) setups.
_DF_ROOT = Path(_df_mod.__file__).parent
_COMP_DIR = _DF_ROOT / "comp"
_ASSETS_DIR = _DF_ROOT / "assets"

# When running as an editable submodule inside the monorepo, the
# webpack config and node_modules live at the library root (one level
# up from ``src/django_fusion/``).  For a plain pip install there is no
# webpack pipeline — the generated entries file can be skipped.
_LIB_ROOT: Path | None = _DF_ROOT.parent.parent if _DF_ROOT.parent.name == "src" else None
_WEBPACK_ENTRIES_FILE: Path | None = _LIB_ROOT / "webpack.entries.js" if _LIB_ROOT else None


@final
class Command(BaseCommand):
    help: str = (
        "Scan registered components and map them to webpack entry points "
        "for the django-fusion asset pipeline."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--output-dir",
            type=str,
            default=None,
            help=(
                "Directory where the generated manifests are saved. "
                "Defaults to the site's STATIC_ROOT or the lib's static/bundles/."
            ),
        )
        parser.add_argument(
            "--generate-entries",
            action="store_true",
            default=False,
            help=(
                "Also generate webpack.entries.js with per-component entry points. "
                "The generated file can be required from webpack.config.js."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Scan and report findings without writing any files.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]
        output_dir: str | None = options["output_dir"]
        generate_entries: bool = options["generate_entries"]

        # ── Resolve output path ──────────────────────────────────────────
        if output_dir:
            out_path = Path(output_dir)
        else:
            # Follow the same convention as generate_asset_manifest.py:
            # STATIC_ROOT / "components" / "manifest.json"
            static_root = getattr(settings, "STATIC_ROOT", None)
            if static_root:
                out_path = Path(static_root)
            else:
                out_path = _DF_ROOT / "static"
            out_path = out_path / "components"
        out_path.mkdir(parents=True, exist_ok=True)

        # ── Step 1: Discover component directories ─────────────────────
        self.log_info("Scanning component directories under %s", _COMP_DIR)
        component_dirs = self._discover_component_dirs()
        self.log_success("Found %d component directories", len(component_dirs))

        # ── Step 2: Scan for SCSS/JS assets in each component dir ──────
        components_map: dict[str, dict[str, Any]] = {}
        for comp_name in sorted(component_dirs, key=str):
            comp_dir = _COMP_DIR / comp_name
            assets = self._find_assets(comp_dir)
            has_scss = bool(assets.get("scss"))
            has_js = bool(assets.get("js"))
            components_map[comp_name] = {
                "name": comp_name,
                "module_path": f"django_fusion/comp/{comp_name}",
                "scss": sorted(assets["scss"]),
                "js": sorted(assets["js"]),
                "templates": [],
                "usage_count": 0,
                "has_webpack_entry": has_scss or has_js,
            }

        # ── Step 3: Scan actual {% comp %} usage in templates ──────────
        self.log_info("Scanning templates for {% comp %} usage…")
        try:
            from django_fusion.comp.loader.templates import (
                gather_block_tag_template_usage,
            )
            for template_path, comp_names in gather_block_tag_template_usage():
                for cname in comp_names:
                    base_name = cname.replace(".", "/").split("/")[0]
                    if base_name in components_map:
                        components_map[base_name]["templates"].append(
                            str(template_path)
                        )
                        components_map[base_name]["usage_count"] += 1
        except ImportError as exc:
            self.log_warning(
                "Could not import gather_block_tag_template_usage: %s. "
                "Template scanning skipped.",
                exc,
            )
        except Exception as exc:
            self.log_warning(
                "Error during template scanning: %s. Continuing with partial results.",
                exc,
            )

        # ── Step 4: Count also component SCSS partials from assets dir ─
        # (for components that have SCSS but aren't in a dedicated comp/ dir)
        scss_partials = sorted(_ASSETS_DIR.rglob("_*.scss"))

        # ── Step 5: Build the manifest ───────────────────────────────────
        total_scanned = sum(
            len(c["templates"]) for c in components_map.values()
        )
        manifest = {
            "components": components_map,
            "total_components": len(components_map),
            "total_with_scss": sum(
                1 for c in components_map.values() if c["scss"]
            ),
            "total_with_js": sum(
                1 for c in components_map.values() if c["js"]
            ),
            "total_scss_partials_in_assets": len(scss_partials),
            "templates_scanned": total_scanned,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

        # ── Step 6: Report ──────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write("═" * 50)
        self.stdout.write("  Component → Webpack Analysis")
        self.stdout.write("═" * 50)
        self.stdout.write(f"  Total components found:    {manifest['total_components']}")
        self.stdout.write(f"  With SCSS partial:         {manifest['total_with_scss']}")
        self.stdout.write(f"  With JS entry:             {manifest['total_with_js']}")
        self.stdout.write(f"  SCSS partials (assets/):   {manifest['total_scss_partials_in_assets']}")
        self.stdout.write(f"  Templates scanned:         {manifest['templates_scanned']}")
        for comp_name, info in components_map.items():
            scss_mark = "✅" if info["scss"] else "⬜"
            js_mark = "✅" if info["js"] else "⬜"
            usage = info["usage_count"]
            self.stdout.write(
                f"    {scss_mark} CSS {js_mark} JS  "
                f"{comp_name:15s}  ({usage} template{'s' if usage != 1 else ''})"
            )
        self.stdout.write("═" * 50)
        self.stdout.write("")

        # ── Step 7: Write files ─────────────────────────────────────────
        if dry_run:
            self.log_info("DRY RUN — no files written.")
            return

        # Write components-manifest.json
        manifest_path = out_path / "components-manifest.json"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, default=str)
        manifest_kb = manifest_path.stat().st_size / 1024
        self.log_success(
            "Components manifest written → %s (%.1f KB)",
            manifest_path,
            manifest_kb,
        )

        # Optionally generate webpack.entries.js
        if generate_entries:
            entries_path = self._generate_webpack_entries(components_map, dry_run=dry_run)
            if entries_path:
                self.log_success(
                    "Webpack entries generated → %s", entries_path
                )

        # ── Summary ──────────────────────────────────────────────────────
        if manifest["total_with_scss"] == 0 and not dry_run:
            self.log_warning(
                "No component SCSS partials found. "
                "Run the build and verify: make build"
            )

        self.log_success("Analysis complete.")

    # ── Helper methods ──────────────────────────────────────────────────

    def _discover_component_dirs(self) -> list[str]:
        """Discover component directories under ``django_fusion/comp/``.

        Returns a list of component names (directory basenames) that
        contain SCSS or template files.
        """
        dirs: list[str] = []
        if not _COMP_DIR.is_dir():
            return dirs
        for entry in sorted(_COMP_DIR.iterdir()):
            if not entry.is_dir():
                continue
            name = entry.name
            # Skip private / config directories
            if name.startswith("_") or name in (
                "configuration", "fragment", "templatetags",
            ):
                continue
            dirs.append(name)
        return dirs

    def _find_assets(self, comp_dir: Path) -> dict[str, list[str]]:
        """Find SCSS and JS files within a component directory.

        Returns
        -------
        dict
            ``{"scss": [...], "js": [...]}`` with relative paths from
            the django-fusion library root.
        """
        scss_files: list[str] = []
        js_files: list[str] = []

        if not comp_dir.is_dir():
            return {"scss": scss_files, "js": js_files}

        # SCSS partials — look for _<name>.scss or <name>.scss
        for f in comp_dir.iterdir():
            if f.suffix == ".scss" and (f.name.startswith("_") or f.name == f"{comp_dir.name}.scss"):
                rel = f.relative_to(_FUSION_LIB_ROOT / "src")
                scss_files.append(str(rel))

        # JS files
        for f in comp_dir.iterdir():
            if f.suffix in (".js", ".jsx", ".ts", ".tsx"):
                rel = f.relative_to(_FUSION_LIB_ROOT / "src")
                js_files.append(str(rel))

        return {"scss": scss_files, "js": js_files}

    def _generate_webpack_entries(
        self,
        components_map: dict[str, dict[str, Any]],
        dry_run: bool = False,
    ) -> Path | None:
        """Generate ``webpack.entries.js`` with per-component entry points.

        The generated file exports an object that can be merged into the
        ``entry`` field of ``webpack.config.js``.
        """
        per_component: dict[str, str] = {}
        vendor: dict[str, str] = {}

        for comp_name, info in components_map.items():
            if not info["has_webpack_entry"]:
                continue
            # Use the first SCSS file as the entry point for this component
            if info["scss"]:
                src_path = info["scss"][0]
                if src_path.startswith("django_fusion/"):
                    src_path = "./src/" + src_path
                per_component[comp_name] = src_path

        if not per_component:
            self.log_info("No components with webpack entries to generate.")
            return None

        # Build the JS content
        lines = [
            "// ============================================================================",
            "// Auto-generated by ``analyze_components_to_webpack``",
            f"// Generated at: {datetime.now(timezone.utc).isoformat()}",
            "// ============================================================================",
            "// Merge this into webpack.config.js:",
            "//   const generatedEntries = require('./webpack.entries');",
            "//   module.exports = {",
            "//     entry: {",
            "//       fusion: '...',  // main bundle",
            "//       ...generatedEntries['per-component'],",
            "//     },",
            "//   };",
            "// ============================================================================",
            "",
            "module.exports = {",
            "  'per-component': {",
        ]
        for name, src in sorted(per_component.items()):
            lines.append(f"    '{name}': '{src}',")
        lines.append("  },")
        lines.append("};")
        lines.append("")

        if not dry_run:
            entries_path = _WEBPACK_ENTRIES_FILE
            entries_path.write_text("\n".join(lines), encoding="utf-8")
            return entries_path

        return _WEBPACK_ENTRIES_FILE
