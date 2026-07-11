# Health Checks — DF-009

> Source of truth: `src/django_fusion/health/views.py`,
> `src/django_fusion/health/urls.py`.

## Views

| Class | URL | Returns | Status codes |
|-------|-----|---------|--------------|
| `HealthCheckView` | `/health/` (via `health_urlpatterns`) | `{"status": "ok"}` | `200` healthy, `503` unhealthy |
| `DatabaseHealthView` | `/health/db/` | `{"status": "ok"}` / `{"status": <error|degraded>, "error": str(exc)}` | `200` ok, `503` connection failed |
| `AssetsHealthView` | `/health/assets/` | similar per-checks pattern | `200` ok, `503` missing |

## Wiring

```python
# urls.py
from django_fusion.health.urls import health_urlpatterns

urlpatterns = [
    # ...
    path("health/", include((health_urlpatterns, "health"))),
]
```

or inline:

```python
from django_fusion.health.views import (
    HealthCheckView, DatabaseHealthView, AssetsHealthView,
)

urlpatterns = [
    path("health/",        HealthCheckView.as_view(),   name="health"),
    path("health/db/",     DatabaseHealthView.as_view(), name="health-db"),
    path("health/assets/", AssetsHealthView.as_view(),  name="health-assets"),
]
```

## Response shape (JSON)

The default view responses are intentionally minimal — per
`src/django_fusion/health/views.py`:

Healthy:

```json
{"status": "ok"}
```

Unhealthy (single-check failure):

```json
{"status": "degraded", "error": "could not connect to server"}
```

> Remark: anything richer (per-check timings, component versions,
> dependency graphs) is the responsibility of the importing site's
> health view, not django-fusion's defaults.

HTTP `503 Service Unavailable` when **any** check fails; `200 OK` when
all pass.

## Docker

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:8000/health/ || exit 1
```

## Kubernetes

```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 15
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/db/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 2
```

## Authentication

By default the health endpoints are **unauthenticated** so probes work.
If your deployment must hide them, gate behind a header check:

```python
from django_fusion.health.views import HealthCheckView
from django.http import HttpResponseForbidden
from django.urls import path

class ProbedHealthCheckView(HealthCheckView):
    def dispatch(self, request, *args, **kwargs):
        token = request.headers.get("X-Probe-Token")
        if token != settings.HEALTHCHECK_TOKEN:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

urlpatterns = [path("health/", ProbedHealthCheckView.as_view())]
```

## Cross-references

- [DF-007 Configuration](./07-configuration.md) — middleware ordering
- [DF-014 FAQ](./14-faq.md) — common health-check failures
