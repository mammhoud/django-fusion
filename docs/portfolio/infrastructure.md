# 🔧 Portfolio — Infrastructure

> Infrastructure specifics for the Portfolio (VResume) project.

---

## Container

| Property | Value |
|----------|-------|
| Container | `vresume-web` |
| Internal Port | `5072` |
| Image | Built from `projects/compose/Dockerfile` |
| Health Check | `Host: 127.0.0.1` → `:5072/health/` |
| Network | `common`, `traefik-net` |

## Deployment

```bash
make deploy-app       # Portfolio starts alongside other Django sites
cd projects && make dev WEBSITE=vresume   # Local dev server
```

## Traefik Router

```yaml
http:
  routers:
    vresume:
      rule: "Host(`vresume.structa.cloud`)"
      service: vresume
      tls:
        certResolver: letsencrypt
  services:
    vresume:
      loadBalancer:
        servers:
          - url: "http://vresume-web:5072"
```

---

## Related

| Topic | Path |
|-------|------|
| Portfolio config | [`configuration.md`](configuration.md) |
| Portfolio use cases | [`use-cases.md`](use-cases.md) |
| Repo overview | [`../../repo-overview.md`](../../repo-overview.md) |
