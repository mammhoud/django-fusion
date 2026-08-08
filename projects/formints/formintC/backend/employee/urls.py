from django.urls import path

from . import views

app_name = "employee"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("fragments/orders/", views.orders_fragment, name="orders_fragment"),
    path("fragments/stats/", views.stats_fragment, name="stats_fragment"),
    path("orders/<int:order_id>/status/", views.order_status, name="order_status"),
]
