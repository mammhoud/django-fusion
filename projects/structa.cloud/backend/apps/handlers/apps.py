from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HandlersConfig(AppConfig):
    """
    django-fusion views that render the landing pages.

    Each view subclasses ``django_fusion.routes.pages.handler.PageHandler`` so
    every request goes through the unified fragment/layout rendering pipeline:
    an HTMX request gets just the page fragment, a plain request gets the full
    layout (see ``apps/handlers/views.py`` for the mechanism).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.handlers"
    label = "handlers"
    verbose_name = _("Landing page handlers")
