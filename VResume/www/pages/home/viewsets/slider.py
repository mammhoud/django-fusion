from django.utils.translation import gettext_lazy as _
from core.snippets import BaseSnippetViewSet
from pages.home.models import Slider


class SliderViewSet(BaseSnippetViewSet):
    model = Slider
    icon = "image"
    menu_label = _("Sliders")
    menu_order = 100
