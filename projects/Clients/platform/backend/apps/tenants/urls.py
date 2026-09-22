"""Course Center URL routes — registration + directory (public schema)."""

from django.urls import path

from . import api

urlpatterns = [
    path("apis/plans/", api.plan_list, name="center_plan_list"),
    path("apis/centers/", api.center_list, name="center_list"),
    path(
        "apis/centers/check-subdomain/",
        api.check_subdomain,
        name="center_check_subdomain",
    ),
    path(
        "apis/centers/register/",
        api.center_register,
        name="center_register",
    ),
    path(
        "apis/centers/verify/<uuid:token>/",
        api.center_verify,
        name="center_verify",
    ),
]