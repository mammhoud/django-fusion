"""
Test URL configuration for blog app tests.
Wraps blog URLs with the 'blog' namespace and includes fusion routable component routes.
"""
from django.contrib import admin
from django.urls import include, path


def _get_fusion_urls():
    """Lazily build fusion site URLs to avoid import-time side effects."""
    try:
        from django_fusion.comp.routes import Application, Site

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
        print(f"Warning: Could not build fusion URLs: {e}", file=sys.stderr)
        return ([], "test")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("apps.blog.urls", namespace="blog")),
    path("fusion/", include(_get_fusion_urls())),
]
