"""Unit tests for django-fusion component template tags.

Tests the four inclusion tags from ``components``:
``{% table %}``, ``{% pagination %}``, ``{% search %}``, ``{% form %}``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from django import forms
from django.conf import settings
from django.core.paginator import Paginator
from django.template import engines


# ── Template directory paths ──────────────────────────────────────────────

_ASSETS_TEMPLATES = str(
    Path(__file__).resolve().parents[3] / "assets" / "templates"
)
_OSOUL_COMP_TEMPLATES = str(
    Path(__file__).resolve().parent.parent
    / "src"
    / "django_fusion"
    / "comp"
    / "templates"
)


# ── Django template engine setup (module-scoped fixture) ──────────────────

@pytest.fixture(scope="module", autouse=True)
def _inject_template_dirs():
    """Augment existing Django TEMPLATES with our dirs and tag libs.

    Follows the same mutation pattern as ``test_comp_registry.py`` so
    we coexist with pytest-django's pre-configured settings.
    """
    templates = list(settings.TEMPLATES)
    if not templates:
        # settings.TEMPLATES is empty (conftest.py doesn't set it).
        # Bootstrap a minimal DjangoTemplates entry.
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
    # Find the DjangoTemplates backend entry
    target_idx = next(
        (
            i
            for i, t in enumerate(templates)
            if t.get("NAME") == "django"
            or t.get("BACKEND", "").endswith("DjangoTemplates")
        ),
        0,
    )

    for d in (_ASSETS_TEMPLATES, _OSOUL_COMP_TEMPLATES):
        if d not in templates[target_idx].setdefault("DIRS", []):
            templates[target_idx]["DIRS"].append(d)

    options = templates[target_idx].setdefault("OPTIONS", {})
    options.setdefault("libraries", {})["components"] = (
        "django_fusion.comp.templatetags.components"
    )
    # Register laces alias (provides comp used by form.html delegation chain)
    options["libraries"].setdefault(
        "laces", "django_fusion.comp.templatetags.components"
    )
    builtins = options.setdefault("builtins", [])
    if "django_fusion.comp.templatetags.components" not in builtins:
        builtins.append("django_fusion.comp.templatetags.components")
    # Also register components as a builtin (table, pagination, search, form)
    if "django_fusion.comp.templatetags.components" not in builtins:
        builtins.append("django_fusion.comp.templatetags.components")

    templates[target_idx].setdefault("NAME", "django")
    settings.TEMPLATES = templates
    engines._engines.clear()
    engines.__dict__.pop("templates", None)
    yield


# ── Helpers ───────────────────────────────────────────────────────────────

def _render(source: str, context: dict | None = None) -> str:
    """Render a template string using the ``django`` engine."""
    try:
        return engines["django"].from_string(source).render(context or {}).strip()
    except KeyError:
        pytest.fail(
            "No 'django' template engine found in settings.TEMPLATES. "
            "Ensure the _inject_template_dirs fixture ran."
        )


# ── Test data ─────────────────────────────────────────────────────────────

@pytest.fixture
def sample_headers():
    return [
        {"label": "Name", "sort_url": "/?sort=name", "is_sorted": False, "direction": ""},
        {"label": "Email", "sort_url": "/?sort=email", "is_sorted": True, "direction": "asc"},
        {"label": "Phone", "sort_url": "", "is_sorted": False, "direction": ""},
    ]


@pytest.fixture
def sample_rows():
    return [
        ["Alice", "alice@example.com", "555-0101"],
        ["Bob", "bob@example.com", "555-0102"],
    ]


@pytest.fixture
def paginated_page_obj():
    items = list(range(25))
    paginator = Paginator(items, 10)
    return paginator.get_page(2)


@pytest.fixture
def single_page_obj():
    paginator = Paginator(list(range(5)), 10)
    return paginator.get_page(1)


@pytest.fixture
def test_form():
    class TestForm(forms.Form):
        name = forms.CharField(label="Name", required=True)
        email = forms.EmailField(label="Email", required=False)
    return TestForm()


# ══════════════════════════════════════════════════════════════════════════
#  Python-level tag function tests
# ══════════════════════════════════════════════════════════════════════════

class TestTableTagFunction:
    def test_returns_context_with_headers_and_rows(self, sample_headers, sample_rows):
        from django_fusion.comp.templatetags.components.table import table
        ctx = table(headers=sample_headers, rows=sample_rows)
        assert ctx["headers"] == sample_headers
        assert ctx["rows"] == sample_rows
        assert ctx["hx_target"] == "#table-container"

    def test_defaults_empty_headers_and_rows(self):
        from django_fusion.comp.templatetags.components.table import table
        ctx = table()
        assert ctx["headers"] == []
        assert ctx["rows"] == []
        assert ctx["table"] is None

    def test_accepts_django_tables2_object(self):
        from django_fusion.comp.templatetags.components.table import table
        mock_table = object()
        ctx = table(table=mock_table)
        assert ctx["table"] is mock_table

    def test_passes_all_optional_params(self):
        from django_fusion.comp.templatetags.components.table import table
        ctx = table(
            hx_target="#my-list",
            table_class="table-sm table-striped",
            empty_message="Nothing to show",
        )
        assert ctx["hx_target"] == "#my-list"
        assert ctx["table_class"] == "table-sm table-striped"
        assert ctx["empty_message"] == "Nothing to show"


class TestPaginationTagFunction:
    def test_returns_context_with_page_obj(self, paginated_page_obj):
        from django_fusion.comp.templatetags.components.pagination import pagination
        ctx = pagination(page_obj=paginated_page_obj)
        assert ctx["page_obj"] is paginated_page_obj
        assert ctx["query_string"] == ""
        assert ctx["hx_target"] == ""

    def test_preserves_query_string(self, paginated_page_obj):
        from django_fusion.comp.templatetags.components.pagination import pagination
        ctx = pagination(page_obj=paginated_page_obj, query_string="q=test&cat=1")
        assert ctx["query_string"] == "q=test&cat=1"

    def test_passes_hx_target(self, paginated_page_obj):
        from django_fusion.comp.templatetags.components.pagination import pagination
        ctx = pagination(page_obj=paginated_page_obj, hx_target="#results")
        assert ctx["hx_target"] == "#results"


class TestSearchTagFunction:
    def test_returns_context_with_defaults(self):
        from django_fusion.comp.templatetags.components.search import search
        ctx = search()
        assert ctx["search_query"] == ""
        assert ctx["hx_target"] == ""
        assert ctx["extra_filters"] == {}
        assert ctx["max_width"] == "320px"

    def test_passes_search_query(self):
        from django_fusion.comp.templatetags.components.search import search
        ctx = search(search_query="django")
        assert ctx["search_query"] == "django"

    def test_passes_extra_filters(self):
        from django_fusion.comp.templatetags.components.search import search
        ctx = search(extra_filters={"category": "tech"})
        assert ctx["extra_filters"] == {"category": "tech"}

    def test_passes_htmx_config(self):
        from django_fusion.comp.templatetags.components.search import search
        ctx = search(hx_target="#results", hx_get="/api/search/")
        assert ctx["hx_target"] == "#results"
        assert ctx["hx_get"] == "/api/search/"


class TestFormTagFunction:
    def test_returns_context_with_form(self, test_form):
        from django_fusion.comp.templatetags.components.form import form
        ctx = form(form=test_form)
        assert ctx["form"] is test_form

    def test_passes_htmx_params(self, test_form):
        from django_fusion.comp.templatetags.components.form import form
        ctx = form(
            form=test_form,
            hx_post="/api/submit/",
            hx_target="#result",
            hx_swap="outerHTML",
        )
        assert ctx["hx_post"] == "/api/submit/"
        assert ctx["hx_target"] == "#result"
        assert ctx["hx_swap"] == "outerHTML"

    def test_passes_cancel_params(self, test_form):
        from django_fusion.comp.templatetags.components.form import form
        ctx = form(
            form=test_form,
            show_cancel=True,
            cancel_label="Discard",
            cancel_hx_get="/back/",
            cancel_hx_target="#form-area",
        )
        assert ctx["show_cancel"] is True
        assert ctx["cancel_hx_get"] == "/back/"
        assert ctx["cancel_hx_target"] == "#form-area"

    def test_passes_display_params(self, test_form):
        from django_fusion.comp.templatetags.components.form import form
        ctx = form(
            form=test_form,
            submit_label="Save Changes",
            form_id="my-form",
            form_class="custom-form",
        )
        assert ctx["submit_label"] == "Save Changes"
        assert ctx["form_id"] == "my-form"
        assert ctx["form_class"] == "custom-form"

    def test_passes_field_success_hint(self, test_form):
        from django_fusion.comp.templatetags.components.form import form
        ctx = form(
            form=test_form,
            field_success="username",
            success_message="Username is available!",
        )
        assert ctx["field_success"] == "username"
        assert ctx["success_message"] == "Username is available!"


# ══════════════════════════════════════════════════════════════════════════
#  Template file existence tests
# ══════════════════════════════════════════════════════════════════════════

_FUSION_TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "django_fusion"
    / "templates"
)


def test_table_template_exists():
    assert (_FUSION_TEMPLATES_DIR / "fusion" / "components" / "table.html").is_file()


def test_pagination_template_exists():
    assert (_FUSION_TEMPLATES_DIR / "fusion" / "components" / "pagination" / "pagination.html").is_file()


def test_search_template_exists():
    assert (_FUSION_TEMPLATES_DIR / "fusion" / "components" / "search.html").is_file()


def test_form_template_exists():
    assert (_FUSION_TEMPLATES_DIR / "components" / "form" / "form.html").is_file()


def test_routable_pagination_template_exists():
    """Pagination lives at fusion/components/pagination/pagination.html."""
    assert (_FUSION_TEMPLATES_DIR / "fusion" / "components" / "pagination" / "pagination.html").is_file()




# ══════════════════════════════════════════════════════════════════════════
#  Import and registration tests
# ══════════════════════════════════════════════════════════════════════════

def test_all_tags_importable_from_components():
    """All four tag functions are importable from components."""
    from django_fusion.comp.templatetags.components import (
        form,
        pagination,
        search,
        table,
    )
    assert callable(table)
    assert callable(pagination)
    assert callable(search)
    assert callable(form)


def test_all_tags_importable_from_submodules():
    """Individual sub-modules are also importable."""
    from django_fusion.comp.templatetags.components.form import form
    from django_fusion.comp.templatetags.components.pagination import pagination
    from django_fusion.comp.templatetags.components.search import search
    from django_fusion.comp.templatetags.components.table import table

    assert callable(table)
    assert callable(pagination)
    assert callable(search)
    assert callable(form)


def test_components_module_has_register():
    from django_fusion.comp.templatetags import components
    from django.template import Library
    assert hasattr(components, "register")
    assert isinstance(components.register, Library)


def test_components_exports_all_four():
    from django_fusion.comp.templatetags.components import (
        form,
        pagination,
        search,
        table,
    )
    assert callable(form)
    assert callable(pagination)
    assert callable(search)
    assert callable(table)
