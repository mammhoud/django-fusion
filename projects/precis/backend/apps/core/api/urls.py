"""Fusion LMS REST API — URL configuration."""

from django.urls import path, register_converter

from django_fusion.routes.core.converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "unislug")

from django_fusion.contrib.api import branding, health

from apps.pages.blog import api as blog
from apps.learning.api import courses, events
from apps.pages.pages import api as pages
from apps.pages.products import api as products

app_name = "api"

urlpatterns = [
    path("health/", health, name="health"),
    path("branding/", branding, name="branding"),
    path("pages/", pages.page_list, name="page_list"),
    path("pages/<unislug:slug>/", pages.page_detail, name="page_detail"),
    path("pages/<unislug:slug>/fragment/", pages.page_fragment, name="page_fragment"),
    path("pages/<unislug:slug>/data/", pages.page_data, name="page_data"),
    # Courses
    path("courses/", courses.list_courses, name="courses_list"),
    path("courses/filters/", courses.course_filters, name="courses_filters"),
    path("courses/<unislug:slug>/", courses.course_detail, name="courses_detail"),
    # Events
    path("events/", events.list_events, name="events_list"),
    path("events/upcoming/", events.upcoming_events, name="events_upcoming"),
    # Event model uses a UUID primary key (fixture pks are UUIDs), so the
    # detail converter must accept non-integer keys.
    path("events/<str:pk>/", events.event_detail, name="events_detail"),
    # Blog
    path("blog/", blog.list_blog_posts, name="blog_list"),
    path("blog/categories/", blog.blog_categories, name="blog_categories"),
    path("blog/tags/", blog.blog_tags, name="blog_tags"),
    path("blog/<unislug:slug>/", blog.blog_post_detail, name="blog_detail"),
    # Products
    path("products/", products.list_products, name="products_list"),
]
