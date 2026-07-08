"""fusion_tags — reusable template tags for the django_fusion component system.

* ``modal_link`` — renders a button-or-anchor element that uses HTMX when
  the request has the ``HX-Request: true`` header, and falls back to a plain
  ``<a href="...">`` when the request is a normal GET. This means a project
  page works with or without JavaScript: crawlers, preview tools, and
  users with JS disabled still get a navigable link.

Usage::

    {% load fusion_tags %}
    {% modal_link url_name="blog:blog-detail" slug=post.slug label=post.title css_class="card__link" %}
"""
from __future__ import annotations

from django import template
from django.urls import NoReverseMatch, reverse
from django.utils.html import conditional_escape, format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def modal_link(context, url_name: str, label: str, css_class: str = "",
               target: str = "#unified-modal-container", swap: str = "innerHTML",
               **url_kwargs) -> str:
    """Render a modal-friendly link with non-HTMX fallback.

    The rendered HTML is always produced via :func:`django.utils.html.format_html`
    so user-supplied ``label`` text is properly escaped. A bad ``url_name``
    raises :exc:`NoReverseMatch` (loud failure) so a typo is visible at
    template render time, not silently producing ``href="#"``.

    The reversed URL is treated as trusted (``mark_safe``) because Django's
    URL layer escapes any user data; this preserves ``&`` and other chars
    inside query strings that ``format_html`` would otherwise double-escape.

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
    # `reverse()` already returns a `SafeString` (Django's URL layer is
    # trusted), so the value can be passed straight into `format_html`
    # without re-escaping. A typo in `url_name` raises `NoReverseMatch`
    # loudly rather than degrading silently to `href="#"`.
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
