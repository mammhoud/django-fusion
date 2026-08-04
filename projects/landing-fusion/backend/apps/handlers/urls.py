"""
Landing fragment endpoints.

These routes sit *before* Wagtail's catch-all so HTMX requests (and plain
loads) are served by the django-fusion ``PageHandler`` pipeline instead of
Wagtail's built-in ``serve()`` — giving us the unified fragment/layout
renderer described in ``apps/handlers/views.py``.
"""
from django.urls import path

from apps.handlers import views

urlpatterns = [
    path("", views.LandingHomeView.as_view(), name="home"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("company/", views.CompanyPageView.as_view(), name="company"),
    path("services/", views.ServicesPageView.as_view(), name="services"),
    path("products/", views.ProductsPageView.as_view(), name="products"),
    path("features/", views.FeaturesPageView.as_view(), name="features"),
    path("projects/", views.ProjectsPageView.as_view(), name="projects"),
    path("contact/", views.ContactPageView.as_view(), name="contact"),
    path("faq/", views.FaqPageView.as_view(), name="faq"),
    path("privacy/", views.PrivacyPageView.as_view(), name="privacy"),
]
