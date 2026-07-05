"""
Test URL configuration for blog app tests.
Wraps blog URLs with the 'blog' namespace and includes osoul routable component routes.
"""
from django.contrib import admin
from django.urls import include, path


def _get_osoul_urls():
    """Lazily build osoul site URLs to avoid import-time side effects."""
    try:
        from django_fusion.web.routes import Application, Site

        from apps.blog.components import BlogPostCreateFragment, BlogPostListFragment

        class BlogApp(Application):
            title = "Blog"
            icon = "article"
            app_name = "blog"

            def has_view_permission(self, user, obj=None):
                return True

        app = BlogApp(viewsets=[BlogPostListFragment(), BlogPostCreateFragment()])
        site = Site(title="Test", viewsets=[app])
        patterns, app_name, namespace = site.urls
        return (patterns, app_name)
    except Exception as e:
        import sys
        print(f"Warning: Could not build osoul URLs: {e}", file=sys.stderr)
        return ([], "test")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("osoul/", include(_get_osoul_urls())),
]
