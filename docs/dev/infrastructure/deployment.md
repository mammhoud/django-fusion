# Infrastructure — Deployment

> **Related Names:** `Docker`, `docker-compose`, `deployment`, `production`, `containers`, `Traefik`, `PostgreSQL`, `Redis`, `health-check`, `backup`
> **Tags:** #deployment #docker #infrastructure #production

```
┌─────────────────────────────────────────────┐
│           TRAEFIK PROXY (443/80)            │
│            (default-proxy container)            │
└──────────────┬────────────────────────────────┘
               │
       ┌───────┼────────┬──────────────┐
       │       │        │              │
       v       v        v              v
    ┌──────────┐  ┌──────────────────┐  ┌──────────┐
    │   CTC    │  │ Precis Main      │  │ VResume  │
    │ Research │  │ unified LMS/site │  │          │
    │ (5070)   │  │ (8074 / 3000)    │  │ (5072)   │
    └──────────┘  └──────────┘  └──────────┘
         │              │             │
         └──────────────┼─────────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              v                   v
         ┌──────────┐       ┌──────────┐
         │PostgreSQL│       │  Redis   │
         │ (5432)   │       │ (6379)   │
         └──────────┘       └──────────┘
```

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| Traefik Proxy | `default-proxy` | 80, 443, 8080 | HTTPS reverse proxy |
| CTC Research | `precis-ctc-website` | 5070 | Django app |
| Precis Main | `precis-main-backend` + `precis-main-frontend` | 8074 / 3000 | Unified Django/Astro app |
| VResume | `vresume-website` | 5072 | Django app |
| PostgreSQL | `postgres` | 5432 | Primary database |
| Redis | `default-redis` | 6379 | Cache & sessions |
| Nginx Media | `shared-proxy` | 80 | Static/media files |

## Current Precis deployment reference

The old `lms-website`/LMS Demo description is retired. `structa.cloud` and
`lms.structa.cloud` are compatibility hosts for
`projects/structa.cloud/`. Deploy and verify it with:

```bash
docker compose --env-file .env \
  -f projects/structa.cloud/docker-compose.yml up -d --build
curl -k -sS -L -o /dev/null \
  -w 'Wagtail: %{http_code} %{url_effective}\n' \
  https://lms.structa.cloud/admin
```

See [`precis-main-proxy-admin.md`](precis-main-proxy-admin.md) for the complete
Traefik contract.

## Project layout

```
/home/structa.cloud/
├── projects/
│   ├── structa.cloud/          # unified Precis LMS + landing
│   ├── precis/precis-landing/       # kept legacy Precis Landing copy
│   ├── precis/precis-ctc/           # standalone CTC Research
│   ├── configs/                     # shared Django configuration
│   └── assets/                      # shared product assets
├── libs/django-fusion/              # shared library submodule
├── application/
│   ├── proxy/                       # Traefik + shared Nginx
│   └── databases/                   # PostgreSQL + Redis Compose
├── docs/                            # authored documentation
└── Makefile                         # root dispatcher
```

## Build and start an application stack

Use the owning product Compose file rather than the retired generic
`projects/compose/Dockerfile` path:

```bash
# Unified Precis
docker compose --env-file .env \
  -f projects/structa.cloud/docker-compose.yml up -d --build

# CTC Research
cd projects/precis/precis-ctc
make redeploy
```

## Start all services

```bash
make deploy
```

Or manually:

```bash
docker compose -f application/databases/docker-compose.yml up -d
docker compose -f application/proxy/docker-compose.yml up -d
cd projects && make docker-up WEBSITE=precis-ctc
```

## Environment variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `PROJECT_PATH` | `precis-ctc` | Site subdirectory in `projects/` |
| `WEBSITE` | `precis-ctc` | Site identifier |
| `DATABASE_URL` | `postgresql://user:pass@postgres:5432/dbname` | Database connection |
| `REDIS_URL` | `redis://default-redis:6379/0` | Redis connection |
| `DEBUG` | `False` | Django debug mode |
| `ALLOWED_HOSTS` | `ctc-research.com,www.ctc-research.com` | Allowed hostnames |

## Database setup

```bash
# Run migrations
docker exec precis-ctc-website python manage.py migrate

# Create superuser
docker exec precis-ctc-website python manage.py createsuperuser

# Backup
docker exec postgres pg_dump -U structa_user ctc_research_db > backup.sql

# Restore
docker exec -i postgres psql -U structa_user ctc_research_db < backup.sql
```

## Common commands

```bash
# View all containers
docker ps -a

# Precis Main logs
docker logs precis-main-backend --tail 50

# CTC logs
docker logs precis-ctc-website --tail 50

# Django checks
docker exec precis-main-backend python manage.py check
docker exec precis-ctc-website python manage.py check

# Collect static for the selected application
docker exec precis-main-backend python manage.py collectstatic --noinput
```

## Troubleshooting

### Site returns "This site can't be reached"

```bash
dig ctc-research.com
curl -v http://ctc-research.com/
```

### SSL certificate error

```bash
docker logs default-proxy | grep -i "acme\|challenge"
echo | openssl s_client -connect ctc-research.com:443 -servername ctc-research.com 2>/dev/null | openssl x509 -noout -dates
```

### 502 Bad Gateway

```bash
docker logs precis-ctc-website | tail -100
docker stats precis-ctc-website
```

### Static files not loading

```bash
docker ps | grep shared-proxy
docker logs shared-proxy
docker exec precis-main-backend python manage.py collectstatic --noinput
```

## Remarks & Notes

- This guide is a cross-product deployment reference; use the owning product
  runbook for exact Compose variables, migrations, seeds, and rollback steps.
- `precis-main` is the current LMS/landing runtime. Historical `lms-website`,
  `precis-lms-*`, and `precis-landing-*` containers are not deployment targets.
- Never print secrets, restore a database, or run `docker compose down --volumes`
  as part of routine deployment troubleshooting.
