"""Health-check endpoint for Django deployments.

Provides a lightweight ``/health/`` view that returns ``200 OK`` with a JSON
payload listing database, cache, and custom check results. Integrates with
Docker HEALTHCHECK, Kubernetes liveness probes, and CI smoke tests.

Usage — add to root URLs::

    from django_fusion.health import urls as health_urls
    urlpatterns += [path("health/", include(health_urls))]
"""

from .views import AssetsHealthView, DatabaseHealthView, HealthCheckView  # noqa: F401
