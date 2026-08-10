"""Tests for ComponentAssetMap, component asset APIs, and template tag."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ── helpers ────────────────────────────────────────────────────────────


def _write_bundles_json(path: Path, chunks: dict):
    """Write a minimal webpack-bundle-tracker stats file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "status": "done",
        "chunks": chunks,
    }))


# ── ComponentAssetEntry ────────────────────────────────────────────────


class TestComponentAssetEntry:
    def test_defaults(self):
        from django_fusion.core.assets.component_map import ComponentAssetEntry

        e = ComponentAssetEntry(component_path="blocks/hero.html")
        assert e.component_path == "blocks/hero.html"
        assert e.css_deps == []
        assert e.js_deps == []
        assert e.vendor_deps == []
        assert e.size_bytes == 0
        assert e.preload is False

    def test_to_dict(self):
        from django_fusion.core.assets.component_map import ComponentAssetEntry

        e = ComponentAssetEntry(
            component_path="blocks/hero.html",
            css_deps=["/static/bundles/hero.css"],
            js_deps=["/static/bundles/hero.js"],
            preload=True,
        )
        d = e.to_dict()
        assert d["component"] == "blocks/hero.html"
        assert d["css"] == ["/static/bundles/hero.css"]
        assert d["js"] == ["/static/bundles/hero.js"]
        assert d["preload"] is True


# ── ComponentAssetMap ──────────────────────────────────────────────────


class TestComponentAssetMap:
    def test_empty_when_no_stats(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        asset_map = ComponentAssetMap(stats_path="/nonexistent/bundles.json")
        assert asset_map.get_component_assets("blocks/hero.html") is None
        assert asset_map.get_all_components() == {}

    def test_no_stats_defaults_to_empty(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        asset_map = ComponentAssetMap()
        # May or may not find stats — should not crash
        result = asset_map.get_all_components()
        assert isinstance(result, dict)

    def test_with_mock_bundles(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "status": "done",
                "chunks": {
                    "main": [{"name": "main.js", "url": "/static/bundles/main.js"}],
                    "blocks_hero": [
                        {"name": "hero.css", "url": "/static/bundles/hero.css"},
                        {"name": "hero.js", "url": "/static/bundles/hero.js"},
                    ],
                    "blocks_stats": [
                        {"name": "stats.js", "url": "/static/bundles/stats.js"},
                    ],
                },
            }, f)
            stats_path = f.name

        asset_map = ComponentAssetMap(stats_path=stats_path)

        # Hero component
        entry = asset_map.get_component_assets("blocks/hero.html")
        assert entry is not None
        assert "/static/bundles/hero.css" in entry.css_deps
        assert "/static/bundles/hero.js" in entry.js_deps
        assert entry.preload is True  # "hero" keyword

        # Stats component
        entry2 = asset_map.get_component_assets("blocks/stats.html")
        assert entry2 is not None
        assert "/static/bundles/stats.js" in entry2.js_deps
        assert entry2.preload is False  # not a critical keyword

        # Missing component
        assert asset_map.get_component_assets("blocks/footer.html") is None

        import os
        os.unlink(stats_path)

    def test_get_page_assets(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "status": "done",
                "chunks": {
                    "blocks_hero": [
                        {"name": "hero.css", "url": "/static/bundles/hero.css"},
                        {"name": "hero.js", "url": "/static/bundles/hero.js"},
                    ],
                    "components_card": [
                        {"name": "card.js", "url": "/static/bundles/card.js"},
                    ],
                },
            }, f)
            stats_path = f.name

        asset_map = ComponentAssetMap(stats_path=stats_path)
        page_assets = asset_map.get_page_assets(
            ["blocks/hero.html", "components/card.html"]
        )
        assert "css" in page_assets
        assert "js" in page_assets
        assert "/static/bundles/hero.css" in page_assets["css"]
        assert "/static/bundles/hero.js" in page_assets["js"]
        assert "/static/bundles/card.js" in page_assets["js"]

        import os
        os.unlink(stats_path)

    def test_to_manifest(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "status": "done",
                "chunks": {
                    "blocks_hero": [
                        {"name": "hero.js", "url": "/static/bundles/hero.js"},
                    ],
                },
            }, f)
            stats_path = f.name

        asset_map = ComponentAssetMap(stats_path=stats_path)
        manifest = asset_map.to_manifest()
        assert "components" in manifest
        assert "blocks/hero.html" in manifest["components"]

        import os
        os.unlink(stats_path)

    def test_legacy_assets_format(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "status": "done",
                "assets": {
                    "blocks_hero": [{"name": "hero.js", "url": "/static/hero.js"}],
                },
            }, f)
            stats_path = f.name

        asset_map = ComponentAssetMap(stats_path=stats_path)
        entry = asset_map.get_component_assets("blocks/hero.html")
        assert entry is not None
        assert "/static/hero.js" in entry.js_deps

        import os
        os.unlink(stats_path)

    def test_main_bundle_excluded(self):
        from django_fusion.core.assets.component_map import ComponentAssetMap

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({
                "status": "done",
                "chunks": {
                    "main": [{"name": "main.js", "url": "/static/main.js"}],
                    "vendor": [{"name": "vendor.js", "url": "/static/vendor.js"}],
                },
            }, f)
            stats_path = f.name

        asset_map = ComponentAssetMap(stats_path=stats_path)
        assert asset_map.get_component_assets("main/main.html") is None
        assert asset_map.get_component_assets("vendor/vendor.html") is None

        import os
        os.unlink(stats_path)


# ── Settings helper ────────────────────────────────────────────────────


class TestComponentAssetSettings:
    def test_defaults_disabled(self):
        from django_fusion.config.assets import get_component_asset_options

        opts = get_component_asset_options()
        assert opts["ENABLED"] is False
        assert opts["PRELOAD_CRITICAL"] is True
        assert opts["LAZY_LOAD_BELOW_FOLD"] is True
        assert opts["CHUNK_SIZE_WARNING"] == 100 * 1024
        assert opts["BUNDLES_JSON_PATH"] is None


# ── Template tag ───────────────────────────────────────────────────────


class TestComponentAssetsTag:
    def test_disabled_returns_empty(self):
        from django_fusion.comp.tags.fusion_assets import (
            fusion_component_assets_json,
        )
        result = fusion_component_assets_json()
        # Disabled by default — returns empty string
        assert result == ""


# ── Views import check ─────────────────────────────────────────────────


class TestComponentAssetViews:
    def test_views_importable(self):
        from django_fusion.core.assets.views import (
            ComponentAssetsView,
            ComponentAssetDetailView,
            PageAssetsView,
        )
        assert ComponentAssetsView is not None
        assert ComponentAssetDetailView is not None
        assert PageAssetsView is not None
