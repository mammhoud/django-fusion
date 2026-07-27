"""
URL patterns for the products plugin (cart & checkout).

Include in the root URL config:
    path("", include("apps.pages.products.urls", namespace="products")),
"""

from django.urls import path

from .views.cart import (
    CartAddItemView,
    CartCountView,
    CartRemoveItemView,
    CartSubtotalView,
    CartUpdateQuantityView,
    CartView,
    CheckoutView,
)

app_name = "products"

urlpatterns = [
    # Cart
    path("cart/",                              CartView.as_view(),               name="cart"),
    path("cart/count/",                        CartCountView.as_view(),          name="cart-count"),
    path("cart/subtotal/",                     CartSubtotalView.as_view(),       name="cart-subtotal"),
    path("cart/add/",                          CartAddItemView.as_view(),        name="cart-add"),
    path("cart/update/<str:item_id>/",         CartUpdateQuantityView.as_view(), name="cart-update"),
    path("cart/remove/<str:item_id>/",         CartRemoveItemView.as_view(),     name="cart-remove"),
    # Checkout
    path("checkout/",                          CheckoutView.as_view(),           name="checkout"),
]
