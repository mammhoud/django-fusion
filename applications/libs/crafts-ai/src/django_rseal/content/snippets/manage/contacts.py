from django.utils.translation import gettext_lazy as _

from django_rseal.content.models import Person

from ..base import BaseSnippetViewSet


class PersonViewSet(BaseSnippetViewSet):
    """Manage simple Person records via the Wagtail Snippet interface."""

    model = Person
    menu_label = _("People")
    icon = "user"
    menu_order = 200
