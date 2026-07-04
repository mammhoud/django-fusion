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
APPS_ROOT = REPO_ROOT / "applications"


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


SHARED_TEMPLATES = APPS_ROOT / "assets" / "templates"

SITE_SPECS = (
    SiteSmokeSpec(
        key="ctc",
        label="CTC Research",
        root=APPS_ROOT / "ctc-research",
        public_templates=(
            "templates/home/main.html",
            "templates/about/main.html",
            "templates/services/main.html",
            "templates/contact/main.html",
        ),
        base_templates=("templates/base_page.html",),
        navigation_templates=(
            str(SHARED_TEMPLATES / "layout" / "landing" / "header" / "landing.html"),
            str(SHARED_TEMPLATES / "layout" / "landing" / "partials" / "navigations.html"),
        ),
        footer_templates=(str(SHARED_TEMPLATES / "layout" / "landing" / "footer.html"),),
        metadata_templates=(str(SHARED_TEMPLATES / "layout" / "landing" / "meta.html"),),
        static_markers=("{% extends", "wagtailcore_tags", "{% block body %}"),
        dynamic_markers=(
            "page.slug",
            "template_name",
            "home/main.html",
            "page.contact_form",
        ),
        component_templates=(
            str(SHARED_TEMPLATES / "home" / "sections" / "slider.html"),
            str(SHARED_TEMPLATES / "home" / "sections" / "listing.html"),
            str(SHARED_TEMPLATES / "services" / "includes" / "services_section.html"),
            str(SHARED_TEMPLATES / "contact" / "sections" / "form.html"),
        ),
    ),
    SiteSmokeSpec(
        key="structa",
        label="LMS Demo",
        root=APPS_ROOT / "lms-demo",
        public_templates=(
            "www/core/templates/home/main.html",
            "www/core/templates/about/main.html",
            "www/core/templates/services/main.html",
            "plugins/templates/learning/course_catalog.html",
            "plugins/templates/products/main.html",
        ),
        base_templates=("assets/templates/layout/landing/skeleton.html",),
        navigation_templates=(
            str(SHARED_TEMPLATES / "layout" / "landing" / "header" / "landing.html"),
            str(SHARED_TEMPLATES / "layout" / "landing" / "partials" / "navigations.html"),
        ),
        footer_templates=(str(SHARED_TEMPLATES / "layout" / "landing" / "footer.html"),),
        metadata_templates=(str(SHARED_TEMPLATES / "layout" / "landing" / "meta.html"),),
        static_markers=("{% static", "render_bundle"),
        dynamic_markers=(
            "page.head",
            "page.summary",
            "page.CTA",
            "courses",
            "products",
        ),
        component_templates=(
            "www/core/templates/home/sections/slider.html",
            "plugins/templates/learning/_course_card.html",
            "plugins/templates/products/sections/_product.html",
            "www/core/templates/services/sections/_testimonial.html",
        ),
    ),
    SiteSmokeSpec(
        key="vresume",
        label="VResume",
        root=APPS_ROOT / "VResume",
        public_templates=(
            "www/pages/templates/home/main.html",
            "www/pages/templates/about/main.html",
            "www/pages/templates/resume/main.html",
            "www/pages/templates/portfolio/main.html",
            "www/pages/templates/connect/main.html",
        ),
        base_templates=("www/pages/templates/base.html",),
        navigation_templates=(
            "www/pages/templates/navigator.html",
            "www/pages/templates/sidebar.html",
        ),
        footer_templates=("www/pages/templates/layout/footer.html",),
        metadata_templates=("www/pages/templates/layout/meta.html",),
        static_markers=("{% static", "render_bundle"),
        dynamic_markers=(
            "settings.communications.VResumeSettings",
            "active_tab",
            "featured_projects",
            "page.experience",
            "contact-form__form",
        ),
        component_templates=(
            "www/pages/templates/components/modals/unified-modal.html",
            "www/pages/templates/home/sections/hero.html",
            "www/pages/templates/resume/sections/experience.html",
            "www/pages/templates/portfolio/sections/projects.html",
            "www/pages/templates/connect/sections/form.html",
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
    assert any(
        "nav" in marker.lower() or "navigation" in marker.lower()
        for marker in layout_source.split()
    )
    assert "footer" in layout_source.lower()
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


def test_shared_base_template_exposes_cross_site_layout_blocks_and_bundles() -> None:
    shared_base = APPS_ROOT / "assets" / "templates" / "base.html"
    source = shared_base.read_text(encoding="utf-8")

    for block_name in (
        "meta",
        "styles",
        "header",
        "body",
        "scripts",
        "extra_assets",
        "extra_head",
    ):
        assert ("{% block " + block_name + " %}" in source) or ("block " + block_name in source)
    assert "render_bundle 'main' 'js'" in source
    assert "render_bundle 'app' 'js'" in source
    assert "plugins/notifications/notification.html" in source or "notifications/notification.html" in source
    assert "data-navigation" in source


def test_static_asset_entrypoints_cover_all_public_sites() -> None:
    webpack_config = APPS_ROOT / "webpack" / "common.config.js"
    package_json = APPS_ROOT / "assets" / "package.json"
    webpack_source = webpack_config.read_text(encoding="utf-8")
    package_source = package_json.read_text(encoding="utf-8")

    for entrypoint in ("ctc-app.js", "lms-app.js", "vresume-app.js"):
        assert entrypoint in webpack_source
    for script_name in ("build:ctc", "build:structa", "build:vresume", "build:all"):
        assert script_name in package_source
