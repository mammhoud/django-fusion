"""
Django admin site configuration for django_fusion.

This module provides a custom admin site using Unfold for enhanced
admin interface with better UI/UX and modern design.

Classes:
    AdminSite: Custom admin site using Unfold with custom settings.

Usage in Django settings::

    INSTALLED_APPS = [
        ...
        "unfold",
        "django.contrib.admin",
        "django_fusion.contrib.admin",
    ]

    ADMIN_SITE = "django_fusion.contrib.admin.admin_site.admin_site"
"""

from unfold.sites import UnfoldAdminSite


class AdminSite(UnfoldAdminSite):
    settings_name = "ADMIN_TEMPLATE"


admin_site = AdminSite()


def register(*models, site=admin_site):
    """
    Register the given model(s) classes and wrapped ModelAdmin class with
    admin site:

    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass

    The `site` kwarg is an admin site to use instead of the default admin site.
    """
    from django.contrib.admin import ModelAdmin
    from django.contrib.admin.sites import AdminSite
    from django.contrib.admin.sites import site as default_site

    def _model_admin_wrapper(admin_class):
        if not models:
            raise ValueError("At least one model must be passed to register.")

        admin_site = site or default_site

        if not isinstance(admin_site, AdminSite):
            raise ValueError("site must subclass AdminSite")

        if not issubclass(admin_class, ModelAdmin):
            raise ValueError("Wrapped class must subclass ModelAdmin.")

        admin_site.register(models, admin_class=admin_class)

        return admin_class

    return _model_admin_wrapper
