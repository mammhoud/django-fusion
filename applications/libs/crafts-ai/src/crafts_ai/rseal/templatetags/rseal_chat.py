"""
{% load rseal_chat %}
{% chat_bubble %}                          — default config from settings
{% chat_bubble backend="rasa" title="Help" greeting="Hi!" %}
{% chat_bubble context_object=product %}   — link to a DB model instance
"""
from __future__ import annotations

import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("components/chat/bubble.html", takes_context=True)
def chat_bubble(
    context,
    backend: str = "",
    title: str = "",
    greeting: str = "",
    placeholder: str = "",
    system_prompt: str = "",
    context_object=None,
    context_data: dict = None,
):
    """
    Render the rseal bubble chat widget.

    Args:
        backend: AI backend override ("openai", "rasa", "echo").
                 Falls back to settings.RSEAL_CHAT_BACKEND.
        title: Header title shown in the chat panel.
        greeting: First bot message shown on open.
        placeholder: Input placeholder text.
        system_prompt: Optional system prompt injected into AI calls.
        context_object: Any Django model instance to link as context.
        context_data: Extra dict serialised as JSON context for the AI.
    """
    cfg_backend = backend or getattr(settings, "RSEAL_CHAT_BACKEND", "echo")
    cfg_title = title or getattr(settings, "RSEAL_CHAT_TITLE", "Assistant")
    cfg_greeting = greeting or getattr(settings, "RSEAL_CHAT_GREETING", "Hi! How can I help you today?")
    cfg_placeholder = placeholder or getattr(settings, "RSEAL_CHAT_PLACEHOLDER", "Type a message…")

    # Build JS config object passed to the widget
    js_config: dict = {"backend": cfg_backend}
    if system_prompt:
        js_config["system_prompt"] = system_prompt
    if context_data:
        js_config["context_data"] = context_data
    if context_object is not None:
        # Serialise linked object for the widget (display only; server handles DB link)
        if hasattr(context_object, "to_dict"):
            js_config["context_object"] = context_object.to_dict()
        else:
            js_config["context_object"] = {"str": str(context_object), "pk": getattr(context_object, "pk", None)}

    return {
        "chat_config": mark_safe(json.dumps(js_config)),
        "chat_title": cfg_title,
        "chat_greeting": cfg_greeting,
        "chat_placeholder": cfg_placeholder,
        "request": context.get("request"),
    }
