"""Unit tests for the nav_link and nav_panel template tags.

Tests the two inclusion tags from ``navigation``:

- ``{% nav_link %}`` — single navigation anchor
- ``{% nav_panel %}`` — vertical navigation panel with multiple links

Verifies correct Unpoly (up-follow / up-target) vs HTMX (hx-get / hx-target)
attribute generation based on the ``UNPOLY_ENABLED`` Django setting.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from django.conf import settings
from django.http import HttpRequest
from django.template import engines
from django.utils.safestring import mark_safe


# ── Template directory paths ──────────────────────────────────────────────

_NAV_TEMPLATES_DIR = str(
    Path(__file__).resolve().parent.parent
    / "src"
    / "django_fusion"
    / "templates"
)


# ── Django template engine setup (module-scoped fixture) ──────────────────

@pytest.fixture(scope="module", autouse=True)
def _inject_template_dirs_and_libraries():
    """Augment existing Django TEMPLATES with our dirs and tag libs.

    Registers:
      - ``navigation`` → nav_link / nav_panel tags
      - ``components`` → filter_by_url + base component tags
    Adds ``_NAV_TEMPLATES_DIR`` to DIRS so inclusion tag templates resolve.
    """
    templates = list(settings.TEMPLATES)
    if not templates:
        templates = [
            {
                "NAME": "django",
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [],
                    "libraries": {},
                    "builtins": [],
                },
            }
        ]
    target_idx = next(
        (
            i
            for i, t in enumerate(templates)
            if t.get("NAME") == "django"
            or t.get("BACKEND", "").endswith("DjangoTemplates")
        ),
        0,
    )

    # Add navigation templates directory so inclusion tags resolve
    dirs: list = templates[target_idx].setdefault("DIRS", [])
    for d in (_NAV_TEMPLATES_DIR,):
        if d not in dirs:
            dirs.append(d)

    # Register libraries
    options = templates[target_idx].setdefault("OPTIONS", {})
    libs: dict = options.setdefault("libraries", {})
    libs["navigation"] = (
        "django_fusion.comp.tags.navigation"
    )
    libs["components"] = (
        "django_fusion.comp.tags.components"
    )
    builtins: list = options.setdefault("builtins", [])
    if "django_fusion.comp.tags.components" not in builtins:
        builtins.append("django_fusion.comp.tags.components")

    templates[target_idx].setdefault("NAME", "django")
    settings.TEMPLATES = templates
    engines._engines.clear()
    engines.__dict__.pop("templates", None)
    yield


# ── Helpers ───────────────────────────────────────────────────────────────


def _render(source: str, context: dict | None = None) -> str:
    """Render a template string using the ``django`` engine."""
    ctx = context or {}
    if "request" not in ctx:
        # Provide a minimal request so nav_link/nav_panel don't crash
        req = HttpRequest()
        req.path = "/"
        req.META["SERVER_NAME"] = "testserver"
        req.META["SERVER_PORT"] = "80"
        ctx["request"] = req
    try:
        return engines["django"].from_string(source).render(ctx).strip()
    except KeyError:
        pytest.fail(
            "No 'django' template engine found in settings.TEMPLATES. "
            "Ensure the _inject_template_dirs_and_libraries fixture ran."
        )


def _make_request(path: str = "/") -> HttpRequest:
    """Create a minimal HttpRequest with the given path."""
    req = HttpRequest()
    req.path = path
    req.META["SERVER_NAME"] = "testserver"
    req.META["SERVER_PORT"] = "80"
    return req


# ══════════════════════════════════════════════════════════════════════════
#  Python-level nav_link function tests
# ══════════════════════════════════════════════════════════════════════════


class TestNavLinkPython:
    """Test the ``nav_link()`` function directly (not via template rendering)."""

    def test_returns_expected_context_keys(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert "url" in ctx
        assert "label" in ctx
        assert "icon" in ctx
        assert "attrs" in ctx
        assert "is_active" in ctx
        assert "target" in ctx
        assert "unpoly_enabled" in ctx

    def test_default_unpoly_enabled_is_true(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert ctx["unpoly_enabled"] is True

    def test_unpoly_attrs_when_enabled(self):
        """When UNPOLY_ENABLED=True, attrs should include up-follow / up-target."""
        from django_fusion.comp.tags.navigation import nav_link
        with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
            request = _make_request("/")
            ctx = nav_link({}, url="/blog/", label="Blog", request=request)
            attrs = ctx["attrs"]
            assert "up-follow" in attrs
            assert 'up-target="#panel-content"' in attrs
            assert "hx-get" not in attrs
            assert "hx-trigger" not in attrs

    def test_htmx_attrs_when_unpoly_disabled(self):
        """When UNPOLY_ENABLED=False, attrs should include hx-get / hx-target."""
        from django_fusion.comp.tags.navigation import nav_link
        with patch.object(settings, "UNPOLY_ENABLED", False, create=True):
            request = _make_request("/")
            ctx = nav_link({}, url="/blog/", label="Blog", request=request)
            attrs = ctx["attrs"]
            assert "hx-get" in attrs
            assert 'hx-target="#panel-content"' in attrs
            assert 'hx-trigger="click"' in attrs
            assert "up-follow" not in attrs

    def test_href_always_present(self):
        """href should be present in both Unpoly and HTMX modes."""
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")

        with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
            ctx = nav_link({}, url="/blog/", label="Blog", request=request)
            assert 'href="/blog/"' in ctx["attrs"]

        with patch.object(settings, "UNPOLY_ENABLED", False, create=True):
            ctx = nav_link({}, url="/blog/", label="Blog", request=request)
            assert 'href="/blog/"' in ctx["attrs"]

    def test_custom_target(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link(
            {}, url="/blog/", label="Blog", target="#main-content", request=request
        )
        assert 'up-target="#main-content"' in ctx["attrs"]

    def test_layer_produces_up_layer_in_unpoly(self):
        from django_fusion.comp.tags.navigation import nav_link
        with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
            request = _make_request("/")
            ctx = nav_link(
                {}, url="/blog/", label="Blog", layer="modal", request=request
            )
            assert 'up-layer="modal"' in ctx["attrs"]

    def test_layer_not_present_in_htmx_mode(self):
        from django_fusion.comp.tags.navigation import nav_link
        with patch.object(settings, "UNPOLY_ENABLED", False, create=True):
            request = _make_request("/")
            ctx = nav_link(
                {}, url="/blog/", label="Blog", layer="modal", request=request
            )
            assert "up-layer" not in ctx["attrs"]

    def test_active_when_path_matches(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/blog/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert ctx["is_active"] is True

    def test_not_active_when_path_differs(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/other/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert ctx["is_active"] is False

    def test_active_when_subpath_match(self):
        """URL /blog/posts/ should match root /blog/ via startswith."""
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/blog/posts/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert ctx["is_active"] is True

    def test_root_url_not_active_for_all_paths(self):
        """The root URL '/' should only match when current path IS '/'."""
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/blog/")
        ctx = nav_link({}, url="/", label="Home", request=request)
        assert ctx["is_active"] is False

    def test_root_url_active_for_root_path(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link({}, url="/", label="Home", request=request)
        assert ctx["is_active"] is True

    def test_icon_passed_through(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link({}, url="/blog/", label="Blog", icon="bi-book", request=request)
        assert ctx["icon"] == "bi-book"

    def test_empty_icon_is_empty_string(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert ctx["icon"] == ""

    def test_resolves_named_url(self):
        """nav_link should resolve a named URL pattern via reverse().
        
        The test URL configuration has no named patterns registered, so
        reverse() will raise NoReverseMatch.  The tag falls back to
        returning the raw URL name — it should never crash.
        """
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link(
            {}, url="admin:index", label="Admin", request=request
        )
        # unresolvable → raw name returned (doesn't crash)
        assert ctx["url"] == "admin:index"
        assert ctx["label"] == "Admin"

    def test_literal_url_passed_through(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link(
            {}, url="https://example.com", label="External", request=request
        )
        assert ctx["url"] == "https://example.com"

    def test_absolute_path_passed_through(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link({}, url="/custom-path/", label="Custom", request=request)
        assert ctx["url"] == "/custom-path/"

    def test_falls_back_on_unresolvable_named_url(self):
        """When reverse() fails, the raw name is returned as the URL."""
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link(
            {}, url="nonexistent:url:that:does:not:exist", label="Bad", request=request
        )
        assert ctx["url"] == "nonexistent:url:that:does:not:exist"

    def test_css_class_in_attrs(self):
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/")
        ctx = nav_link(
            {}, url="/blog/", label="Blog", css_class="d-block mb-2", request=request
        )
        assert 'class="d-block mb-2"' in ctx["attrs"]

    def test_uses_context_request_when_no_explicit_request(self):
        """When request is not passed explicitly, context['request'] is used."""
        from django_fusion.comp.tags.navigation import nav_link
        request = _make_request("/blog/")
        ctx = nav_link({"request": request}, url="/blog/", label="Blog")
        assert ctx["is_active"] is True

    def test_attrs_is_safe_string(self):
        from django_fusion.comp.tags.navigation import nav_link
        from django.utils.safestring import SafeString
        request = _make_request("/")
        ctx = nav_link({}, url="/blog/", label="Blog", request=request)
        assert isinstance(ctx["attrs"], SafeString)


# ══════════════════════════════════════════════════════════════════════════
#  Python-level nav_panel function tests
# ══════════════════════════════════════════════════════════════════════════


class TestNavPanelPython:
    """Test the ``nav_panel()`` function directly."""

    def test_returns_expected_context_keys(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel(
            {},
            links=[
                {"url": "/blog/", "label": "Blog"},
                {"url": "/about/", "label": "About"},
            ],
        )
        assert "links" in ctx
        assert "title" in ctx
        assert "css_class" in ctx
        assert "unpoly_enabled" in ctx

    def test_links_have_required_keys(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel(
            {},
            links=[{"url": "/blog/", "label": "Blog"}],
        )
        link = ctx["links"][0]
        for key in ("url", "label", "icon", "attrs", "is_active", "target"):
            assert key in link, f"Missing key {key!r} in link dict"

    def test_unpoly_attrs_on_links(self):
        from django_fusion.comp.tags.navigation import nav_panel
        with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
            ctx = nav_panel(
                {},
                links=[{"url": "/blog/", "label": "Blog"}],
            )
            attrs = ctx["links"][0]["attrs"]
            assert "up-follow" in attrs
            assert 'up-target="#panel-content"' in attrs

    def test_htmx_attrs_on_links_when_disabled(self):
        from django_fusion.comp.tags.navigation import nav_panel
        with patch.object(settings, "UNPOLY_ENABLED", False, create=True):
            ctx = nav_panel(
                {},
                links=[{"url": "/blog/", "label": "Blog"}],
            )
            attrs = ctx["links"][0]["attrs"]
            assert "hx-get" in attrs
            assert 'hx-target="#panel-content"' in attrs
            assert 'hx-trigger="click"' in attrs
            assert "up-follow" not in attrs

    def test_per_link_target_override(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel(
            {},
            target="#shared-target",
            links=[
                {"url": "/one/", "label": "One"},
                {"url": "/two/", "label": "Two", "target": "#specific-target"},
            ],
        )
        assert ctx["links"][0]["target"] == "#shared-target"
        assert ctx["links"][1]["target"] == "#specific-target"

    def test_per_link_layer(self):
        from django_fusion.comp.tags.navigation import nav_panel
        with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
            ctx = nav_panel(
                {},
                links=[{"url": "/modal/", "label": "Modal", "layer": "modal"}],
            )
            assert 'up-layer="modal"' in ctx["links"][0]["attrs"]

    def test_empty_links_list_empty_string(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel({}, links=[])
        assert ctx["links"] == []

    def test_default_title_is_empty(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel({}, links=[{"url": "/", "label": "Home"}])
        assert ctx["title"] == ""

    def test_title_passed_through(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel(
            {}, links=[{"url": "/", "label": "Home"}], title="Navigation"
        )
        assert ctx["title"] == "Navigation"

    def test_default_css_class_is_card(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel({}, links=[{"url": "/", "label": "Home"}])
        assert ctx["css_class"] == "card"

    def test_custom_css_class(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel(
            {}, links=[{"url": "/", "label": "Home"}], css_class="sidebar-card"
        )
        assert ctx["css_class"] == "sidebar-card"

    def test_active_detection_per_link(self):
        from django_fusion.comp.tags.navigation import nav_panel
        request = _make_request("/blog/")
        ctx = nav_panel(
            {"request": request},
            links=[
                {"url": "/blog/", "label": "Blog"},
                {"url": "/about/", "label": "About"},
            ],
        )
        assert ctx["links"][0]["is_active"] is True
        assert ctx["links"][1]["is_active"] is False

    def test_icon_passed_through_per_link(self):
        from django_fusion.comp.tags.navigation import nav_panel
        ctx = nav_panel(
            {},
            links=[{"url": "/blog/", "label": "Blog", "icon": "bi-book"}],
        )
        assert ctx["links"][0]["icon"] == "bi-book"


# ══════════════════════════════════════════════════════════════════════════
#  Template rendering tests — {% nav_link %}
# ══════════════════════════════════════════════════════════════════════════


class TestNavLinkTemplate:
    """Test that ``{% nav_link %}`` renders correct HTML in templates."""

    def test_renders_anchor_with_href(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" %}'
        )
        assert '<a ' in html
        assert 'href="/blog/"' in html
        assert "Blog" in html

    def test_renders_up_follow_in_unpoly_mode(self):
        settings.UNPOLY_ENABLED = True
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_link url="/blog/" label="Blog" %}'
            )
            # "up-follow" appears as a bare HTML attribute with
            # surrounding spaces; the comment contains (up-follow/up-target)
            # so we check for the spaced form to avoid false positives.
            assert " up-follow " in html
            assert 'up-target="#panel-content"' in html
            assert "hx-get=" not in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_renders_htmx_in_htmx_mode(self):
        settings.UNPOLY_ENABLED = False
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_link url="/blog/" label="Blog" %}'
            )
            # "up-follow" in comment text must not trigger a match.
            # Check for the HTML attribute form (with surrounding spaces).
            assert " up-follow " not in html
            assert 'hx-get="/blog/"' in html
            assert 'hx-target="#panel-content"' in html
            assert 'hx-trigger="click"' in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_renders_hx_push_url_in_htmx_mode(self):
        settings.UNPOLY_ENABLED = False
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_link url="/blog/" label="Blog" %}'
            )
            assert 'hx-push-url="true"' in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_no_hx_push_url_in_unpoly_mode(self):
        """Unpoly mode should not include hx-push-url."""
        settings.UNPOLY_ENABLED = True
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_link url="/blog/" label="Blog" %}'
            )
            assert "hx-push-url" not in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_renders_icon_when_provided(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" icon="bi-book" %}'
        )
        assert '<i class="bi-book me-2"></i>' in html

    def test_no_icon_when_not_provided(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" %}'
        )
        assert "<i " not in html

    def test_aria_current_when_active(self):
        request = _make_request("/blog/")
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" %}',
            context={"request": request},
        )
        assert 'aria-current="page"' in html

    def test_no_aria_current_when_not_active(self):
        request = _make_request("/other/")
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" %}',
            context={"request": request},
        )
        assert "aria-current" not in html

    def test_custom_target_rendered(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" target="#sidebar" %}'
        )
        assert 'up-target="#sidebar"' in html

    def test_layer_rendered_in_unpoly(self):
        settings.UNPOLY_ENABLED = True
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_link url="/blog/" label="Blog" layer="modal" %}'
            )
            assert 'up-layer="modal"' in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_css_class_rendered(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" css_class="d-block mb-2 text-primary" %}'
        )
        assert 'class="d-block mb-2 text-primary"' in html

    def test_label_rendered_as_given(self):
        """The label is rendered inside a <span> tag."""
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog &amp; News" %}'
        )
        assert "<span>Blog &amp; News</span>" in html

    def test_renders_span_wrapper_for_label(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_link url="/blog/" label="Blog" %}'
        )
        assert "<span>Blog</span>" in html


# ══════════════════════════════════════════════════════════════════════════
#  Template rendering tests — {% nav_panel %}
# ══════════════════════════════════════════════════════════════════════════


class TestNavPanelTemplate:
    """Test that ``{% nav_panel %}`` renders correct HTML in templates."""

    def _panel_links(self) -> str:
        return (
            '{% load navigation %}'
            '{% nav_panel links=links %}'
        )

    def test_renders_nav_with_card_class(self):
        html = _render(
            self._panel_links(),
            context={
                "links": [
                    {"url": "/blog/", "label": "Blog"},
                    {"url": "/profile/", "label": "Profile"},
                ]
            },
        )
        assert '<nav class="card"' in html
        assert "Blog" in html
        assert "Profile" in html

    def test_renders_up_follow_in_unpoly_mode(self):
        settings.UNPOLY_ENABLED = True
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_panel links=links %}',
                context={"links": [{"url": "/blog/", "label": "Blog"}]},
            )
            assert " up-follow " in html
            assert "hx-get=" not in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_renders_htmx_in_htmx_mode(self):
        settings.UNPOLY_ENABLED = False
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_panel links=links %}',
                context={"links": [{"url": "/blog/", "label": "Blog"}]},
            )
            assert " up-follow " not in html
            assert 'hx-get="/blog/"' in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_renders_hx_push_url_in_htmx_mode(self):
        settings.UNPOLY_ENABLED = False
        try:
            html = _render(
                '{% load navigation %}'
                '{% nav_panel links=links %}',
                context={"links": [{"url": "/blog/", "label": "Blog"}]},
            )
            assert 'hx-push-url="true"' in html
        finally:
            try:
                delattr(settings, "UNPOLY_ENABLED")
            except AttributeError:
                pass

    def test_renders_title_header(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_panel links=links title="Profile Menu" %}',
            context={"links": [{"url": "/", "label": "Home"}]},
        )
        assert '<div class="card-header">' in html
        assert "Profile Menu" in html

    def test_no_card_header_when_no_title(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_panel links=links %}',
            context={"links": [{"url": "/", "label": "Home"}]},
        )
        assert "card-header" not in html

    def test_uses_ul_nav_flex_column(self):
        html = _render(
            self._panel_links(),
            context={"links": [{"url": "/", "label": "Home"}]},
        )
        assert '<ul class="nav flex-column">' in html
        assert '<li class="nav-item">' in html
        assert 'class="nav-link' in html

    def test_active_class_on_active_link(self):
        request = _make_request("/blog/")
        html = _render(
            self._panel_links(),
            context={
                "request": request,
                "links": [
                    {"url": "/blog/", "label": "Blog"},
                    {"url": "/about/", "label": "About"},
                ],
            },
        )
        assert 'class="nav-link active"' in html
        assert 'aria-current="page"' in html

    def test_icons_rendered(self):
        html = _render(
            self._panel_links(),
            context={
                "links": [
                    {"url": "/", "label": "Home", "icon": "bi-house"},
                ],
            },
        )
        assert '<i class="bi-house me-2"></i>' in html

    def test_empty_links_shows_empty_message(self):
        html = _render(
            self._panel_links(),
            context={"links": []},
        )
        assert "No navigation items." in html

    def test_custom_css_class(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_panel links=links css_class="sidebar-nav" %}',
            context={"links": [{"url": "/", "label": "Home"}]},
        )
        assert 'class="sidebar-nav"' in html

    def test_aria_label_with_title(self):
        html = _render(
            '{% load navigation %}'
            '{% nav_panel links=links title="Settings" %}',
            context={"links": [{"url": "/", "label": "Home"}]},
        )
        assert 'aria-label="Settings"' in html

    def test_aria_label_default_when_no_title(self):
        html = _render(
            self._panel_links(),
            context={"links": [{"url": "/", "label": "Home"}]},
        )
        assert 'aria-label="Navigation"' in html


# ══════════════════════════════════════════════════════════════════════════
#  Template file existence tests
# ══════════════════════════════════════════════════════════════════════════

_NAV_TEMPLATES_PATH = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "django_fusion"
    / "templates"
    / "fusion"
    / "navigation"
)


def test_nav_link_template_exists():
    assert (_NAV_TEMPLATES_PATH / "nav_link.html").is_file()


def test_nav_panel_template_exists():
    assert (_NAV_TEMPLATES_PATH / "nav_panel.html").is_file()


# ══════════════════════════════════════════════════════════════════════════
#  Import and registration tests
# ══════════════════════════════════════════════════════════════════════════


def test_nav_link_importable():
    from django_fusion.comp.tags.navigation import nav_link
    assert callable(nav_link)


def test_nav_panel_importable():
    from django_fusion.comp.tags.navigation import nav_panel
    assert callable(nav_panel)


def test_navigation_library_has_register():
    from django_fusion.comp.tags import navigation
    from django.template import Library
    assert hasattr(navigation, "register")
    assert isinstance(navigation.register, Library)


def test_helper_unpoly_enabled_default():
    from django_fusion.comp.tags.navigation import _unpoly_enabled
    with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
        assert _unpoly_enabled() is True
    with patch.object(settings, "UNPOLY_ENABLED", False, create=True):
        assert _unpoly_enabled() is False
    # When the setting is not defined, it should default to True
    # (but we can't easily test this with patch since we create the setting)


def test_helper_resolve_url_literal():
    from django_fusion.comp.tags.navigation import _resolve_url
    assert _resolve_url("/blog/") == "/blog/"
    assert _resolve_url("https://example.com") == "https://example.com"
    assert _resolve_url("http://example.com/path") == "http://example.com/path"


def test_helper_resolve_url_named():
    """_resolve_url handles unresolvable named URLs gracefully."""
    from django_fusion.comp.tags.navigation import _resolve_url
    result = _resolve_url("admin:index")
    # admin:index won't resolve in the test URL config
    assert result == "admin:index"  # returns raw name, doesn't crash


def test_helper_resolve_url_unresolvable():
    from django_fusion.comp.tags.navigation import _resolve_url
    result = _resolve_url("nonexistent:url:path")
    assert result == "nonexistent:url:path"


def test_helper_build_attrs_unpoly():
    from django_fusion.comp.tags.navigation import _build_attrs
    with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
        attrs = _build_attrs("/blog/")
        assert "up-follow" in attrs
        assert attrs["up-follow"] == ""
        assert attrs["up-target"] == "#panel-content"
        assert "hx-get" not in attrs


def test_helper_build_attrs_htmx():
    from django_fusion.comp.tags.navigation import _build_attrs
    with patch.object(settings, "UNPOLY_ENABLED", False, create=True):
        attrs = _build_attrs("/blog/")
        assert "up-follow" not in attrs
        assert attrs["hx-get"] == "/blog/"
        assert attrs["hx-target"] == "#panel-content"
        assert attrs["hx-trigger"] == "click"


def test_helper_build_attrs_custom_target():
    from django_fusion.comp.tags.navigation import _build_attrs
    attrs = _build_attrs("/blog/", target="#sidebar")
    assert attrs["up-target"] == "#sidebar"


def test_helper_build_attrs_layer():
    from django_fusion.comp.tags.navigation import _build_attrs
    with patch.object(settings, "UNPOLY_ENABLED", True, create=True):
        attrs = _build_attrs("/blog/", layer="modal")
        assert attrs["up-layer"] == "modal"


def test_helper_render_attrs_empty_value():
    from django_fusion.comp.tags.navigation import _render_attrs
    result = _render_attrs({"up-follow": "", "href": "/blog/"})
    # up-follow has empty value → rendered as bare attribute
    assert 'href="/blog/"' in result
    assert "up-follow" in result
    assert 'up-follow=""' not in result  # bare, not empty string


def test_helper_render_attrs_value():
    from django_fusion.comp.tags.navigation import _render_attrs
    result = _render_attrs({"href": "/blog/", "class": "nav-link"})
    assert 'href="/blog/"' in result
    assert 'class="nav-link"' in result
