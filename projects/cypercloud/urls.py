from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("customizer/", include("cypercloud.site")),  # Updated: customizer → cypercloud
    path("", include("chat.urls")),  # Chat becomes the root
    # JSON component / template analyzer endpoint (django_fusion.analyzer).
    # POST /api/analyzer/analyze/ with the spec JSON body.
    path("api/analyzer/", include("django_fusion.analyzer.urls")),
] 
