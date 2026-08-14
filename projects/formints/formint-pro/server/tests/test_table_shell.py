from __future__ import annotations

from pathlib import Path

import pytest
from django.template import engines
from django.test import override_settings


_SERVER_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = _SERVER_ROOT.parents[3]
_FUSION_TEMPLATES = (
    _REPO_ROOT / "libs" / "django-fusion" / "src" / "django_fusion" / "templates"
)
_FORMINT_TEMPLATES = _SERVER_ROOT / "formint" / "templates"


@pytest.mark.usefixtures("django_bootstrap")
def test_all_formint_tables_use_shared_fusion_shell():
    """The six server-rendered tables share the django-fusion shell contract."""
    templates = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [str(_FORMINT_TEMPLATES), str(_FUSION_TEMPLATES)],
            "APP_DIRS": False,
            "OPTIONS": {
                "libraries": {
                    "components": "django_fusion.comp.templatetags.components",
                },
            },
        }
    ]

    with override_settings(TEMPLATES=templates):
        template_engine = engines["django"]
        cases = {
            "products": (
                "products", "products", "/htmx/forms/product/", "+ New product",
            ),
            "customers": (
                "customers", "customers", "/htmx/forms/customer/", "+ New customer",
            ),
            "categories": (
                "categories", "categories", "/htmx/forms/category/", "+ New category",
            ),
            "client_categories": (
                "client_categories", "client categories",
                "/htmx/forms/client-category/", "+ New tier",
            ),
            "suppliers": (
                "suppliers", "suppliers", "/htmx/forms/supplier/", "+ New supplier",
            ),
            "sales": ("sales", "recent sales", None, None),
        }

        for resource, (fragment, count_label, new_url, new_label) in cases.items():
            template = template_engine.get_template(
                f"formint/tables/{resource}.html"
            )
            rendered = template.render(
                {
                    "resource": resource.replace("_", "-"),
                    "table_headers": [{"label": "Name"}],
                    "table_data": [{"id": 1, "name": "Demo"}],
                }
            )
            assert (
                f'data-fusion-fragment="formint.tables.{fragment}"' in rendered
            ), resource
            assert f"1 {count_label}" in rendered, resource
            if new_url:
                assert 'type="button"' in rendered, resource
                assert f'hx-get="{new_url}"' in rendered, resource
                assert new_label in rendered, resource
            else:
                assert "hx-get=" not in rendered, resource
