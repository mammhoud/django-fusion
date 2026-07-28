# Health Check Integration

Status: Planned

Summary: Spec for integrating the `django_fusion.health` module's health check endpoints across all sites. Covers Docker HEALTHCHECK configuration, Kubernetes liveness/readiness probes, Traefik health check routing, and monitoring dashboard integration for each site (CTC Research, LMS Demo, VResume).

## What Will Replace This Page
- Docker HEALTHCHECK commands per site using `HealthCheckView`
- Kubernetes probe YAML examples mapping to `DatabaseHealthView` and `AssetsHealthView`
- Traefik healthCheck configuration snippets with correct Host headers
- JSON response contract documentation for each health view
