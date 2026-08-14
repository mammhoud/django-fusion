from django.urls import path

from apps.core.api import resource_api

from . import views as crm_views

urlpatterns = [
    path("companies/", resource_api, {"resource": "companies"}, name="companies_api"),
    path("contacts/", resource_api, {"resource": "contacts"}, name="contacts_api"),
    path("deals/", resource_api, {"resource": "deals"}, name="deals_api"),
    path("pipelines/", resource_api, {"resource": "pipelines"}, name="pipelines_api"),
    path("board/", crm_views.pipeline_board_api, name="pipeline_board_api"),
    path("deals/<int:pk>/stage/", crm_views.deal_move_api, name="deal_move_api"),
]
