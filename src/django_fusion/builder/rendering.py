"""
django_fusion.builder.rendering
===============================

The landing builder renderer.

``BuilderRenderer`` turns a ``BuilderPage`` into renderable output by:

1. Flattening the Wagtail StreamField into plain JSON-safe dicts
   (resolving ``PageChooserBlock`` values to URLs).
2. Resolving dynamic template fields (``{{ company.name }}``) in every text
   value against the page's ``template_context``, with URL sanitization on
   href-like keys.
3. Rendering each section through its ``builder/sections/<type>.html``
   partial (composing the shared ``fu-*`` component classes).
4. Exposing a JSON payload (``to_dict``) for the data-API road and a
   preview-issues report for the editor.
"""

from __future__ import annotations

from typing import Any

from django.template.loader import render_to_string
from wagtail.models import Page

from django_fusion.template_fields import TemplateFieldEngine, sanitize_url

#: Section template name for a block type.
SECTION_TEMPLATE = "builder/sections/{type}.html"

#: Keys whose resolved values are URLs and must be sanitized.
_URL_KEYS = {"href", "cta_href", "src", "url"}

#: Default stylesheets shipped with the builder (layout + lean theme build).
_DEFAULT_CSS = ["builder/builder.css", "builder/builder-theme.css"]


def _safe_static(path: str) -> str:
    """Resolve a static URL, falling back to the raw path on failure.

    Manifest-based storages (whitenoise) raise when a file has not been
    collected; tests and un-collected checkouts fall back to the plain
    ``/static/...`` path so rendering never crashes.
    """
    try:
        from django.templatetags.static import static

        return static(path)
    except Exception:
        return f"/static/{path}"


def _stream_to_plain(value: Any) -> Any:
    """Recursively convert Wagtail StreamField values to JSON-safe Python.

    Handles StructValue/ListValue from ``wagtail.blocks`` and resolves
    ``PageChooserBlock`` values to ``{id, title, url}`` dicts.
    """
    if isinstance(value, Page):
        try:
            return {"id": value.pk, "title": value.title, "url": value.url}
        except Exception:
            return {"id": value.pk, "title": value.title, "url": ""}
    if hasattr(value, "items") and hasattr(value, "get"):
        return {key: _stream_to_plain(item) for key, item in value.items()}
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        return [_stream_to_plain(item) for item in value]
    return value


def _normalize_page_links(value: Any) -> Any:
    """Promote serialized PageChooserBlock values to href keys recursively.

    A chosen page becomes ``{id, title, url}`` via ``_stream_to_plain``;
    editors may pick a page instead of typing a URL, so ``page`` → ``href``
    and ``<name>_page`` → ``<name>_href``, with the page title filling an
    empty label. Applies to nested dicts/lists (pricing tiers, features).
    """
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                _normalize_page_links(item)
        return value
    if not isinstance(value, dict):
        return value
    for key, item in list(value.items()):
        if isinstance(item, list):
            for sub in item:
                if isinstance(sub, dict):
                    _normalize_page_links(sub)
            continue
        if isinstance(item, dict) and item.get("url"):
            if key == "page":
                value["href"] = value.get("href") or item["url"]
                value["label"] = value.get("label") or item.get("title")
            elif key.endswith("_page"):
                base = key[: -len("_page")]
                value[f"{base}_href"] = value.get(f"{base}_href") or item["url"]
                value[f"{base}_label"] = value.get(f"{base}_label") or item.get("title")
    return value


def _resolve_dynamic(value: Any, engine: TemplateFieldEngine, context: dict[str, Any], *, path: str = "") -> Any:
    """Recursively resolve dynamic template fields in every string value.

    Strings containing ``{{`` are run through the engine. Values under
    URL-ish keys are additionally sanitized so a crafted context value
    cannot inject ``javascript:`` links.
    """
    if isinstance(value, str):
        if "{{" in value:
            value = engine.render(value, context)
        if path in _URL_KEYS:
            value = sanitize_url(value)
        return value
    if isinstance(value, list):
        return [_resolve_dynamic(item, engine, context, path=path) for item in value]
    if isinstance(value, dict):
        return {key: _resolve_dynamic(item, engine, context, path=key) for key, item in value.items()}
    return value


def _collect_text(value: Any, *, texts: list[str] | None = None) -> list[str]:
    """Collect every string value in a section payload (for validation)."""
    if texts is None:
        texts = []
    if isinstance(value, str):
        if "{{" in value:
            texts.append(value)
    elif isinstance(value, list):
        for item in value:
            _collect_text(item, texts=texts)
    elif isinstance(value, dict):
        for item in value.values():
            _collect_text(item, texts=texts)
    return texts


