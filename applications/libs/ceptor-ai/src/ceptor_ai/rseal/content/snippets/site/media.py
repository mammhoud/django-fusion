from django.utils.translation import gettext_lazy as _
from wagtail.documents.models import Document
from wagtail.images.models import Image

from ..base import BaseSnippetViewSet


class DocumentViewSet(BaseSnippetViewSet):
    """Manage simple Person records via the Wagtail Snippet interface."""

    model = Document
    menu_label = _("Documents")
    icon = "site"
    menu_order = 200

class ImageViewSet(BaseSnippetViewSet):
    """Manage simple Person records via the Wagtail Snippet interface."""

    model = Image
    menu_label = _("Images")
    icon = "site"
    menu_order = 200
