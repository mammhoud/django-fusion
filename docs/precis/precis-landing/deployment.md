# 🚀 Precis Landing — Deployment Compatibility Note

> **Current runtime:** `projects/structa.cloud/`
> **Legacy source copy:** `projects/precis/precis-landing/`
> **Dispatcher aliases:** `WEBSITE=precis-landing` and `WEBSITE=precis-lms` map to
> the unified Precis Main runtime where supported.

Precis Landing is no longer a separate production container stack. The public
`structa.cloud` router and the `lms.structa.cloud` compatibility router both
send their backend and frontend service URLs to:

- `precis-main-backend:8074`
- `precis-main-frontend:3000`

Use the canonical Precis Main commands from
`projects/structa.cloud/`:

```bash
make validate-local
make deploy-local
make validate-production
make deploy-production
```

The complete Fusion render and Nx command reference is
[`../landing-fusion-render-flow.html`](../landing-fusion-render-flow.html).


- [Precis Main deployment](../deployment.md)
- [Precis Main proxy and admin runbook](../../dev/infrastructure/precis-main-proxy-admin.md)
- [Precis product index](../README.md)

The source-of-truth proxy files are:

```text
application/proxy/configs/traefik/dynamic/precis-landing.yml
application/proxy/configs/traefik/dynamic/lms-fusion.yml
```

## Remarks & Notes

- The router and service identifiers retain historical Precis Landing/LMS
  labels for compatibility, but legacy container URLs must not be restored.
- Edit the canonical Precis Main Compose file and the dynamic proxy files when
  the runtime contract changes; do not add a second legacy deployment path.
- The legacy `projects/precis/precis-landing/` tree is retained as an archive/
  compatibility copy and is not the new product boundary.
