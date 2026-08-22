"""Contract tests for the Formint shared asset registry.

These tests intentionally use only the Python standard library. Asset wiring is
configuration and filesystem behavior, so it should be verifiable without
installing an edition's frontend, Django, or Rust dependencies.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


FORMINT_ROOT = Path(__file__).resolve().parents[1]
SHARED_ROOT = FORMINT_ROOT / "assets" / "shared"


class SharedAssetRegistryTests(unittest.TestCase):
    """Protect ownership, existence, and relative-path invariants."""

    def test_canonical_shared_assets_exist(self) -> None:
        required_files = (
            "public/Logo.svg",
            "public/Logo.png",
            "public/bg-texture.svg",
            "images/formint-crest.svg",
            "images/CompanyLogo.png",
            "static/pos-crest.svg",
            "fonts/outfit/Outfit-400.woff2",
            "fonts/outfit/Outfit-500.woff2",
            "fonts/outfit/Outfit-600.woff2",
            "fonts/outfit/Outfit-700.woff2",
            "icons/icon.ico",
            "icons/icon.icns",
            "icons/remix/remixicon.woff2",
            "styles/fonts/outfit.css",
            "styles/fonts/roboto.css",
            "styles/fonts/remixicon.css",
        )

        missing = [path for path in required_files if not (SHARED_ROOT / path).is_file()]
        self.assertEqual([], missing, f"Missing canonical shared assets: {missing}")

    def test_shared_css_relative_urls_resolve(self) -> None:
        """Every local URL in shared font declarations must point to a file."""
        url_pattern = re.compile(r"url\(\s*['\"]?([^'\")]+)")
        css_files = sorted((SHARED_ROOT / "styles").rglob("*.css"))
        self.assertTrue(css_files, "No shared CSS declarations were found")

        missing: list[str] = []
        for css_file in css_files:
            for raw_url in url_pattern.findall(css_file.read_text(encoding="utf-8")):
                if raw_url.startswith(("data:", "http://", "https://", "//", "#")):
                    continue
                relative_url = raw_url.split("?", 1)[0]
                target = (css_file.parent / relative_url).resolve()
                if not target.is_file():
                    missing.append(f"{css_file.relative_to(FORMINT_ROOT)} -> {raw_url}")

        self.assertEqual([], missing, f"Broken shared CSS asset URLs: {missing}")

    def test_asset_registry_declares_the_canonical_roots(self) -> None:
        registry = (FORMINT_ROOT / "configs" / "assets.yml").read_text(encoding="utf-8")
        expected_fragments = (
            "root: assets",
            "shared_root: assets/shared",
            "public_dir: assets/shared/public",
            "source_alias: '@formints-assets'",
            "static_source: assets/shared/static",
            "community:",
            "standard:",
            "cloud:",
            "pro:",
            "client:",
        )

        for fragment in expected_fragments:
            self.assertIn(fragment, registry)

    def test_edition_frontend_configs_resolve_to_shared_root(self) -> None:
        configs = {
            "community": (FORMINT_ROOT / "formint-community/astro.config.mjs", "../assets/shared"),
            "standard": (FORMINT_ROOT / "formint-standard/astro.config.mjs", "../assets/shared"),
            "cloud": (
                FORMINT_ROOT / "formint-cloud/frontend/astro.config.mjs",
                "../../assets/shared",
            ),
            "pro": (
                FORMINT_ROOT / "formint-pro/frontend/astro.config.mjs",
                "../../assets/shared",
            ),
            "client": (FORMINT_ROOT / "formint-client/vite.config.ts", "../assets/shared"),
        }

        for edition, (config_path, relative_root) in configs.items():
            with self.subTest(edition=edition):
                source = config_path.read_text(encoding="utf-8")
                expected_root = (config_path.parent / relative_root).resolve()
                self.assertEqual(SHARED_ROOT.resolve(), expected_root)
                self.assertRegex(
                    source,
                    rf"new URL\(\s*['\"]{re.escape(relative_root)}['\"]",
                    f"{edition} does not resolve its shared asset root",
                )
                self.assertRegex(source, r"['\"]@formints-assets['\"]\s*:\s*SHARED_ASSETS")
                self.assertIn("fs: { allow: [SHARED_ASSETS] }", source)

                if edition in {"community", "standard", "cloud"}:
                    self.assertRegex(
                        source,
                        rf"publicDir:\s*fileURLToPath\(new URL\(\s*['\"]{re.escape(relative_root)}/public['\"]",
                    )

    def test_frontend_typescript_aliases_resolve_to_shared_root(self) -> None:
        configs = {
            "community": (FORMINT_ROOT / "formint-community/tsconfig.json", "../assets/shared"),
            "standard": (FORMINT_ROOT / "formint-standard/tsconfig.json", "../assets/shared"),
            "cloud": (
                FORMINT_ROOT / "formint-cloud/frontend/tsconfig.json",
                "../../assets/shared",
            ),
            "pro": (
                FORMINT_ROOT / "formint-pro/frontend/tsconfig.json",
                "../../assets/shared",
            ),
            "client": (
                FORMINT_ROOT / "formint-client/frontend/tsconfig.json",
                "../../assets/shared",
            ),
        }

        for edition, (config_path, relative_root) in configs.items():
            with self.subTest(edition=edition):
                source = config_path.read_text(encoding="utf-8")
                self.assertEqual(SHARED_ROOT.resolve(), (config_path.parent / relative_root).resolve())
                self.assertIn(
                    f'"@formints-assets/*": ["{relative_root}/*"]',
                    source,
                    f"{edition} TypeScript alias is not canonical",
                )

    def test_django_settings_use_shared_static_source_and_isolated_output(self) -> None:
        settings_files = (
            FORMINT_ROOT / "formint-pro/server/configs/__init__.py",
            FORMINT_ROOT / "formint-cloud/backend/configs/__init__.py",
            FORMINT_ROOT / "formint-client/backend/settings.py",
        )

        for settings_path in settings_files:
            with self.subTest(settings=str(settings_path.relative_to(FORMINT_ROOT))):
                source = settings_path.read_text(encoding="utf-8")
                self.assertIn("FORMINT_SHARED_ASSETS = Path(", source)
                self.assertIn('"FORMINT_SHARED_ASSETS"', source)
                self.assertIn(
                    'STATICFILES_DIRS = [str(FORMINT_SHARED_ASSETS / "static")]',
                    source,
                )
                self.assertIn('STATIC_ROOT = BASE_DIR / "staticfiles"', source)

    def test_tauri_asset_references_resolve(self) -> None:
        config_paths = (
            FORMINT_ROOT / "formint-community/src-tauri/tauri.conf.json",
            FORMINT_ROOT / "formint-standard/src-tauri/tauri.conf.json",
            FORMINT_ROOT / "formint-client/src-tauri/tauri.conf.json",
        )

        for config_path in config_paths:
            with self.subTest(config=str(config_path.relative_to(FORMINT_ROOT))):
                config = json.loads(config_path.read_text(encoding="utf-8"))
                bundle = config["bundle"]
                references = list(bundle.get("icon", []))
                installer_icon = bundle.get("windows", {}).get("nsis", {}).get("installerIcon")
                if installer_icon:
                    references.append(installer_icon)

                missing = [
                    reference
                    for reference in references
                    if not (config_path.parent / reference).resolve().is_file()
                ]
                self.assertEqual([], missing, f"Broken Tauri asset paths: {missing}")

    def test_standard_tray_icon_uses_canonical_shared_asset(self) -> None:
        source = (FORMINT_ROOT / "formint-standard/src-tauri/src/lib.rs").read_text(
            encoding="utf-8"
        )
        self.assertIn('include_bytes!("../../../assets/shared/public/Logo.png")', source)
        self.assertNotIn("formint-standard/assets/icons", source)

    def test_duplicate_edition_asset_roots_are_absent(self) -> None:
        forbidden_directories = (
            "formint-community/assets/images",
            "formint-community/assets/fonts",
            "formint-standard/assets/images",
            "formint-standard/assets/fonts",
            "formint-cloud/frontend/assets/images",
            "formint-cloud/frontend/assets/fonts",
            "formint-pro/frontend/src/assets/fonts",
        )
        present = [path for path in forbidden_directories if (FORMINT_ROOT / path).exists()]
        self.assertEqual([], present, f"Duplicate asset roots remain: {present}")


if __name__ == "__main__":
    unittest.main()
