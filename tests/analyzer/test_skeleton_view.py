"""Tests for the skeleton manifest endpoint and FUSION_ANALYZER settings."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the src tree is importable
_SRC = Path(__file__).resolve().parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


# ── AnalyzerOptions tests ──────────────────────────────────────────────


class TestAnalyzerOptionsDefaults:
    """Verify the frozen dataclass ships with safe defaults."""

    def test_all_fields_off_by_default(self):
        from django_fusion.config.analyzer import AnalyzerOptions

        opts = AnalyzerOptions()
        assert opts.enabled is False
        assert opts.skeleton_auto_detect is True
        assert opts.skeleton_default_variant == "line"
        assert opts.emit_skeleton_manifest is True
        assert opts.cache_duration == 3600
        assert opts.analyze_depth == 3
        assert opts.analyze_filters == {}

    def test_frozen(self):
        from django_fusion.config.analyzer import AnalyzerOptions

        opts = AnalyzerOptions()
        with pytest.raises(Exception):  # noqa: B017
            opts.enabled = True  # type: ignore[misc]


# ── skeleton variant resolver tests ────────────────────────────────────


class TestSkeletonVariantResolution:
    """Three-priority resolver: explicit → naming convention → default."""

    @pytest.fixture(autouse=True)
    def _imports(self):
        from django_fusion.fragments.analyzer.schemas import Component
        from django_fusion.fragments.analyzer.skeleton_view import (
            _resolve_skeleton_variant,
        )

        self.resolve = _resolve_skeleton_variant
        self.Component = Component

    # Priority 1 — explicit

    def test_explicit_skeleton_wins(self):
        c = self.Component(name="Hero", path="blocks/hero.html", skeleton="hero-section")
        assert self.resolve(c) == "hero-section"

    def test_explicit_overrides_naming_convention(self):
        c = self.Component(name="Hero", path="blocks/hero.html", skeleton="custom-banner")
        assert self.resolve(c) == "custom-banner"

    # Priority 2 — naming convention

    @pytest.mark.parametrize(
        "path,expected",
        [
            ("blocks/hero.html", "hero-section"),
            ("sections/stats.html", "stats-row"),
            ("components/features.html", "features-grid"),
            ("blocks/testimonial.html", "testimonial"),
            ("blocks/testimonials.html", "testimonials-carousel"),
            ("sections/pricing.html", "pricing-grid"),
            ("blocks/faq.html", "faq-list"),
            ("sections/cta.html", "cta-banner"),
            ("blocks/contact.html", "contact-form"),
            ("blocks/team.html", "team-grid"),
            ("blocks/blog_index.html", "blog-grid"),
            ("blocks/timeline.html", "timeline"),
        ],
    )
    def test_naming_convention_mapping(self, path, expected):
        c = self.Component(name=Path(path).stem.title(), path=path)
        assert self.resolve(c) == expected

    # Priority 3 — path-directory default

    def test_components_dir_defaults_to_card(self):
        c = self.Component(name="Widget", path="components/widget.html")
        assert self.resolve(c) == "card"

    def test_layout_dir_defaults_to_line(self):
        c = self.Component(name="Base", path="layout/base.html")
        assert self.resolve(c) == "line"

    # auto_detect off

    def test_auto_detect_off_falls_back(self):
        c = self.Component(name="Hero", path="blocks/hero.html")
        assert self.resolve(c, auto_detect=False) == "line"

    def test_custom_default_variant(self):
        c = self.Component(name="Mystery", path="blocks/mystery.html")
        assert self.resolve(c, default_variant="skeleton") == "skeleton"

    # edge cases

    def test_empty_path_does_not_crash(self):
        c = self.Component(name="Empty", path="")
        result = self.resolve(c)
        assert result == "line"  # fallback to default

    def test_no_skeleton_no_match_returns_default(self):
        c = self.Component(
            name="Unknown", path="blocks/unknown_thing.html", category="Unknown"
        )
        assert self.resolve(c) == "line"


# ── settings defaults tests ────────────────────────────────────────────


class TestAnalyzerSettingsDefaults:
    """Verify _get_analyzer_options() returns expected defaults."""

    def test_defaults_when_django_not_configured(self):
        from django_fusion.fragments.analyzer.skeleton_view import (
            _get_analyzer_options,
        )

        cfg = _get_analyzer_options()
        assert cfg["ENABLED"] is False
        assert cfg["SKELETON_AUTO_DETECT"] is True
        assert cfg["SKELETON_DEFAULT_VARIANT"] == "line"
        assert cfg["ANALYZE_DEPTH"] == 3
        assert cfg["ANALYZE_FILTERS"] == {}

    def test_cfg_keys_match_analyzer_options(self):
        from django_fusion.config.analyzer import AnalyzerOptions
        from django_fusion.fragments.analyzer.skeleton_view import (
            _get_analyzer_options,
        )

        opts = AnalyzerOptions()
        cfg = _get_analyzer_options()
        assert cfg["ENABLED"] == opts.enabled
        assert cfg["SKELETON_AUTO_DETECT"] == opts.skeleton_auto_detect
        assert cfg["SKELETON_DEFAULT_VARIANT"] == opts.skeleton_default_variant
        assert cfg["CACHE_DURATION"] == opts.cache_duration
        assert cfg["ANALYZE_DEPTH"] == opts.analyze_depth
        assert cfg["ANALYZE_FILTERS"] == opts.analyze_filters
