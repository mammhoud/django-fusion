from django.urls import path

from django_fusion.contrib.api import health, layouts

from . import views

app_name = "shop"

urlpatterns = [
    # Catalog JSON for the Astro frontend
    path("api/catalog/", views.catalog_api, name="catalog_api"),
    path("apis/auth/status/", views.auth_status_api, name="auth_status"),
    # HTMX fragments (django-fusion dual-mode handlers)
    path("shop/fragments/products/", views.products_fragment, name="products_fragment"),
    path("shop/fragments/cart/count/", views.cart_count_fragment, name="cart_count"),
    path("shop/fragments/cart/drawer/", views.cart_drawer_fragment, name="cart_drawer"),
    # Cart actions (HTMX POST)
    path("shop/cart/add/", views.cart_add, name="cart_add"),
    path("shop/cart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("shop/cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    # Checkout + orders
    path("checkout/", views.checkout_page, name="checkout"),
    path("orders/", views.place_order, name="place_order"),
    path("orders/mine/", views.my_orders, name="my_orders"),
    path(
        "orders/<str:reference>/confirmation/",
        views.order_confirmation,
        name="order_confirmation",
    ),
    # django_fusion.contrib.api — shared fusion API helpers
    path("fusion/health/", health, name="fusion_health"),
    path("fusion/layouts/", layouts, name="fusion_layouts"),
    # Branding — settings-driven (django_fusion.contrib.api.branding needs
    # Wagtail, so the purchase app serves its own payload).
    path("fusion/branding/", views.branding, name="fusion_branding"),
    # Fusion render-mode contract
    path("fusion/render-mode/", views.render_mode, name="fusion_render_mode"),
    path("fusion/navigation/", views.navigation, name="fusion_navigation"),
    path("fusion/assets/", views.assets, name="fusion_assets"),
    path("fusion/session-mode/", views.session_mode, name="fusion_session_mode"),
]
