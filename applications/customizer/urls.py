from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("customizer/", include("customizer.site")),
    path("", include("chat.urls")),  # Chat becomes the root
]
