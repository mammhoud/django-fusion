"""Website and page discovery helpers for the customizer UI."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.urls import reverse

SECTION_DIRS = {"sections", "components", "blocks", "layout"}
PAGE_DIR_HINTS = {"pages", "home", "landing", "layouts"}


def configured_websites() -> list[dict[str, object]]:
    """Return configured websites using the canonical display slugs."""
    websites: list[dict[str, object]] = []
    for website in settings.CUSTOMIZER_APPS:
        data = dict(website)
        root = Path(data.pop("template_root"))
        data["template_root"] = str(root)
        data["pages_url"] = reverse(
            "customizer_pages",
            kwargs={"website_slug": data["slug"]},
        )
        websites.append(data)
    return websites


def section_templates(root: Path) -> list[dict[str, object]]:
    """Return section/component templates below a website template root."""
    if not root.exists():
        return []

    sections: list[dict[str, object]] = []
    for path in sorted(root.rglob("*.html")):
        rel = path.relative_to(root)
        if not (set(rel.parts) & SECTION_DIRS):
            continue
        sections.append(
            {
                "path": rel.as_posix(),
                "name": path.stem.replace("_", " ").replace("-", " ").title(),
                "category": rel.parts[0] if rel.parts else "templates",
            }
        )
    return sections


def page_templates(root: Path) -> list[Path]:
    """Return likely page templates for a website template root."""
    if not root.exists():
        return []

    pages: list[Path] = []
    for path in sorted(root.rglob("*.html")):
        rel = path.relative_to(root)
        if set(rel.parts) & SECTION_DIRS:
            continue
        if len(rel.parts) == 1 or set(rel.parts) & PAGE_DIR_HINTS:
            pages.append(path)
    return pages


def pages_for_website(website_slug: str) -> dict[str, object] | None:
    """Build page-card data with sections linked to each page."""
    for website in configured_websites():
        if website["slug"] != website_slug:
            continue

        root = Path(str(website["template_root"]))
        sections = section_templates(root)
        pages = []
        for path in page_templates(root):
            rel = path.relative_to(root).as_posix()
            page_section_prefix = Path(rel).parent.as_posix()
            linked_sections = [
                section
                for section in sections
                if page_section_prefix == "."
                or section["path"].startswith(page_section_prefix)
                or section["category"] in {"sections", "components", "blocks"}
            ]
            pages.append(
                {
                    "path": rel,
                    "title": path.stem.replace("_", " ").replace("-", " ").title(),
                    "sections": linked_sections,
                }
            )

        return {"website": website, "pages": pages, "sections": sections}
    return None
