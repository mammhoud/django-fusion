"""CMS Fusion REST API — URL configuration.

Mounted under ``/apis/`` (see www/urls.py).

HTMX action fragments are registered in their related app's ``Application``
viewsets (LMSApp, BlogApp, EventsApp, CoreApp) under each app's own prefix
(e.g. ``/lms/courses/grid/``) — there is no separate ``/actions/`` tree.
"""

from django.urls import path, register_converter

from django_fusion.routes.core.converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "unislug")

from django_fusion.contrib.api import branding, health, layouts

from apps.pages.blog import api as blog
from apps.pages.lms.api import courses
from apps.pages.pages import api as pages
from apps.pages.products import api as products

app_name = "apis"

urlpatterns = [
    path("health/", health, name="health"),
    path("branding/", branding, name="branding"),
    path("layouts/", layouts, name="layouts"),
    path("pages/", pages.page_list, name="page_list"),
    path("pages/<unislug:slug>/", pages.page_detail, name="page_detail"),
    path("pages/<unislug:slug>/fragment/", pages.page_fragment, name="page_fragment"),
    path("pages/<unislug:slug>/data/", pages.page_data, name="page_data"),
    # Courses
    path("courses/", courses.list_courses, name="courses_list"),
    path("courses/filters/", courses.course_filters, name="courses_filters"),
    path("courses/<unislug:slug>/", courses.course_detail, name="courses_detail"),
    # Blog
    path("blog/", blog.list_blog_posts, name="blog_list"),
    path("blog/categories/", blog.blog_categories, name="blog_categories"),
    path("blog/tags/", blog.blog_tags, name="blog_tags"),
    path("blog/<unislug:slug>/", blog.blog_post_detail, name="blog_detail"),
    # Products
    path("products/", products.list_products, name="products_list"),
]
