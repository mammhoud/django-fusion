"""
Wagtail admin hooks for django_fusion.

This module registers Wagtail snippets for email template management
in the Wagtail admin interface.

Classes:
    AuthEmailTemplateViewSet: Snippet view set for AuthEmailTemplate.
    AuthEmailSnippetGroup: Group for auth and email snippets.

Usage in Wagtail settings::

    WAGTAIL_HOOKS_MODULE = "django_fusion.contrib.admin.wagtail_hooks"
"""

from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import AuthEmailTemplate


class AuthEmailTemplateViewSet(SnippetViewSet):
    model = AuthEmailTemplate
    icon = "mail"
    menu_label = _("Email Templates")
    list_display = ["template_type", "subject", "is_active"]
    list_filter = ["template_type", "is_active"]
    search_fields = ["subject"]
    # Explicit name prevents KeyError on URL reversal when app_label differs
    name = "auth_email_template"


class AuthEmailSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Auth & Email")
    menu_icon = "lock"
    menu_order = 300
    items = (AuthEmailTemplateViewSet,)


register_snippet(AuthEmailSnippetGroup)
