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
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   CTC    │  │  LMS     │  │ VResume  │
    │ Research │  │  Demo    │  │          │
    │ (5070)   │  │ (5071)   │  │ (5072)   │
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
| CTC Research | `ctc-research-website` | 5070 | Django app |
| LMS Demo | `lms-website` | 5071 | Django app |
| VResume | `vresume-website` | 5072 | Django app |
| PostgreSQL | `postgres` | 5432 | Primary database |
| Redis | `default-redis` | 6379 | Cache & sessions |
| Nginx Media | `shared-media` | 80 | Static/media files |

## Project layout

```
/home/structa.cloud/
├── projects/                       # Django monorepo
│   ├── ctc-research/
│   ├── lms/
│   ├── VResume/
│   ├── libs/django-fusion/
│   ├── libs/ceptor-ai/
│   ├── assets/
│   ├── configs/
│   └── www/
├── applications/
│   ├── proxy/                  # Traefik config
│   └── databases/              # Postgres/Redis compose
├── docs/                       # Documentation
├── Makefile                    # Root dispatcher
└── docker-compose.yml
```

## Build a site image

```bash
docker build \
  --build-arg PROJECT_PATH=ctc-research \
  -f projects/compose/Dockerfile \
  -t structa-ctc-research:latest \
  .
```

## Start all services

```bash
make deploy
```

Or manually:

```bash
docker compose -f applications/databases/docker-compose.yml up -d
docker compose -f applications/proxy/docker-compose.yml up -d
cd projects && make docker-up WEBSITE=ctc-research
```

## Environment variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `PROJECT_PATH` | `ctc-research` | Site subdirectory in `projects/` |
| `WEBSITE` | `ctc-research` | Site identifier |
| `DATABASE_URL` | `postgresql://user:pass@postgres:5432/dbname` | Database connection |
| `REDIS_URL` | `redis://default-redis:6379/0` | Redis connection |
| `DEBUG` | `False` | Django debug mode |
| `ALLOWED_HOSTS` | `ctc-research.com,www.ctc-research.com` | Allowed hostnames |

## Database setup

```bash
# Run migrations
docker exec ctc-research-website python manage.py migrate

# Create superuser
docker exec ctc-research-website python manage.py createsuperuser

# Backup
docker exec postgres pg_dump -U structa_user ctc_research_db > backup.sql

# Restore
docker exec -i postgres psql -U structa_user ctc_research_db < backup.sql
```

## Common commands

```bash
# View all containers
docker ps -a

# View logs
docker logs ctc-research-website --tail 50 -f

# Restart a container
docker restart ctc-research-website

# Django check
docker exec ctc-research-website python manage.py check

# Collect static
docker exec ctc-research-website python manage.py collectstatic --noinput
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
docker logs ctc-research-website | tail -100
docker stats ctc-research-website
```

### Static files not loading

```bash
docker ps | grep shared-media
docker logs shared-media
docker exec ctc-research-website python manage.py collectstatic --noinput
```
