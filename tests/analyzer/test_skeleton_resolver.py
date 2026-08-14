"""Tests for SkeletonResolver, fusion_page_skeleton tag, and FUSION_SKELETON."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ── SkeletonEntry ──────────────────────────────────────────────────────


class TestSkeletonEntry:
    def test_defaults(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonEntry

        e = SkeletonEntry(variant="card", component_path="blocks/card.html")
        assert e.variant == "card"
        assert e.component_path == "blocks/card.html"
        assert e.props == {}
        assert e.skeleton_config == {}
        assert e.order == 0

    def test_custom_values(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonEntry

        e = SkeletonEntry(
            variant="hero-section",
            component_path="blocks/hero.html",
            props={"key": "val"},
            order=3,
        )
        assert e.order == 3
        assert e.props == {"key": "val"}


# ── SkeletonResolver ───────────────────────────────────────────────────


class TestSkeletonResolver:
    def test_constructor_without_django(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        r = SkeletonResolver()
        assert r is not None
        # Without Django settings, defaults to disabled
        assert r._cfg["ENABLED"] is False

    def test_disabled_returns_empty_list(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        r = SkeletonResolver()
        result = r.resolve_page_skeleton("pages/home.html")
        assert result == []

    def test_component_variant_resolution(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        r = SkeletonResolver()
        # Should resolve hero → hero-section via naming convention
        variant = r.resolve_component_variant("blocks/hero.html")
        assert variant == "hero-section"

    def test_unknown_component_defaults_to_line(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        r = SkeletonResolver()
        variant = r.resolve_component_variant("blocks/mystery.html")
        assert variant == "line"

    def test_to_json_serialises_entries(self):
        from django_fusion.fragments.skeleton.resolver import (
            SkeletonEntry,
            SkeletonResolver,
        )
        r = SkeletonResolver()
        entries = [
            SkeletonEntry(variant="hero-section", component_path="blocks/hero.html", order=0),
            SkeletonEntry(variant="card", component_path="components/card.html", order=1),
        ]
        payload = r.to_json(entries)
        assert "skeletons" in payload
        assert len(payload["skeletons"]) == 2
        assert payload["skeletons"][0]["variant"] == "hero-section"
        assert payload["skeletons"][0]["order"] == 0

    def test_normalise_path_adds_html(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        assert SkeletonResolver._normalise_path("pages/home") == "pages/home.html"

    def test_normalise_path_strips_leading_slash(self):
        from django_fusion.fragments.skeleton.resolver import SkeletonResolver
        assert SkeletonResolver._normalise_path("/pages/home.html") == "pages/home.html"


# ── FUSION_SKELETON settings ───────────────────────────────────────────


class TestSkeletonOptions:
    def test_defaults(self):
        from django_fusion.config.skeleton import SkeletonOptions
        opts = SkeletonOptions()
        assert opts.enabled is False
        assert opts.first_paint_skeleton is True
        assert opts.htmx_skeleton is True
        assert opts.allowed_skeleton_variants == []
        assert opts.reduced_motion_mode == "prefers"
        assert opts.animation_duration == "1.4s"
        assert opts.skeleton_css_path is None

    def test_frozen(self):
        from django_fusion.config.skeleton import SkeletonOptions
        opts = SkeletonOptions()
        with pytest.raises(Exception):  # noqa: B017
            opts.enabled = True  # type: ignore[misc]


# ── Template tag (import check) ────────────────────────────────────────


class TestFusionSkeletonTag:
    def test_tag_importable(self):
        from django_fusion.comp.tags.fusion_skeleton import fusion_page_skeleton
        assert callable(fusion_page_skeleton)

    def test_empty_template_path_returns_empty(self):
        from django_fusion.comp.tags.fusion_skeleton import fusion_page_skeleton
        result = fusion_page_skeleton(template_path="")
        assert result == ""


# ── Skeleton package exports ───────────────────────────────────────────


class TestSkeletonPackageExports:
    def test_skeleton_entry_exported(self):
        from django_fusion.fragments.skeleton import SkeletonEntry, SkeletonResolver
        assert SkeletonEntry is not None
        assert SkeletonResolver is not None
