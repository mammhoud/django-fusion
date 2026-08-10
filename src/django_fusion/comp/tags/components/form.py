"""``{% form %}`` — unified form component inclusion tag.

Usage::

    {% load components %}

    {% form form=my_form hx_post="/api/endpoint/" hx_target="#result" submit_label="Save" %}
"""

from __future__ import annotations

from typing import Any

from django_fusion.comp.tags.components import register


@register.inclusion_tag("components/form/form.html", takes_context=False)
def form(
    form: Any = None,
    hx_post: str = "",
    hx_url: str = "",
    hx_target: str = "",
    hx_swap: str = "",
    hx_indicator: str = "",
    is_multipart: bool = False,
    form_class: str = "",
    form_id: str = "",
    form_action: str = "",
    form_method: str = "",
    form_extra_attrs: str = "",
    submit_label: str = "",
    submit_attrs: str = "",
    show_cancel: bool = False,
    cancel_label: str = "",
    cancel_onclick: str = "",
    cancel_hx_get: str = "",
    cancel_hx_target: str = "",
    cancel_hx_swap: str = "",
    field_success: str = "",
    success_message: str = "",
) -> dict[str, Any]:
    """Render a unified Django form with HTMX support.

    Renders the canonical ``components/form/form.html`` template, passing
    all parameters through.

    Args:
        form: Django form object (required).
        hx_post / hx_url: HTMX POST endpoint.
        hx_target: HTMX target selector.
        hx_swap: HTMX swap strategy.
        hx_indicator: HTMX loading indicator selector.
        is_multipart: Force multipart encoding.
        form_class: Extra CSS classes.
        form_id: HTML ``id`` attribute.
        form_action: Traditional form action URL.
        form_method: HTTP method when not using HTMX.
        form_extra_attrs: Raw HTML attributes string.
        submit_label: Submit button text.
        submit_attrs: Raw HTML attributes for submit button.
        show_cancel: Show a cancel button.
        cancel_label: Cancel button text.
        cancel_onclick: JS onclick for cancel.
        cancel_hx_get: HTMX GET URL for cancel navigation.
        cancel_hx_target: HTMX target for cancel.
        cancel_hx_swap: HTMX swap for cancel.
        field_success: Field name for per-field success hint.
        success_message: Success hint text.
    """
    return {
        "form": form,
        "hx_post": hx_post,
        "hx_url": hx_url,
        "hx_target": hx_target,
        "hx_swap": hx_swap,
        "hx_indicator": hx_indicator,
        "is_multipart": is_multipart,
        "form_class": form_class,
        "form_id": form_id,
        "form_action": form_action,
        "form_method": form_method,
        "form_extra_attrs": form_extra_attrs,
        "submit_label": submit_label,
        "submit_attrs": submit_attrs,
        "show_cancel": show_cancel,
        "cancel_label": cancel_label,
        "cancel_onclick": cancel_onclick,
        "cancel_hx_get": cancel_hx_get,
        "cancel_hx_target": cancel_hx_target,
        "cancel_hx_swap": cancel_hx_swap,
        "field_success": field_success,
        "success_message": success_message,
    }
