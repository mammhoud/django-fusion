"""
Landing fragment endpoints.

These routes sit *before* Wagtail's catch-all so HTMX requests (and plain
loads) are served by the django-fusion ``PageHandler`` pipeline instead of
Wagtail's built-in ``serve()`` — giving us the unified fragment/layout
renderer described in ``apps/handlers/views.py``.
"""
from django.urls import path
from django.views.generic import RedirectView

from apps.handlers import views

urlpatterns = [
    path("", views.LandingHomeView.as_view(), name="home"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("about/team/", views.TeamPageView.as_view(), name="about_team"),
    # Company merged into About — legacy URL redirects permanently.
    path("company/", RedirectView.as_view(url="/about/", permanent=True), name="company_redirect"),
    # Projects merged into Products — the catalog carries the repo project
    # grid; the legacy URL redirects permanently.
    path("projects/", RedirectView.as_view(url="/products/", permanent=True), name="projects_redirect"),
    path("services/", views.ServicesPageView.as_view(), name="services"),
    path("pricing/", views.PricingPageView.as_view(), name="pricing"),
    path("blog/", views.BlogPageView.as_view(), name="blog"),
    path("blog/<slug:slug>/", views.BlogPostPageView.as_view(), name="blog_post"),
    path("products/", views.ProductsPageView.as_view(), name="products"),
    path("products/<slug:slug>/", views.ProductPageView.as_view(), name="product"),
    path("products/<slug:slug>/preview/<slug:edition>/", views.ProductPreviewView.as_view(), name="product_preview"),
    path("brand/", views.BrandPageView.as_view(), name="brand"),
    path("features/", views.FeaturesPageView.as_view(), name="features"),
    path("contact/", views.ContactPageView.as_view(), name="contact"),
    path("faq/", views.FaqPageView.as_view(), name="faq"),
    path("privacy/", views.PrivacyPageView.as_view(), name="privacy"),
]
