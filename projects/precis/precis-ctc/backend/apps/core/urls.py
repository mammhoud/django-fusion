# Cart endpoints — wired via i18n_patterns(path("cart/", include("apps.core.urls", namespace="cart")))
# in www/urls.py.

from django.urls import path

from apps.pages.products.views.cart import (
    CartAddItemView,
    CartCountView,
    CartRemoveItemView,
    CartSubtotalView,
    CartUpdateQuantityView,
    CartView,
    CheckoutView,
)

app_name = "cart"


urlpatterns = [
    # Cart endpoints — wired as i18n_patterns(path("cart/", include("apps.core.urls", namespace="cart")))
    path("count/", CartCountView.as_view(), name="cart-count"),
    path("items/", CartView.as_view(), name="cart-items"),
    path("subtotal/", CartSubtotalView.as_view(), name="cart-subtotal"),
    path("update/<str:item_id>/", CartUpdateQuantityView.as_view(), name="cart-update-quantity"),
    path("remove/<str:item_id>/", CartRemoveItemView.as_view(), name="cart-remove-item"),
    path("add/", CartAddItemView.as_view(), name="cart-add-item"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]

