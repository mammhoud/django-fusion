"""Page catalog helpers for the customizer UI."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django_fusion.site.interface.pages import PageCatalog, TemplateRoot


def customizer_apps() -> list[dict[str, object]]:
    """Return configured apps with page data from the shared page catalog."""
    apps = []
    for app in settings.CUSTOMIZER_APPS:
        app_data = dict(app)
        root = Path(app_data.pop("template_root"))
        catalog = PageCatalog(
            template_roots=[
                TemplateRoot(
                    name=str(app_data.get("name") or app_data.get("label") or root),
                    path=root,
                    customizer_base_url=str(
                        app_data.get("customizer_url", "/cypercloud/")
                    ),
                )
            ]
        )
        app_data["template_root"] = str(root)
        app_data["pages"] = [page.to_dict() for page in catalog.pages()]
        app_data["templates"] = [
            section.to_dict()
            for page in catalog.template_pages()
            for section in page.sections
        ]
        apps.append(app_data)
    return apps
