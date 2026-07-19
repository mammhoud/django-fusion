# 🔧 LMS — Infrastructure

> Infrastructure specifics for the LMS (Learning Management System) project.

---

## Container

| Property | Value |
|----------|-------|
| Container | `lms-web` |
| Internal Port | `5071` |
| Image | Built from `projects/compose/Dockerfile` |
| Health Check | `Host: 127.0.0.1` → `:5071/health/` |
| Network | `common`, `traefik-net` |

## Deployment

```bash
make deploy-app    # LMS starts alongside other Django sites
cd projects && make dev WEBSITE=lms   # Local dev server
```

## Traefik Router

```yaml
# applications/proxy/traefik/dynamic/lms.yml
http:
  routers:
    lms:
      rule: "Host(`lms.structa.cloud`)"
      service: lms
      tls:
        certResolver: letsencrypt
  services:
    lms:
      loadBalancer:
        servers:
          - url: "http://lms-web:5071"
```

## Media

Static/media files served by `shared-media` (Nginx):
- Static: `/var/www/sites/lms/static/`
- Media: `/var/www/sites/lms/media/`

---

## Related

| Topic | Path |
|-------|------|
| LMS config | [`configuration.md`](configuration.md) |
| LMS use cases | [`use-cases.md`](use-cases.md) |
| Shared WWW | [`shared-integration.md`](shared-integration.md) |
| Repo overview | [`../../repo-overview.md`](../../repo-overview.md) |
