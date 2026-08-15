from django.contrib import admin

from .models import Cart, CartItem, Category, Order, OrderItem, Product, PromoCode


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "glyph", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_available",
        "is_featured",
        "sort_order",
    )
    list_filter = ("category", "is_available", "is_featured")
    list_editable = ("price", "is_available", "is_featured", "sort_order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")
    autocomplete_fields = ("category",)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "item_count", "subtotal", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "reference",
        "customer_name",
        "order_type",
        "payment_method",
        "status",
        "total",
        "created_at",
    )
    list_filter = ("status", "order_type", "payment_method", "created_at")
    search_fields = ("reference", "customer_name", "customer_email")
    readonly_fields = (
        "reference",
        "subtotal",
        "discount",
        "tax",
        "total",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (None, {"fields": ("reference", "status", "order_type", "payment_method")}),
        ("Customer", {"fields": ("customer_name", "customer_email", "customer_phone")}),
        (
            "Fulfilment",
            {
                "fields": (
                    "ready_at",
                    "table_number",
                    "delivery_address",
                    "delivery_city",
                    "delivery_zip",
                )
            },
        ),
        ("Totals", {"fields": ("subtotal", "discount", "tax", "total")}),
        ("Promo", {"fields": ("promo_code",)}),
        ("Notes", {"fields": ("notes",)}),
    )
    inlines = [OrderItemInline]


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "value",
        "is_active",
        "used_count",
        "max_uses",
    )
    list_filter = ("discount_type", "is_active")
    list_editable = ("is_active", "value")
    search_fields = ("code",)
