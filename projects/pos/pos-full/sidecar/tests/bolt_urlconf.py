"""URL conf used by bolt API tests."""

from django.urls import path

from bolt_api import bolt

urlpatterns = [
    path("bolt/", bolt.urls),
]
