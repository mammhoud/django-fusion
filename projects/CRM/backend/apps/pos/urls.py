from django.urls import path

from . import views

urlpatterns = [
    path("ingest/pos/sales/", views.ingest_pos_sales, name="ingest_pos_sales"),
]
