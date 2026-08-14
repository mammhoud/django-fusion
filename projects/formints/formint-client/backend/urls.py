"""FormintC purchase-app URL configuration."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("django-admin/", admin.site.urls),
    # ── Wagtail CMS — editor admin + document library ───────────────────
    # /cms/ hosts the Wagtail admin (Django admin stays on /django-admin/).
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # ── Auth — django-allauth headless API + server-rendered pages ─────
    # Consumed by the Alpine LoginModal on the Astro frontend.
    path("api/auth/", include("allauth.headless.urls")),
    path("accounts/", include("allauth.urls")),
    # ── Shop — storefront data + HTMX cart/checkout fragments ───────────
    path("", include("shop.urls")),
    # ── Employee — staff-only dashboard + order inbox ───────────────────
    path("employee/", include("employee.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Wagtail is deliberately last because it owns the remaining page paths
# (e.g. /about/, /contact/ — CMS-managed pages under the shop storefront).
urlpatterns += [path("", include(wagtail_urls))]
