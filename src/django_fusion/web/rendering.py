"""
django_fusion.rendering
======================

Generic template renderer for Django projects.

Provides HTML rendering, email rendering (HTML + text + subject),
component rendering, and an HttpResponse helper.

This module has **no dependency** on django-rseal, Wagtail, or any
application-layer package.

Classes
-------
TemplateRenderer
    The main renderer class.

Settings
--------
``OSOUL_TEMPLATE_RENDERER``
    Dotted import path to a custom :class:`TemplateRenderer` subclass.

Usage::

    from django_fusion.web.rendering import TemplateRenderer

    renderer = TemplateRenderer()
    html = renderer.render("emails/invitation.html", {"name": "Alice"})

    email = renderer.render_email(
        "emails/invitation.html",
        context={"name": "Alice"},
        subject="You're invited",
    )

    response = renderer.render_to_response("account/login.html", ctx, request)
    html = renderer.render_component("card.html", {"title": "Hello"})
    renderer = TemplateRenderer.get_default()
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from django.http import HttpResponse
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

_default_renderer: Optional["TemplateRenderer"] = None


def _strip_html(html: str) -> str:
    """Strip HTML tags to produce a plain-text version."""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class TemplateRenderer:
    """
    Generic template renderer for Django projects.

    Wraps Django's template engine with email-aware rendering,
    component rendering, and a configurable singleton default.

    Args:
        template_dirs: Extra template directories (informational).
        context_processors: Extra context processor dotted paths (informational).
    """

    def __init__(
        self,
        template_dirs: list = None,
        context_processors: list = None,
    ):
        self.template_dirs = template_dirs or []
        self.context_processors = context_processors or []

    def render(self, template_name: str, context: dict, request=None) -> str:
        """
        Render a Django template to a string.

        Args:
            template_name: Template path (e.g. ``"emails/invitation.html"``).
            context: Template context variables.
            request: Optional HttpRequest — enables context processors.

        Returns:
            Rendered HTML string.
        """
        try:
            return render_to_string(template_name, context, request=request)
        except TemplateDoesNotExist:
            logger.error("Template not found: %s", template_name)
            raise
        except Exception as exc:
            logger.error("Template render error for %s: %s", template_name, exc)
            raise

    def render_email(
        self,
        template_name: str,
        context: dict,
        subject: str = None,
    ) -> dict:
        """
        Render an email template returning HTML, plain-text, and subject.

        Looks for a companion ``*.txt`` template; falls back to stripping HTML.

        Args:
            template_name: HTML template path.
            context: Template context variables.
            subject: Email subject. Falls back to ``context["subject"]``.

        Returns:
            dict with keys ``html``, ``text``, ``subject``.
        """
        html = self.render(template_name, context)
        text = _strip_html(html)

        text_template = template_name.replace(".html", ".txt")
        try:
            text = self.render(text_template, context)
        except TemplateDoesNotExist:
            pass

        return {
            "html": html,
            "text": text,
            "subject": subject or context.get("subject", ""),
        }

    def render_to_response(
        self,
        template_name: str,
        context: dict,
        request=None,
        status: int = 200,
        content_type: str = "text/html; charset=utf-8",
    ) -> HttpResponse:
        """
        Render a template and return an HttpResponse.

        Args:
            template_name: Template path.
            context: Template context.
            request: Optional Django request.
            status: HTTP status code (default 200).
            content_type: Response content-type header.

        Returns:
            HttpResponse with rendered content.
        """
        html = self.render(template_name, context, request=request)
        return HttpResponse(html, status=status, content_type=content_type)

    def render_component(
        self,
        component_name: str,
        props: dict,
        request=None,
    ) -> str:
        """
        Render a ``comp/`` component template by name.

        Prepends ``"components/"`` if not already present.

        Args:
            component_name: Component template name (e.g. ``"card.html"``).
            props: Component properties / context dict.
            request: Optional Django request.

        Returns:
            Rendered component HTML string.
        """
        if not component_name.startswith("components/"):
            component_name = f"components/{component_name}"
        return self.render(component_name, props, request=request)

    @classmethod
    def get_default(cls) -> "TemplateRenderer":
        """
        Return the default TemplateRenderer singleton.

        Controlled by the ``OSOUL_TEMPLATE_RENDERER`` Django setting
        (dotted import path). Falls back to the built-in class.

        Returns:
            Shared TemplateRenderer instance.
        """
        global _default_renderer
        if _default_renderer is None:
            try:
                from django.conf import settings
                renderer_path = getattr(settings, "OSOUL_TEMPLATE_RENDERER", None)
                if renderer_path:
                    from django.utils.module_loading import import_string
                    _default_renderer = import_string(renderer_path)()
                else:
                    _default_renderer = cls()
            except Exception:
                _default_renderer = cls()
        return _default_renderer
