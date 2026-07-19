# Portfolio — Configuration Reference

> **Domain:** vresume.structa.cloud | **Port:** 5072 | **DB:** PostgreSQL `vresume`

## Site Registration

```yaml
# projects/configs/settings/ENV/sites.yml
sites:
  vresume:
    domain: vresume.structa.cloud
    db_name: vresume
    port: 5072
    path: portfolio
    site_id: 3
```

## Environment Variables

| Variable | Required | Purpose |
|----------|:--------:|---------|
| `DB_NAME_VRESUME` | ✅ | PostgreSQL database name |
| `VRESUME_HOST` | ✅ | Site domain |

## Key Plugins

| Plugin | Path | Purpose |
|--------|------|---------|
| Accounts | `plugins/accounts/adapters.py` | Auth adapters (RegistrationAdapter, SocialAccountAdapter) |
| Blog | `plugins/blog/` | Blog with Wagtail integration |
| Profile | `plugins/profile/` | User profiles with avatar and social auth |

## Shared WWW Worker

See [`projects/lms/shared-integration.md`](../lms/shared-integration.md) — the shared worker stack (`projects/www/worker/`) handles email dispatch (Dramatiq) and scheduled tasks (Celery Beat) identically across all Django sites.

## Related

| Resource | Path |
|----------|------|
| Portfolio README | [`README.md`](README.md) |
| Deployment guide | [`../../guides/04-deploy.md`](../../guides/04-deploy.md) |
| Backend environment | [`../../back-env/`](../../back-env/) |
