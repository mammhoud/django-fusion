# 🔧 Backend Environment

> Per-site environment configuration, settings layering, and env var reference for all Structa Cloud Django projects.

---

## Settings Layering

Each Django project loads settings in this order (later overrides earlier):

```
1. projects/configs/base/*.py        # Shared base settings
2. projects/<site>/configs/settings.yml  # Dynaconf default
3. projects/<site>/configs/settings.development.yml  # Dev overrides
4. projects/<site>/configs/settings.production.yml   # Prod overrides
5. Environment variables (.env)      # Secrets, tokens
```

---

## Per-Site Environment Vars

### LMS (`projects/lms/`)

```bash
DB_NAME_LMS=db_lms
ALLOWED_HOSTS=lms.structa.cloud,localhost,127.0.0.1
SITE_ID=2
DJANGO_SETTINGS_MODULE=configs.settings.lms
```

### Portfolio (`projects/portfolio/`)

```bash
DB_NAME_VRESUME=db_vresume
ALLOWED_HOSTS=vresume.structa.cloud,localhost,127.0.0.1
SITE_ID=3
DJANGO_SETTINGS_MODULE=configs.settings.portfolio
```

### Cypercloud (`projects/cypercloud/`)

```bash
DB_NAME_CYPERCLOUD=db_cypercloud
ALLOWED_HOSTS=cypercloud.structa.cloud,localhost,127.0.0.1
SITE_ID=4
DJANGO_SETTINGS_MODULE=configs.settings.cypercloud
OLLAMA_HOST=http://ollama:11434
OPENAI_API_KEY=sk-...
```

### CTC Research (`projects/precis-ctc/`)

```bash
DB_NAME_CTC=db_ctc
ALLOWED_HOSTS=ctc-research.com,www.ctc-research.com,localhost,127.0.0.1
SITE_ID=1
```

---

## Shared Infrastructure Env Vars

```bash
# Postgres (shared cluster)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres

# Traefik
CF_DNS_API_TOKEN=<cloudflare-token>

# GitHub (for make push)
github=ghp_...   # or GITHUB_TOKEN=...
```

---

## Settings Files Reference

| File | Scope | Example |
|------|-------|---------|
| `projects/configs/base/settings.py` | All sites | INSTALLED_APPS, MIDDLEWARE |
| `projects/configs/base/templates.py` | All sites | TEMPLATES_DIRS order |
| `<site>/configs/settings.yml` | Per-site | Dynaconf default config |
| `<site>/configs/settings.development.yml` | Per-site dev | Debug mode, SQLite |
| `<site>/configs/settings.production.yml` | Per-site prod | PostgreSQL, secure cookies |

---

## Adding a New Site

1. Create `projects/<site>/configs/settings.yml`
2. Add `DB_NAME_<SITE>` in root `.env`
3. Register in `projects/configs/settings/`
4. Add to `projects/Makefile` WEBSITE alias
5. Add Traefik router in `applications/proxy/configs/traefik/dynamic/`

---

## Related

| Topic | Path |
|-------|------|
| Infrastructure | [`../infrastructure/`](../infrastructure/) |
| Per-project config | [`../projects/`](../projects/) |
| Deployment guide | [`../guides/04-deploy.md`](../guides/04-deploy.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
