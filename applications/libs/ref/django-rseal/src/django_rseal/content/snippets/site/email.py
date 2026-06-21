


from django.utils.translation import gettext_lazy as _

from django_rseal.content.models import EmailSettings

from ..base import BaseSnippetViewSet


class EmailSettingsViewSet(BaseSnippetViewSet):
    """Manage simple Person records via the Wagtail Snippet interface."""

    model = EmailSettings
    menu_label = _("Email Settings")
    icon = "mail"
    menu_order = 200
