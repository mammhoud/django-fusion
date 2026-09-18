"""Admin registrations for the products & cart plugin."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline line items shown under each cart."""

    model = CartItem
    extra = 0
    readonly_fields = (
        "product_name",
        "product_description",
        "price",
        "quantity",
        "added_at",
    )
    can_delete = True
    verbose_name = _("Cart Item")
    verbose_name_plural = _("Cart Items")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart browsing: user/session carts with their line items."""

    list_display = ("id", "user", "session_key", "total_items", "total_price", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__email", "user__username", "session_key")
    readonly_fields = ("id", "created_at", "updated_at", "total_items", "total_price")
    inlines = (CartItemInline,)

    fieldsets = (
        (None, {"fields": ("id", "user", "session_key")}),
        (_("Summary"), {"fields": ("total_items", "total_price")}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("Total items"))
    def total_items(self, obj):
        return obj.total_items

    @admin.display(description=_("Total price"))
    def total_price(self, obj):
        return obj.total_price


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Standalone line-item browsing (read-mostly)."""

    list_display = ("product_name", "cart", "quantity", "price", "total_price", "added_at")
    list_filter = ("added_at",)
    search_fields = ("product_name", "product_id", "cart__user__email", "cart__session_key")
    readonly_fields = ("cart", "product_id", "product_name", "product_description", "price", "quantity", "added_at", "total_price")
