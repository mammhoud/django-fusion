"""Public schema URLconf — served when no tenant is resolved.

django-tenants uses this URLconf for requests that don't match a tenant
domain (e.g. the bare ``dev.structa.cloud`` root).  With path-based routing
this means any request that does NOT start with ``/t/<tenant>/``.

Routes here serve the tenant directory, registration flow, and the public
landing page.  Everything else is gated behind a tenant path."""

from django.urls import include, path

urlpatterns = [
    # Tenant registry + registration (public)
    path("", include("apps.tenants.urls")),
]