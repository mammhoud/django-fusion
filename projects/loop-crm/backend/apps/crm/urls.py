from django.urls import path

from apps.core.api import resource_api

urlpatterns = [
    path("companies/", resource_api, {"resource": "companies"}, name="companies_api"),
    path("contacts/", resource_api, {"resource": "contacts"}, name="contacts_api"),
    path("deals/", resource_api, {"resource": "deals"}, name="deals_api"),
    path("pipelines/", resource_api, {"resource": "pipelines"}, name="pipelines_api"),
]
