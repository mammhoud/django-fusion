from django.urls import path

from apps.billing import views

urlpatterns = [
    path("billing/checkout/", views.checkout, name="billing_checkout"),
    path("billing/portal/", views.portal, name="billing_portal"),
    path("billing/webhook/stripe/", views.webhook, name="billing_webhook"),
    path("apis/billing/plans/", views.plans_api, name="billing_plans_api"),
    path("apis/billing/account/", views.account_api, name="billing_account_api"),
]
