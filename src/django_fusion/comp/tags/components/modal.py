from __future__ import annotations

from django.urls import NoReverseMatch, reverse
from django.utils.html import conditional_escape, format_html

from django_fusion.comp.tags.components import register


@register.inclusion_tag("fusion/components/modal/modal.html")
def generate_modal(modal_id, modal_title, modal_body):
    """
    Template tag to generate a modal dialog.

    Usage:
        {% generate_modal modal_id="myModal" modal_title="Modal Title" modal_body="This is the body of the modal" %}
    """
    return {"modal_id": modal_id, "modal_title": modal_title, "modal_body": modal_body}


@register.simple_tag(takes_context=True)
def modal_link(context, url_name: str, label: str, css_class: str = "",
               target: str = "#unified-modal-container", swap: str = "innerHTML",
               **url_kwargs) -> str:
    """Render a modal-friendly link with non-HTMX fallback.

    The rendered HTML is always produced via :func:`django.utils.html.format_html`
    so user-supplied ``label`` text is properly escaped. A bad ``url_name``
    raises :exc:`NoReverseMatch` (loud failure) so a typo is visible at
    template render time, not silently producing ``href="#"``.

    Parameters
    ----------
    context
        Template context (injected by ``simple_tag(takes_context=True)``).
    url_name
        Django URL name to reverse (e.g. ``"blog:blog-detail"``).
    label
        Visible label text (auto-escaped).
    css_class
        Optional class applied to both the button and the anchor.
    target
        HTMX target selector (default: ``#unified-modal-container``).
    swap
        HTMX swap strategy (default: ``innerHTML``).
    **url_kwargs
        Forwarded to ``django.urls.reverse`` (e.g. ``slug="..."``).
    """
    href = reverse(url_name, kwargs=url_kwargs or None)
    safe_label = conditional_escape(label)
    request = context.get("request")
    is_htmx = bool(getattr(request, "htmx", False)) if request is not None else False
    class_attr = css_class or ""
    if is_htmx:
        return format_html(
            '<button type="button" hx-get="{href}" hx-target="{target}" hx-swap="{swap}"{cls}>{label}</button>',
            href=href,
            target=target,
            swap=swap,
            cls=format_html(' class="{}"', class_attr) if class_attr else "",
            label=safe_label,
        )
    return format_html(
        '<a href="{href}"{cls}>{label}</a>',
        href=href,
        cls=format_html(' class="{}"', class_attr) if class_attr else "",
        label=safe_label,
    )
