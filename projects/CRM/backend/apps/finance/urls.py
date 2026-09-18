from django.urls import path

from apps.core.api import resource_api

from .views import finance_export, revenue_trend_api

urlpatterns = [
    path("invoices/", resource_api, {"resource": "invoices"}, name="invoices_api"),
    path("payments/", resource_api, {"resource": "payments"}, name="payments_api"),
    path("revenue/", resource_api, {"resource": "revenue"}, name="revenue_api"),
    path("revenue/trend/", revenue_trend_api, name="revenue_trend_api"),
    path("finance/export/", finance_export, name="finance_export"),
]
