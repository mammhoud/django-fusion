"""
Test URL configuration for blog app tests.
Wraps blog URLs with the 'blog' namespace and includes routable component routes.
"""
from django.contrib import admin
from django.urls import include, path


def _get_component_urls():
    """Lazily build component site URLs to avoid import-time side effects."""
    try:
        from django_fusion.routes.core.sites import Application, Module
        from plugins.blog.components import BlogPostCreateFragment, BlogPostListFragment

        class BlogApp(Application):
            title = "Blog"
            icon = "article"
            app_name = "blog"

            def has_view_permission(self, user, obj=None):
                return True

        app = BlogApp(viewsets=[BlogPostListFragment(), BlogPostCreateFragment()])
        module = Module(title="Test", viewsets=[app])
        patterns, app_name, namespace = module.urls
        return (patterns, app_name)
    except Exception as e:
        import sys
        print(f"Warning: Could not build component URLs: {e}", file=sys.stderr)
        return ([], "test")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("plugins.blog.urls", namespace="blog")),
    path("components/", include(_get_component_urls())),
]
