"""Page discovery services for customizer and site tooling."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import re
from typing import Any, Iterable

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import DatabaseError, OperationalError, ProgrammingError
from django.template import engines
from django.urls import NoReverseMatch, reverse

SECTION_DIRS = {"sections", "components", "blocks", "layout"}
INCLUDE_RE = re.compile(r"{%\s*(?:include|extends)\s+[\"']([^\"']+)[\"']")


@dataclass(frozen=True)
class SectionSummary:
    """A reusable template section discovered for a page."""

    name: str
    path: str
    category: str
    component_paths: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PageSummary:
    """Structured page metadata used by customizer UIs."""

    title: str
    slug: str
    path: str
    template: str | None = None
    sections: tuple[SectionSummary, ...] = ()
    component_paths: tuple[str, ...] = ()
    edit_url: str | None = None
    customizer_url: str | None = None
    source: str = "template"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["sections"] = [section.to_dict() for section in self.sections]
        return data


@dataclass(frozen=True)
class TemplateRoot:
    """Named template root available to the catalog."""

    name: str
    path: Path
    customizer_base_url: str = "/customizer/"


@dataclass
class PageCatalog:
    """Discover Wagtail pages and plain template-backed pages."""

    template_roots: Iterable[TemplateRoot | Path | str] | None = None
    section_dirs: set[str] = field(default_factory=lambda: set(SECTION_DIRS))

    def pages(self) -> list[PageSummary]:
        seen: set[tuple[str, str | None]] = set()
        summaries: list[PageSummary] = []
        for page in self.wagtail_pages():
            seen.add((page.path, page.template))
            summaries.append(page)
        for page in self.template_pages():
            if (page.path, page.template) not in seen:
                summaries.append(page)
        return sorted(summaries, key=lambda page: page.path)

    def template_pages(self) -> list[PageSummary]:
        summaries: list[PageSummary] = []
        for root in self.get_template_roots():
            for template in self._iter_templates(root.path):
                if set(Path(template).parts) & self.section_dirs:
                    continue
                summaries.append(self.from_template(template, root))
        return summaries

    def wagtail_pages(self) -> list[PageSummary]:
        if not apps.is_installed("wagtail"):
            return []
        try:
            page_model = apps.get_model("wagtailcore", "Page")
        except (LookupError, ImproperlyConfigured):
            return []
        try:
            records = page_model.objects.live().public().specific().defer_streamfields()
        except AttributeError:
            records = page_model.objects.all()
        try:
            return [self.from_wagtail_page(page) for page in records]
        except (DatabaseError, OperationalError, ProgrammingError):
            return []

    def from_wagtail_page(self, page: Any) -> PageSummary:
        template = getattr(page, "template", None)
        full_url = getattr(page, "full_url", None)
        url_path = getattr(page, "url_path", "") or ""
        path = full_url or self._clean_path(url_path) or f"/{getattr(page, 'slug', '')}/"
        return PageSummary(
            title=getattr(page, "title", str(page)),
            slug=getattr(page, "slug", ""),
            path=path,
            template=template,
            sections=self.sections_for_template(template),
            component_paths=self.component_paths_for_template(template),
            edit_url=self._wagtail_edit_url(page),
            customizer_url=self._customizer_url(path=path, template=template),
            source="wagtail",
        )

    def from_template(self, template: str, root: TemplateRoot) -> PageSummary:
        slug = Path(template).stem
        path = "/" if slug in {"index", "home"} else f"/{slug}/"
        return PageSummary(
            title=slug.replace("_", "-").replace("-", " ").title(),
            slug=slug,
            path=path,
            template=template,
            sections=self.sections_for_template(template),
            component_paths=self.component_paths_for_template(template),
            customizer_url=self._customizer_url(path=path, template=template, root=root),
        )

    def sections_for_template(self, template: str | None) -> tuple[SectionSummary, ...]:
        return tuple(
            SectionSummary(
                name=Path(path).stem.replace("_", " ").title(),
                path=path,
                category=self._category_for(path),
                component_paths=(path,),
            )
            for path in self.component_paths_for_template(template)
        )

    def component_paths_for_template(self, template: str | None) -> tuple[str, ...]:
        if not template:
            return ()
        return tuple(
            dict.fromkeys(
                path for path in self._included_templates(template)
                if self._is_component_path(path)
            )
        )

    def get_template_roots(self) -> list[TemplateRoot]:
        roots = self.template_roots
        if roots is None:
            roots = self._roots_from_customizer_settings() or self._roots_from_django()
        result: list[TemplateRoot] = []
        for index, root in enumerate(roots):
            if isinstance(root, TemplateRoot):
                result.append(root)
            else:
                result.append(TemplateRoot(name=f"templates-{index}", path=Path(root)))
        return result

    def _roots_from_customizer_settings(self) -> list[TemplateRoot]:
        roots = []
        for app in getattr(settings, "CUSTOMIZER_APPS", []):
            root = app.get("template_root")
            if root:
                roots.append(TemplateRoot(
                    name=str(app.get("name") or app.get("label") or root),
                    path=Path(root),
                    customizer_base_url=str(app.get("customizer_url", "/customizer/")),
                ))
        return roots

    def _roots_from_django(self) -> list[TemplateRoot]:
        roots = []
        for backend in engines.all():
            engine = getattr(backend, "engine", None)
            roots.extend(
                TemplateRoot(name=Path(directory).name, path=Path(directory))
                for directory in getattr(engine, "dirs", [])
            )
        return roots

    def _iter_templates(self, root: Path) -> Iterable[str]:
        if not root.exists():
            return []
        return (str(path.relative_to(root)) for path in sorted(root.rglob("*.html")))

    def _included_templates(self, template: str) -> tuple[str, ...]:
        for root in self.get_template_roots():
            candidate = root.path / template
            if candidate.exists():
                return tuple(INCLUDE_RE.findall(candidate.read_text(encoding="utf-8")))
        return ()

    def _is_component_path(self, path: str) -> bool:
        return bool(set(Path(path).parts) & self.section_dirs)

    def _category_for(self, path: str) -> str:
        for part in Path(path).parts:
            if part in self.section_dirs:
                return part
        return "templates"

    def _wagtail_edit_url(self, page: Any) -> str | None:
        page_id = getattr(page, "id", None) or getattr(page, "pk", None)
        if not page_id:
            return None
        try:
            return reverse("wagtailadmin_pages:edit", args=[page_id])
        except NoReverseMatch:
            return f"/admin/pages/{page_id}/edit/"

    def _customizer_url(self, *, path: str, template: str | None, root: TemplateRoot | None = None) -> str:
        base = (root.customizer_base_url if root else "/customizer/").rstrip("/")
        target = template or path.strip("/") or "index"
        return f"{base}/?template={target}"

    def _clean_path(self, path: str) -> str:
        if not path:
            return ""
        parts = [part for part in path.strip("/").split("/") if part]
        if parts and parts[0] == "home":
            parts = parts[1:]
        return "/" + "/".join(parts) + ("/" if parts else "")


def discover_pages(template_roots: Iterable[TemplateRoot | Path | str] | None = None) -> list[PageSummary]:
    """Convenience wrapper for page catalog discovery."""
    return PageCatalog(template_roots=template_roots).pages()


__all__ = ["PageCatalog", "PageSummary", "SectionSummary", "TemplateRoot", "discover_pages"]
