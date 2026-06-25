from django.urls import include, path
from pages.views import (
    tab_view,
    project_detail_view,
    blog_detail_view,
    contact_submit,
    subscribe_view,
)
from pages.portfolio.views import portfolio_search
from pages.blog.views import blog_search

app_name = "pages"

urlpatterns = [
    # HTMX modal endpoints
    path("project/<str:project_id>/", project_detail_view, name="project_detail"),
    path("blog/<int:blog_id>/", blog_detail_view, name="blog_detail"),
    path("contact/submit/", contact_submit, name="contact_submit"),
    path("subscribe/", subscribe_view, name="subscribe"),
    
    path("events/", include(("pages.events.urls", "events"), namespace="events")),

    # Search endpoints (HTMX)
    path("blog/search/", blog_search, name="blog_search"),
    path("portfolio/search/", portfolio_search, name="portfolio_search"),

    # Dynamic Tab endpoints (should be after static ones)
    path("<str:tab_name>/", tab_view, name="tab"),
    
    # Blog app (posts, previews, tracking)
    path("blog/", include(("pages.blog.urls", "blog"))),
    
    # Connect app (newsletter, tracking)
    path("comm/", include("pages.connect.urls")),
]
