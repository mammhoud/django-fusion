"""Cross-site smoke coverage for public pages and shared layout contracts.

These tests intentionally stay at the template/static-contract layer so they can
run quickly for every site without starting browsers or requiring fixture-heavy
Wagtail page trees. The contracts mirror the public pages each site exposes and
catch missing base layout includes, metadata, navigation, footer, asset bundles,
and representative dynamic content bindings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_ROOT = REPO_ROOT / "projects"


@dataclass(frozen=True)
class SiteSmokeSpec:
    key: str
    label: str
    root: Path
    public_templates: tuple[str, ...]
    base_templates: tuple[str, ...]
    navigation_templates: tuple[str, ...]
    footer_templates: tuple[str, ...]
    metadata_templates: tuple[str, ...]
    static_markers: tuple[str, ...]
    dynamic_markers: tuple[str, ...]
    component_templates: tuple[str, ...]


SITE_SPECS = (
    SiteSmokeSpec(
        key="ctc",
        label="CTC Research",
        root=APPS_ROOT / "precis" / "backend",
        public_templates=(
            "templates/index.html",
            "templates/base_page.html",
        ),
        base_templates=("templates/base.html", "templates/base_page.html"),
        navigation_templates=(),
        footer_templates=(),
        metadata_templates=(),
        static_markers=("{% extends", "{% load", "{% block", "<!DOCTYPE html>"),
        dynamic_markers=(
            "page.title",
            "fusion_layout",
            "wagtailcore_tags",
            "page.slug",
        ),
        component_templates=(
            "templates/base_page.html",
            "templates/events/event_page.html",
            "templates/blocks/minimal_contact_form.html",
        ),
    ),
    SiteSmokeSpec(
        key="structa",
        label="Structa Cloud",
        root=APPS_ROOT / "precis" / "precis-main" / "backend",
        public_templates=(
            "apps/pages/templates/pages/home.html",
            "apps/pages/templates/pages/about.html",
            "apps/pages/templates/pages/services.html",
            "apps/pages/templates/pages/products.html",
            "apps/pages/templates/pages/pricing.html",
            "apps/pages/templates/pages/contact.html",
        ),
        base_templates=("apps/pages/templates/pages/base.html",),
        navigation_templates=("apps/pages/templates/pages/partials/header.html",),
        footer_templates=("apps/pages/templates/pages/partials/footer.html",),
        metadata_templates=(),
        static_markers=("{% static", "{% load", "{% block"),
        dynamic_markers=(
            "page.title",
            "localized_content",
            "page.slug",
            "content_language",
        ),
        component_templates=(
            "apps/pages/templates/pages/partials/page_content.html",
            "apps/content/templates/content/blocks/hero.html",
            "apps/content/templates/content/blocks/editions.html",
        ),
    ),
)


@pytest.mark.parametrize("spec", SITE_SPECS, ids=lambda spec: spec.key)
def test_public_page_templates_exist_for_each_site(spec: SiteSmokeSpec) -> None:
    for relative_path in spec.public_templates:
        path = spec.root / relative_path
        assert path.exists(), f"{spec.label} public template missing: {relative_path}"
        assert path.read_text(encoding="utf-8").strip(), relative_path


@pytest.mark.parametrize("spec", SITE_SPECS, ids=lambda spec: spec.key)
def test_base_layout_includes_navigation_footer_metadata_and_assets(
    spec: SiteSmokeSpec,
) -> None:
    base_source = "\n".join(
        (spec.root / relative_path).read_text(encoding="utf-8")
        for relative_path in spec.base_templates
    )
    layout_source = (
        base_source
        + "\n"
        + "\n".join(
            (spec.root / relative_path).read_text(encoding="utf-8")
            for relative_path in (
                spec.navigation_templates
                + spec.footer_templates
                + spec.metadata_templates
            )
        )
    )

    if "<html" not in base_source:
        base_source += (APPS_ROOT / "assets" / "templates" / "base.html").read_text(
            encoding="utf-8"
        )

    assert "<html" in base_source
    assert "<body" in base_source
    assert "{% block" in base_source
    for marker in spec.static_markers:
        assert marker in layout_source
    has_nav = any(
        "nav" in marker.lower() or "navigation" in marker.lower()
        for marker in layout_source.split()
    )
    has_fusion_layout = "fusion_layout" in layout_source
    assert has_nav or has_fusion_layout, (
        f"{spec.label} missing nav/navigation markers and no fusion_layout"
    )
    assert "footer" in layout_source.lower() or "fusion_layout" in layout_source
    assert "meta" in layout_source.lower()


@pytest.mark.parametrize("spec", SITE_SPECS, ids=lambda spec: spec.key)
def test_representative_components_and_dynamic_data_bindings_are_present(
    spec: SiteSmokeSpec,
) -> None:
    public_source = "\n".join(
        (spec.root / relative_path).read_text(encoding="utf-8")
        for relative_path in spec.base_templates
        + spec.public_templates
        + spec.component_templates
    )

    for relative_path in spec.component_templates:
        assert (
            spec.root / relative_path
        ).exists(), f"{spec.label} component template missing: {relative_path}"
    for marker in spec.dynamic_markers:
        assert (
            marker in public_source
        ), f"{spec.label} missing dynamic marker {marker!r}"
    assert "{% include" in public_source or "{% comp" in public_source
    assert "{% for" in public_source


def test_site_base_templates_expose_cross_site_layout_blocks() -> None:
    """Every site's base template exposes a document shell and content blocks.

    Each current Django site ships its own base layout (per-site templates in
    the new projects/ layout); the shared contract is a real document with
    template tags and overridable blocks.
    """
    for spec in SITE_SPECS:
        base_source = "\n".join(
            (spec.root / relative_path).read_text(encoding="utf-8")
            for relative_path in spec.base_templates
        )
        assert "<html" in base_source or "<body" in base_source, spec.label
        assert "{% block" in base_source, spec.label
        assert "{% load" in base_source, spec.label


def test_static_asset_dirs_cover_all_public_sites() -> None:
    """Shared static assets and per-site staticfiles roots exist for every site."""
    shared_static = APPS_ROOT / "assets" / "static"
    assert shared_static.is_dir()
    assert any(shared_static.iterdir())
    for spec in SITE_SPECS:
        static_root = spec.root / "assets" / "staticfiles"
        assert static_root.is_dir(), f"{spec.label} missing staticfiles dir"
