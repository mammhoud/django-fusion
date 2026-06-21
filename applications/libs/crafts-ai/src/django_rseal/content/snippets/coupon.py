"""
Coupon SnippetViewSet for Wagtail admin.
Registered via wagtail_hooks.py.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from django_rseal.content.models.coupon import Coupon


class CouponViewSet(SnippetViewSet):
    model = Coupon

    menu_label = _("Coupons")
    menu_icon = "tag"
    menu_order = 350
    add_to_admin_menu = False
    list_display = ["code", "name", "discount_type", "discount_value", "is_active", "times_used", "valid_until"]
    list_filter = ["is_active", "discount_type"]
    search_fields = ["code", "name"]
