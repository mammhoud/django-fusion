"""Template section/component discovery utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_GET

SECTION_MARKERS = {"sections", "components", "blocks", "layout"}


def discover_sections(template_roots: Iterable[Path] | None = None) -> list[dict[str, str]]:
    """Discover reusable section/component templates below configured roots."""
    roots = list(template_roots or [Path(d) for d in settings.TEMPLATES[0].get("DIRS", [])])
    sections: list[dict[str, str]] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.html")):
            rel = path.relative_to(root)
            if SECTION_MARKERS.isdisjoint(rel.parts):
                continue
            sections.append(
                {
                    "template": str(rel),
                    "name": path.stem.replace("_", " ").title(),
                    "category": next((p for p in rel.parts if p in SECTION_MARKERS), "templates"),
                    "root": str(root),
                }
            )
    return sections


@require_GET
def sections_json(request):
    """Unauthenticated JSON endpoint for page/template renderer discovery."""
    return JsonResponse({"sections": discover_sections()})


@require_GET
def render_component_json(request):
    """Render a template via the comp renderer API without authentication."""
    template_name = request.GET.get("template")
    if not template_name:
        return JsonResponse({"error": "Missing template"}, status=400)
    html = render_to_string(template_name, {"request": request})
    return JsonResponse({"template": template_name, "html": html})
