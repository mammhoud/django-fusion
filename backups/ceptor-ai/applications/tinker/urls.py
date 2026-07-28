from django.contrib import admin
from django.urls import path, include
from django_fusion.health import AssetsHealthView, DatabaseHealthView, HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("customizer/", include("tinker.site")),  # Updated: customizer → tinker
    path("", include("chat.urls")),  # Chat becomes the root
    # JSON component / template analyzer endpoint (django_fusion.comp.analyzer).
    # POST /api/analyzer/analyze/ with the spec JSON body.
    path("api/analyzer/", include("django_fusion.comp.analyzer.urls")),
    # ── Standard health-check URLs (mirrors VResume / ctc-research / lms-demo / crm) ──
    path("health/", HealthCheckView.as_view(), name="health"),
    path("assets/health/", AssetsHealthView.as_view(), name="assets-health"),
    path("health/database/", DatabaseHealthView.as_view(), name="health-database"),
] 