class BuilderRenderer:
    """Renders a ``BuilderPage``: sections, theme attributes, JSON, preview.

    Args:
        page: A concrete ``BuilderPage`` instance.
        request: Optional request (passed to template rendering).
        preview: Render in preview mode (adds a watermark + issue bar).
        context_override: Extra template-context values layered over the
            page's stored ``template_context`` (used by previews/tests).
    """

    def __init__(
        self,
        page,
        *,
        request=None,
        preview: bool = False,
        context_override: dict[str, Any] | None = None,
    ) -> None:
        self.page = page
        self.request = request
        self.preview = preview
        self.engine = TemplateFieldEngine()
        self.context = self._build_context(context_override)

    # ── context ────────────────────────────────────────────────────────────

    def _build_context(self, override: dict[str, Any] | None) -> dict[str, Any]:
        base = dict(self.page.template_context or {})
        if override:
            base.update(override)
        return base

    # ── theme attributes ───────────────────────────────────────────────────

    def theme_attrs(self) -> str:
        """The ``<html>`` attributes activating the page's theme/brand/dark mode."""
        attrs: list[str] = []
        if self.page.theme and self.page.theme != "default":
            attrs.append(f'data-theme="{self.page.theme}"')
        if self.page.brand:
            attrs.append(f'data-brand="{self.page.brand}"')
        if self.page.dark_mode:
            attrs.append('class="dark"')
        return " ".join(attrs)

    def css_urls(self) -> list[str]:
        """Resolved URLs for the builder's default stylesheets.

        Products override the page template's ``builder_css``/``theme_css``
        blocks to load their full compiled theme instead.
        """
        return [_safe_static(path) for path in _DEFAULT_CSS]

    # ── sections ───────────────────────────────────────────────────────────

    def sections(self) -> list[dict[str, Any]]:
        """Flatten the StreamField into resolved, JSON-safe section dicts."""
        return self._flatten_sections(resolve=True)

    def _flatten_sections(self, *, resolve: bool) -> list[dict[str, Any]]:
        """Flatten the StreamField into plain section dicts.

        With ``resolve=True`` dynamic template fields are resolved against the
        context; with ``resolve=False`` the raw ``{{ variable }}`` text is
        kept (used for validation/preview issue reporting).
        """
        sections: list[dict[str, Any]] = []
        for block in self.page.sections:
            data = _stream_to_plain(block.value)
            _normalize_page_links(data)
            data["type"] = block.block_type
            if resolve:
                data = _resolve_dynamic(data, self.engine, self.context)
            sections.append(data)
        return sections

    def sections_html(self) -> str:
        """Render every section to HTML via its partial template."""
        parts: list[str] = []
        for section in self.sections():
            template_name = SECTION_TEMPLATE.format(type=section["type"])
            parts.append(
                render_to_string(
                    template_name,
                    {"section": section, "builder": self},
                    request=self.request,
                )
            )
        return "".join(parts)

    # ── validation / preview ───────────────────────────────────────────────

    def preview_issues(self) -> list[dict[str, Any]]:
        """Collect validation issues across all section text values.

        Validates the *raw* (unresolved) section text so unresolved dynamic
        fields are reported even though the rendered output fails safe to
        empty strings.
        """
        issues: list[dict[str, Any]] = []
        for section in self._flatten_sections(resolve=False):
            for text in _collect_text(section):
                for issue in self.engine.validate(text, context=self.context):
                    issues.append(
                        {
                            "level": issue.level,
                            "code": issue.code,
                            "message": issue.message,
                            "path": issue.path,
                        }
                    )
        return issues

    def has_unresolved(self) -> bool:
        return any(issue["code"] == "unresolved" for issue in self.preview_issues())

    @property
    def unresolved_count(self) -> int:
        """Number of unresolved dynamic fields across all sections."""
        return sum(1 for issue in self.preview_issues() if issue["code"] == "unresolved")

    # ── data API ───────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """The JSON payload consumed by the data-API road and Astro clients."""
        return {
            "id": self.page.pk,
            "slug": self.page.slug or "home",
            "title": self.page.title,
            "type": self.page.__class__.__name__,
            "theme": self.page.theme,
            "brand": self.page.brand,
            "dark_mode": self.page.dark_mode,
            "seo_title": getattr(self.page, "seo_title", "") or self.page.title,
            "search_description": getattr(self.page, "search_description", ""),
            "template_context": self.context,
            "sections": self.sections(),
            "preview": self.preview,
            "issues": self.preview_issues(),
        }


__all__ = ["BuilderRenderer", "_collect_text", "_normalize_page_links", "_resolve_dynamic", "_stream_to_plain"]
