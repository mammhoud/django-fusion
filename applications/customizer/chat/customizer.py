"""Template discovery helpers for the customizer UI."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings

SECTION_DIRS = {"sections", "components", "blocks", "layout"}


def template_tree(root: Path) -> list[dict[str, object]]:
    """Return a small JSON-serializable tree of sections/components."""
    if not root.exists():
        return []
    items: list[dict[str, object]] = []
    for path in sorted(root.rglob("*.html")):
        rel = path.relative_to(root)
        if not (set(rel.parts) & SECTION_DIRS):
            continue
        items.append(
            {
                "path": str(rel),
                "name": path.stem.replace("_", " ").title(),
                "category": rel.parts[0] if rel.parts else "templates",
            }
        )
    return items


def customizer_apps() -> list[dict[str, object]]:
    apps = []
    for app in settings.CUSTOMIZER_APPS:
        app_data = dict(app)
        root = Path(app_data.pop("template_root"))
        app_data["template_root"] = str(root)
        app_data["templates"] = template_tree(root)
        apps.append(app_data)
    return apps
