from pathlib import Path
from types import SimpleNamespace

import pytest
from django.test import override_settings
from django_fusion.routes.pages.catalog import PageCatalog, TemplateRoot


def write_template(root: Path, name: str, content: str = "") -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.mark.django_db
def test_catalog_discovers_plain_template_pages_and_sections(tmp_path):
    write_template(
        tmp_path,
        "index.html",
        '{% include "sections/hero.html" %}\n{% include "components/card.html" %}',
    )
    write_template(tmp_path, "sections/hero.html", "Hero")
    write_template(tmp_path, "components/card.html", "Card")

    catalog = PageCatalog(template_roots=[TemplateRoot("demo", tmp_path)])

    # Use template_pages() to avoid Wagtail pages from the test database
    pages = catalog.template_pages()

    assert len(pages) == 1
    page = pages[0]
    assert page.title == "Index"
    assert page.path == "/"
    assert page.template == "index.html"
    assert page.component_paths == ("sections/hero.html", "components/card.html")
    assert [section.category for section in page.sections] == ["sections", "components"]
    assert page.customizer_url == "/customizer/?template=index.html"


@pytest.mark.django_db
def test_catalog_uses_customizer_settings_as_template_roots(tmp_path):
    write_template(tmp_path, "about.html", '{% include "blocks/profile.html" %}')
    write_template(tmp_path, "blocks/profile.html", "Profile")

    with override_settings(
        CUSTOMIZER_APPS=[
            {
                "name": "Demo",
                "template_root": str(tmp_path),
                "customizer_url": "/design/",
            }
        ]
    ):
        # Use template_pages() to avoid Wagtail pages from the test database
        pages = PageCatalog().template_pages()
        assert len(pages) == 1
        page = pages[0]

    assert page.slug == "about"
    assert page.path == "/about/"
    assert page.component_paths == ("blocks/profile.html",)
    assert page.customizer_url == "/design/?template=about.html"


def test_wagtail_page_summary_does_not_require_wagtail_database(tmp_path):
    write_template(tmp_path, "home_page.html", '{% include "layout/header.html" %}')
    write_template(tmp_path, "layout/header.html", "Header")
    page = SimpleNamespace(
        id=42,
        title="Home",
        slug="home",
        template="home_page.html",
        url_path="/home/",
    )

    summary = PageCatalog(template_roots=[tmp_path]).from_wagtail_page(page)

    assert summary.source == "wagtail"
    assert summary.title == "Home"
    assert summary.path == "/"
    assert summary.edit_url == "/admin/pages/42/edit/"
    assert summary.component_paths == ("layout/header.html",)
