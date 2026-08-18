# Precis LMS — Configuration

> Environment variables, settings, and deployment configuration.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DJANGO_SETTINGS_MODULE` | `settings` | Settings module path |
| `DJANGO_SITE` | `precis` | Site identifier |
| `DJANGO_ALLOWED_HOSTS` | `*` | Allowed hostnames |
| `DB_NAME` | `db_precis` | Database name |
| `DB_USER` | — | Database user |
| `DB_PASSWORD` | — | Database password |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `STRIPE_API_KEY` | — | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | — | Stripe public key |
| `FUSION_RENDER_FIRST_DEFAULT` | `True` | Default render mode |

---

## Settings (Dynaconf)

Configuration uses Dynaconf YAML files under `Env/`:

```yaml
# Env/_site.yml
sites:
  precis:
    domain: lms.structa.cloud
    db_name: db_precis
    port: 8073
```

---

## Quick Commands

```bash
cd projects/precis/precis-main/backend

# Check settings
uv run --project ../.. python manage.py diffsettings

# Run checks
uv run --project ../.. python manage.py check

# Migrate
uv run --project ../.. python manage.py migrate
```

---

## Related

- [`README.md`](README.md) — project overview
- [`courses.md`](courses.md) — course models and views
- [`deployment.md`](deployment.md) — Docker deployment
