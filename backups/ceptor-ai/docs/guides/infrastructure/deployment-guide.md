# Structa Cloud Deployment Guide

**Version:** 1.0.0  
**Last Updated:** July 5, 2026  
**Status:** Production

---

## Table of Contents

1. [Infrastructure Overview](#infrastructure-overview)
2. [Project Structure](#project-structure)
3. [Docker Deployment](#docker-deployment)
4. [Proxy & SSL Configuration](#proxy--ssl-configuration)
5. [Django Site Setup](#django-site-setup)
6. [Common Commands](#common-commands)
7. [Troubleshooting](#troubleshooting)

---

## Infrastructure Overview

### Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TRAEFIK PROXY (443/80)                  │
│              (default-proxy container, Traefik 3.7.6)       │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┼────────┬──────────────┐
       │       │        │              │
       v       v        v              v
    ┌──────────────┐ ┌──────────────┐ ┌─────────────┐
    │ CTC Research │ │  VResume     │ │  Structa    │
    │   Website    │ │    Website   │ │ LMS Demo    │
    │ (gunicorn    │ │ (gunicorn    │ │ (gunicorn   │
    │  5070)       │ │  5072)       │ │  5071)      │
    └──────────────┘ └──────────────┘ └─────────────┘
       │                 │                  │
       └─────────┬───────┴──────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
        v                  v
    ┌──────────┐      ┌──────────┐
    │PostgreSQL│      │  Redis   │
    │ (5432)   │      │ (6379)   │
    └──────────┘      └──────────┘
```

### Core Services

| Service | Container | Port | Status | Purpose |
|---------|-----------|------|--------|---------|
| Traefik Proxy | `default-proxy` | 80, 443, 8080 | ✅ Healthy | HTTPS reverse proxy, SSL termination |
| CTC Research | `ctc-research-website` | 5070 | ✅ Healthy | Django app (gunicorn) |
| VResume | `vresume-web` | 5072 | ✅ Healthy | Django app (gunicorn) |
| LMS Demo | `lms-web` | 5071 | ✅ Healthy | Django app (gunicorn) |
| PostgreSQL | `postgres` | 5432 | ✅ Healthy | Primary database |
| Redis | `default-redis` | 6379 | ✅ Healthy | Cache & session store |
| Nginx Media | `shared-media` | 80 | ✅ Healthy | Static/media file server |

---

## Project Structure

### Root Layout

```
/home/structa.cloud/
├── .git/                          # Git repository
├── .github/                       # GitHub Actions workflows
├── applications/                  # Main Django monorepo (see below)
├── proxy/                         # Traefik proxy configuration
├── databases/                     # Database containers (PostgreSQL)
├── docs/                          # Project documentation
├── Makefile                       # Root-level task delegation
├── CHANGELOG.md                   # Version history
├── DEPLOYMENT_GUIDE.md            # This file
└── docker-compose.yml             # Multi-container orchestration
```

### Applications Monorepo Structure

```
/home/structa.cloud/applications/
├── Makefile                       # Main dispatcher for all Django tasks
├── pyproject.toml                 # Workspace-level Python config
├── uv.lock                        # Frozen dependency lock file
├── manage.py                      # Django management entry point
├── configs/                       # Shared Django configuration
│   ├── base/                      # Base settings modules
│   ├── settings/                  # Environment-specific settings
│   └── tests/                     # Test configuration
├── assets/                        # Shared frontend assets
│   ├── static/                    # Shared static files
│   ├── templates/                 # Shared Wagtail templates
│   ├── scripts/                   # Build/automation scripts
│   └── locale/                    # Localization files
├── libs/                          # Local reusable Django libraries
│   ├── django-fusion/             # Core framework (Wagtail, views, routing)
│   └── ceptor-ai/                 # AI/content models
├── tasks/                         # Shared task runners
├── webpack/                       # Webpack build configuration
│
├── ctc-research/                  # CTC Research site
│   ├── Makefile                   # Site-specific tasks
│   ├── www/                       # Django apps
│   ├── plugins/                   # Site plugins (blog, lms, accounts, etc.)
│   ├── templates/                 # Site-specific templates
│   ├── assets/                    # Site-specific assets
│   └── settings.py                # Site configuration
│
├── lms-demo/                      # LMS Demo site
│   ├── Makefile
│   ├── www/
│   ├── plugins/
│   └── templates/
│
├── VResume/                       # VResume site (capitalized)
│   ├── Makefile
│   ├── www/
│   ├── plugins/
│   └── templates/
│
└── customizer/                    # CMS customizer app
```

### Proxy Configuration Structure

```
/home/structa.cloud/proxy/
├── Dockerfile                     # Traefik container image
├── docker-compose.traefik.yml     # Traefik compose file
├── .env                           # Cloudflare credentials (gitignored)
├── .env.example                   # Env template
├── acme/
│   ├── .gitkeep
│   ├── acme.json                  # Let's Encrypt storage (gitignored)
│   └── backups/                   # ACME backups
├── certs/                         # Static self-signed certs (fallback)
│   ├── ctc-research.crt
│   ├── ctc-research.key
│   ├── structa-cloud.crt
│   └── ...
├── traefik/
│   ├── dynamic.yml                # Static config (global settings, ACME resolvers)
│   └── dynamic/                   # Dynamic router configs (hot-reloaded)
│       ├── ctc-research.yml       # CTC Research routers & services
│       ├── structa-cloud.yml      # Structa Cloud routers & services
│       ├── vresume.yml            # VResume routers & services
│       ├── media-servers.yml      # Shared media server
│       ├── middlewares.yml        # Traefik middlewares
│       ├── dashboard.yml          # Traefik dashboard
│       ├── certs.yml              # Static TLS certs (fallback)
│       └── catchall.yml           # Catchall router for unmatched hosts
└── scripts/
    └── manage-certs.sh            # Certificate management script
```

---

## Docker Deployment

### Building & Running

#### Build the CTC Research image

```bash
cd /home/structa.cloud
docker build \
  --build-arg PROJECT_PATH=ctc-research \
  -f compose/Dockerfile \
  -t structa-ctc-research:latest \
  .
```

#### Run containers (recommended: use docker-compose)

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d ctc-research-website

# View logs
docker-compose logs -f ctc-research-website

# Stop services
docker-compose down
```

### Key Environment Variables

| Variable | Example | Purpose |
|----------|---------|---------|
| `PROJECT_PATH` | `ctc-research` | Site subdirectory in applications/ |
| `WEBSITE` | `ctc-research` | Site identifier for Django |
| `DJANGO_SITE` | `ctc-research` | Django site name (used in settings) |
| `DATABASE_URL` | `postgresql://user:pass@postgres:5432/ctc_research_db` | Database connection |
| `REDIS_URL` | `redis://default-redis:6379/0` | Redis connection |
| `DEBUG` | `False` | Django debug mode (always False in production) |
| `ALLOWED_HOSTS` | `ctc-research.com,www.ctc-research.com` | Allowed hostnames |
| `LETSENCRYPT_EMAIL` | `structa.cloud@gmail.com` | LE account email |

---

## Proxy & SSL Configuration

### Let's Encrypt Setup (HTTP-01)

**Status:** ✅ Active for CTC Research

#### Prerequisites
1. DNS A records point to this server (187.77.166.222)
2. Port 80 reachable from internet
3. `proxy/acme/acme.json` exists (mode 0600)

#### Configuration

**File:** `/home/structa.cloud/proxy/traefik/dynamic.yml`

```yaml
certificatesResolvers:
  letsencrypt-http:
    acme:
      email: structa.cloud@gmail.com
      storage: /etc/traefik/acme/acme.json
      caServer: https://acme-v02.api.letsencrypt.org/directory
      httpChallenge:
        entryPoint: web
```

#### Enable for a site

**File:** `/home/structa.cloud/proxy/traefik/dynamic/ctc-research.yml`

```yaml
routers:
  ctc-site-https:
    rule: 'Host(`ctc-research.com`) || Host(`www.ctc-research.com`)'
    entryPoints: [web-secure]
    service: ctc-site-service
    tls:
      certResolver: letsencrypt-http  # ← Enable LE cert
```

#### Verify Certificate

```bash
# Check certificate details
echo | openssl s_client -connect ctc-research.com:443 -servername ctc-research.com 2>/dev/null \
  | openssl x509 -noout -issuer -dates

# Output should show:
# issuer=C = US, O = Let's Encrypt, CN = R3
# notBefore=Jul  5 08:24:41 2026 GMT
# notAfter=Oct  3 08:24:40 2026 GMT
```

### Cloudflare DNS-01 (Alternative)

**Status:** ⚠️ Not configured (requires Cloudflare API token)

If you want to use Cloudflare DNS-01 instead of HTTP-01:

#### 1. Get Cloudflare API Token

- Go to https://dash.cloudflare.com/profile/api-tokens
- Create token with scope: Zone / DNS / Edit
- Restrict to relevant zones

#### 2. Set credentials

**File:** `/home/structa.cloud/proxy/.env`

```
CF_DNS_API_TOKEN=your_token_here
LETSENCRYPT_EMAIL=structa.cloud@gmail.com
```

#### 3. Enable in static config

**File:** `/home/structa.cloud/proxy/traefik/dynamic.yml`

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: structa.cloud@gmail.com
      storage: /etc/traefik/acme/acme.json
      caServer: https://acme-v02.api.letsencrypt.org/directory
      dnsChallenge:
        provider: cloudflare
        delayBeforeCheck: 30
```

#### 4. Update routers to use it

```yaml
tls:
  certResolver: letsencrypt  # DNS-01 resolver
```

#### 5. Restart proxy

```bash
docker restart default-proxy
```

### Self-Signed Fallback Certs

**Status:** ✅ Active (fallback only)

If Let's Encrypt fails, Traefik falls back to self-signed certs in `proxy/traefik/dynamic/certs.yml`:

```yaml
tls:
  certificates:
    - certFile: /etc/traefik/certs/ctc-research.crt
      keyFile: /etc/traefik/certs/ctc-research.key
```

---

## Django Site Setup

### Database

#### Initialize

```bash
# Run migrations
docker exec ctc-research-website python manage.py migrate

# Create superuser
docker exec ctc-research-website python manage.py createsuperuser
# Username: admin
# Password: (set securely)
# Email: admin@ctc-research.com
```

#### Backup

```bash
# Dump database
docker exec postgres pg_dump -U structa_user ctc_research_db > backup.sql

# Restore
docker exec -i postgres psql -U structa_user ctc_research_db < backup.sql
```

### Wagtail

#### Create HomePage

```bash
docker exec ctc-research-website python manage.py shell <<EOF
from www.core.content.models.pages.home import HomePage
from wagtail.models import Site, Locale

# Create HomePage
locale = Locale.objects.get(language_code='en')
home = HomePage(title='Home', slug='home', live=True, locale=locale)

# Add to root
root = Page.objects.get(depth=1)
root.add_child(instance=home)

# Set as site root
site = Site.objects.get(is_default_site=True)
site.root_page = home
site.hostname = 'ctc-research.com'
site.save()

print('✅ HomePage created and configured')
EOF
```

#### Access Admin

```
https://ctc-research.com/admin/
Username: admin
Password: (your password)
```

---

## Common Commands

### Docker

```bash
# View all containers
docker ps -a

# View container logs
docker logs ctc-research-website --tail 50 -f

# Execute command in container
docker exec ctc-research-website python manage.py check

# Restart container
docker restart ctc-research-website

# Stop & remove containers
docker-compose down

# Remove volumes too (WARNING: deletes data)
docker-compose down -v
```

### Django Management

```bash
# Check configuration
docker exec ctc-research-website python manage.py check

# Run migrations
docker exec ctc-research-website python manage.py migrate

# Create superuser
docker exec ctc-research-website python manage.py createsuperuser

# Load fixtures
docker exec ctc-research-website python manage.py loaddata fixture.json

# Django shell
docker exec -it ctc-research-website python manage.py shell

# Collect static files
docker exec ctc-research-website python manage.py collectstatic --noinput
```

### Make (Recommended)

```bash
# Run all tests
make test

# Lint & format code
make lint

# Build assets
make webpack

# Database checks
make check-db

# Migrate
make migrate

# See all targets
make help
```

### Proxy Management

```bash
# View Traefik dashboard
# https://localhost:8080/dashboard/ (local only, behind firewall)

# Check certificate status
echo | openssl s_client -connect ctc-research.com:443 -servername ctc-research.com 2>/dev/null | openssl x509 -noout -dates

# Check Let's Encrypt store
cat /home/structa.cloud/proxy/acme/acme.json | python3 -m json.tool | grep -A 10 'ctc-research'

# Restart proxy to reload configs
docker restart default-proxy

# View proxy logs
docker logs default-proxy -f --tail 50
```

---

## Troubleshooting

### Site Returns "This site can't be reached"

**Cause:** DNS not pointing to server or firewall blocking.

**Solution:**
```bash
# Check DNS
dig ctc-research.com

# Should return: 187.77.166.222 (this server's IP)
# If not, update A records at your DNS provider (Hostinger, Cloudflare, etc.)

# Test connectivity
curl -v http://ctc-research.com/
# Should get 301 redirect to https://
```

### SSL Certificate Error (ERR_CERT_AUTHORITY_INVALID)

**Cause:** Using self-signed cert (Let's Encrypt failed).

**Solution:**
1. Check if LE challenge is working:
   ```bash
   docker logs default-proxy | grep -i "acme\|challenge"
   ```
2. Verify DNS is correct:
   ```bash
   dig ctc-research.com
   ```
3. Check port 80 is accessible:
   ```bash
   curl -v http://ctc-research.com/
   ```
4. If still failing, Traefik will auto-retry next request after 5 minutes

### Site Serves "Placeholder Page"

**Cause:** HomePage template not rendering (missing django-fusion library or empty content).

**Solution:**
```bash
# Verify django-fusion is installed
docker exec ctc-research-website python -c "import django_fusion; print('✅ Installed')"

# If missing, install it
docker exec ctc-research-website uv pip install -e /app/libs/django-fusion

# Verify HomePage has content in admin
https://ctc-research.com/admin/pages/
```

### Gunicorn Crashes / 502 Bad Gateway

**Cause:** Application error or out of memory.

**Solution:**
```bash
# Check logs
docker logs ctc-research-website | tail -100

# Check container resource usage
docker stats ctc-research-website

# Restart container
docker restart ctc-research-website

# If persistent, increase memory in docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 1G
```

### Database Connection Fails

**Cause:** PostgreSQL down or incorrect credentials.

**Solution:**
```bash
# Check PostgreSQL status
docker ps | grep postgres

# Check logs
docker logs postgres | tail -50

# Verify credentials in settings
docker exec ctc-research-website python manage.py check

# Test connection
docker exec postgres psql -U structa_user -d ctc_research_db -c "SELECT 1"
```

### Static Files / Images Not Loading

**Cause:** Media server not running or Nginx routing misconfigured.

**Solution:**
```bash
# Check shared-media container
docker ps | grep shared-media

# Check Nginx logs
docker logs shared-media

# Verify static files collected
docker exec ctc-research-website python manage.py collectstatic --dry-run

# Collect if missing
docker exec ctc-research-website python manage.py collectstatic --noinput
```

### Let's Encrypt Rate Limit Hit

**Error:** `too many certificates already issued for exact set of domains`

**Solution:**
1. Switch to staging CA temporarily:
   ```yaml
   # In dynamic.yml
   caServer: https://acme-staging-v02.api.letsencrypt.org/directory
   ```
2. Delete/backup acme.json:
   ```bash
   mv /home/structa.cloud/proxy/acme/acme.json /home/structa.cloud/proxy/acme/acme.json.backup
   touch /home/structa.cloud/proxy/acme/acme.json
   chmod 600 /home/structa.cloud/proxy/acme/acme.json
   ```
3. Restart and test:
   ```bash
   docker restart default-proxy
   curl https://ctc-research.com/  # This will trigger a new cert request
   ```
4. Once working on staging, flip back to production CA

---

## Useful Resources

- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Let's Encrypt DNS-01](https://doc.traefik.io/traefik/https/acme/#dnschallenge)
- [Wagtail Documentation](https://docs.wagtail.org/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

---

## Support

For issues or questions:
1. Check logs: `docker logs <container-name>`
2. Review this guide's Troubleshooting section
3. Check CHANGELOG.md for recent changes
4. Run diagnostic checks: `make check-health`
