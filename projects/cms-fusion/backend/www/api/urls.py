"""CMS Fusion REST API — URL configuration."""

from django.urls import path

from . import blog, courses, fusion_health, pages, products

app_name = "api"

urlpatterns = [
    path("fusion/health", fusion_health.fusion_health, name="fusion_health"),
    path("pages/", pages.page_list, name="page_list"),
    path("pages/<slug:slug>/", pages.page_detail, name="page_detail"),
    path("pages/<slug:slug>/fragment/", pages.page_fragment, name="page_fragment"),
    path("pages/<slug:slug>/data/", pages.page_data, name="page_data"),
    # Courses
    path("courses/", courses.list_courses, name="courses_list"),
    path("courses/filters", courses.course_filters, name="courses_filters"),
    path("courses/<slug:slug>", courses.course_detail, name="courses_detail"),
    # Blog
    path("blog/", blog.list_blog_posts, name="blog_list"),
    path("blog/categories", blog.blog_categories, name="blog_categories"),
    path("blog/tags", blog.blog_tags, name="blog_tags"),
    path("blog/<slug:slug>", blog.blog_post_detail, name="blog_detail"),
    # Products
    path("products/", products.list_products, name="products_list"),
]
