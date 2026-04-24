# type: ignore NOQA
# from __future__ import annotations

from allauth.account.decorators import secure_admin_login

# from allauth.account.views import LoginView, SignupView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.generic.base import TemplateView

from .apps import AccountsConfig
from .site import *

app_name = AccountsConfig.label


urlpatterns = [
    # Cart endpoints (account-level)
    path("cart/count/", CartCountView.as_view(), name="cart-count"),
    path("cart/items/", CartView.as_view(), name="cart-items"),
    path("cart/subtotal/", CartSubtotalView.as_view(), name="cart-subtotal"),
    path("cart/update/<str:item_id>/", CartUpdateQuantityView.as_view(), name="cart-update-quantity"),
    path("cart/remove/<str:item_id>/", CartRemoveItemView.as_view(), name="cart-remove-item"),
    path("cart/add/", CartAddItemView.as_view(), name="cart-add-item"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]

