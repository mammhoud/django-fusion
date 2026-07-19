# Infrastructure Reference

**Version:** 1.0.0  
**Last Updated:** July 5, 2026

---

## Network Topology

```
┌────────────────────────────────────────────────────────────────┐
│                          INTERNET                              │
│                  (DNS: ctc-research.com → 187.77.166.222)       │
└────────────────────┬───────────────────────────────────────────┘
                     │
                     │ Port 443 (HTTPS)
                     │ Port 80 (HTTP)
                     │
        ┌────────────▼────────────┐
        │   Traefik Proxy         │
        │ (default-proxy:443/80)  │
        │   Cert Resolver: LE     │
        └────────────┬────────────┘
                     │
        ┌────────────┼────────────┬──────────────┐
        │            │            │              │
        │ HTTP/1.1   │            │              │
        │ Upgrade    │ HTTP/2     │ HTTP/2       │
        │ to HTTPS   │            │              │
        │   301      │            │              │
        │            │            │              │
        v            v            v              v
   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  HTTP   │  │ CTC Res. │  │ VResume  │  │LMS Demo  │
   │Redirect │  │ Gunicorn │  │Gunicorn  │  │Gunicorn  │
   │         │  │  :5070   │  │  :5072   │  │  :5071   │
   └─────────┘  └──────────┘  └──────────┘  └──────────┘
                     │              │            │
                     └──────────────┼────────────┘
                                    │
                      ┌─────────────┼──────────────┐
                      │             │              │
                      v             v              v
                  ┌──────────┐  ┌──────────┐  ┌─────────┐
                  │PostgreSQL│  │  Redis   │  │  Nginx  │
                  │   :5432  │  │  :6379   │  │ Media   │
                  │  (shared)│  │ (shared) │  │  :80    │
                  └──────────┘  └──────────┘  └─────────┘
```

---

## Container Details

### default-proxy (Traefik)

| Property | Value |
|----------|-------|
| **Image** | Custom Dockerfile |
| **Container Name** | `default-proxy` |
| **Ports** | 80 (HTTP), 443 (HTTPS), 8080 (dashboard) |
| **Status** | ✅ Healthy |
| **Health Check** | `curl -f http://localhost:8080/ping` |
| **Volumes** | `/var/run/docker.sock`, `./traefik/dynamic`, `./certs`, `./acme` |
| **Env File** | `./.env` (Cloudflare credentials) |
| **Log Driver** | `json-file` (default) |
| **Memory Limit** | 512M |
| **CPU Limit** | 1 core |

**Key Functions:**
- SSL/TLS termination (Let's Encrypt or self-signed)
- Request routing to backend services
- Automatic redirects (HTTP → HTTPS)
- Middleware chain (compression, CSRF, security headers)
- Health checking backends

---

### ctc-research-website (Django/Gunicorn)

| Property | Value |
|----------|-------|
| **Image** | Built from `projects/compose/Dockerfile` |
| **Container Name** | `ctc-research-website` |
| **Port** | 5070 (internal, not exposed) |
| **Status** | ✅ Healthy |
| **Health Check** | `curl -f http://localhost:5070/health/` |
| **Base Image** | `python:3.11-slim` |
| **Env File** | `.env.dev` (development settings) |
| **Entrypoint** | `/start` (gunicorn server) |
| **Workers** | Auto-calculated (typically 2-4 workers) |
| **Timeout** | 120 seconds |
| **Log Driver** | `json-file` |
| **Memory Limit** | 1GB |
| **CPU Limit** | 1 core |

**Key Functions:**
- Django application server
- Wagtail CMS engine
- Database ORM queries
- Session/cache management (via Redis)

**Configuration:**
```
WEBSITE=ctc-research
DJANGO_SITE=ctc-research
DATABASE_URL=postgresql://user:pass@postgres:5432/ctc_research_db
REDIS_URL=redis://default-redis:6379/0
DEBUG=False
ALLOWED_HOSTS=ctc-research.com,www.ctc-research.com
```

---

### postgres (PostgreSQL)

| Property | Value |
|----------|-------|
| **Image** | `postgres:15-alpine` (custom build) |
| **Container Name** | `postgres` |
| **Port** | 5432 (internal, not exposed) |
| **Status** | ✅ Healthy |
| **Health Check** | `pg_isready -U structa_user` |
| **Log Driver** | `json-file` |
| **Memory Limit** | 512M |
| **Data Directory** | `/var/lib/postgresql/data` (volume mount) |

**Databases:**
- `ctc_research_db` (CTC Research site)
- `lms_demo_db` (LMS Demo site)
- `vresume_db` (VResume site)

**Users:**
- `structa_user` (app user)
- `postgres` (admin user)

---

### default-redis (Redis)

| Property | Value |
|----------|-------|
| **Image** | `redis:7-alpine` |
| **Container Name** | `default-redis` |
| **Port** | 6379 (internal, not exposed) |
| **Status** | ✅ Healthy |
| **Uptime** | 3+ days |
| **Log Driver** | `json-file` |
| **Memory Limit** | 256M |
| **Data Directory** | `/data` (volume mount) |

**Purpose:**
- Session cache
- Task queue (Celery)
- Rate limiting
- General caching

---

### shared-media (Nginx)

| Property | Value |
|----------|-------|
| **Image** | Custom Dockerfile (Nginx) |
| **Container Name** | `shared-media` |
| **Port** | 80 (internal, proxied via Traefik) |
| **Status** | ✅ Healthy |
| **Log Driver** | `json-file` |
| **Volumes** | `/var/www/sites/{ctc-research,vresume,lms}` |

**Purpose:**
- Serve static files (CSS, JS, images)
- Serve user-uploaded media (documents, photos)
- Offload file serving from Django

**Routing (via Traefik):**
```
/static/*  → Nginx → /var/www/sites/{site}/static/
/media/*   → Nginx → /var/www/sites/{site}/media/
```

---

## SSL/TLS Configuration

### Current Setup

**Type:** Let's Encrypt HTTP-01  
**Resolver:** `letsencrypt-http`  
**Email:** `structa.cloud@gmail.com`  
**CA Server:** `https://acme-v02.api.letsencrypt.org/directory`  
**Storage:** `/etc/traefik/acme/acme.json` (in container)  
**Fallback:** Self-signed certs in `/traefik/dynamic/certs.yml`

### Certificate Status

| Domain | Issuer | Valid Until | Auto-Renew |
|--------|--------|-------------|------------|
| ctc-research.com | Let's Encrypt (R3) | Oct 3, 2026 | ✅ Yes |
| www.ctc-research.com | Let's Encrypt (R3) | Oct 3, 2026 | ✅ Yes |
| arch.ctc-research.com | Let's Encrypt (R3) | Oct 3, 2026 | ✅ Yes |
| structa.cloud | Self-signed (fallback) | Jul 4, 2027 | ❌ No |
| vresume.structa.cloud | Self-signed (fallback) | Jul 4, 2027 | ❌ No |

### Certificate Renewal

- **Trigger:** 30 days before expiry
- **Frequency:** Every 60 days (default LE cert lifetime)
- **Automatic:** ✅ Yes (Traefik handles)
- **Downtime:** None (renewal in-place)

---

## DNS Resolution

### Current State

```bash
ctc-research.com        → 187.77.166.222  (A record)
www.ctc-research.com    → 187.77.166.222  (A record via CNAME)
arch.ctc-research.com   → 187.77.166.222  (A record via CNAME)
```

### DNS Provider

| Detail | Value |
|--------|-------|
| **Provider** | Hostinger |
| **Nameservers** | ns1.dns-parking.com, ns2.dns-parking.com |
| **TTL** | 300 seconds (5 minutes) |
| **Update Time** | ~5-15 minutes to propagate |

### Verification

```bash
# Check DNS globally
dig ctc-research.com +short
# Expected: 187.77.166.222

# Check with Google DNS
dig @8.8.8.8 ctc-research.com +short

# Check MX records (if email configured)
dig ctc-research.com MX +short
```

---

## Storage & Volumes

### Named Volumes

```bash
# View all volumes
docker volume ls

# Key volumes:
docker volume inspect structacloud_postgres_data
docker volume inspect structacloud_redis_data
docker volume inspect structacloud_staticfiles
docker volume inspect structacloud_media
```

| Volume | Mount Path | Purpose | Size |
|--------|-----------|---------|------|
| `postgres_data` | `/var/lib/postgresql/data` | Database files | ~500MB |
| `redis_data` | `/data` | Redis snapshots | ~50MB |
| `staticfiles` | `/var/www/sites/*/static/` | CSS, JS, images | ~100MB |
| `media` | `/var/www/sites/*/media/` | User uploads | Variable |

### Bind Mounts

```
/home/structa.cloud/applications/proxy/traefik/dynamic → /etc/traefik/dynamic (Traefik configs)
/home/structa.cloud/applications/proxy/acme → /etc/traefik/acme (Let's Encrypt store)
/home/structa.cloud/applications/proxy/certs → /etc/traefik/certs (Self-signed fallback)
```

### Backup Strategy

**Database:**
```bash
# Full backup
docker exec postgres pg_dump -U structa_user ctc_research_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
docker exec -i postgres psql -U structa_user ctc_research_db < backup.sql

# Automated backup (cron)
0 2 * * * docker exec postgres pg_dump -U structa_user ctc_research_db > /backups/ctc_research_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

**Let's Encrypt Certs:**
```bash
# Backup ACME store
cp -r /home/structa.cloud/applications/proxy/acme/acme.json /home/structa.cloud/applications/proxy/acme/backups/acme_$(date +%Y%m%d_%H%M%S).json

# Traefik will auto-renew within 30 days before expiry
```

**Media & Static:**
```bash
# Backup user uploads
docker run --rm -v structacloud_media:/media -v /backups:/backup ubuntu tar czf /backup/media_$(date +%Y%m%d).tar.gz /media
```

---

## Performance & Resource Allocation

### Container Resources

```yaml
# docker-compose.yml resource limits
default-proxy:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M

ctc-research-website:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
      reservations:
        cpus: '0.5'
        memory: 512M
```

### Monitoring Commands

```bash
# Real-time resource usage
docker stats

# Per-container usage
docker stats ctc-research-website --no-stream

# Memory usage over time
watch -n 1 'docker stats --no-stream | grep ctc-research'

# Disk usage
docker system df

# Top processes in container
docker exec ctc-research-website top -b -n 1
```

### Optimization Tips

1. **Gunicorn Workers:** Typically `2 * CPU_cores + 1` (e.g., 5 for 2-core)
2. **Database Connections:** Set `CONN_MAX_AGE` (default 600s) based on traffic
3. **Redis:** Monitor with `redis-cli MONITOR` and `redis-cli SLOWLOG GET`
4. **Nginx:** Enable gzip compression and browser caching

---

## Security Considerations

### Network Isolation

```
Exposed to Internet:
  ✅ Port 80 (HTTP) — Traefik
  ✅ Port 443 (HTTPS) — Traefik
  ❌ Port 5070 (Django) — NOT exposed
  ❌ Port 5432 (PostgreSQL) — NOT exposed
  ❌ Port 6379 (Redis) — NOT exposed
  ❌ Port 8080 (Traefik dashboard) — Local only
```

### Firewall Rules

```bash
# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS
ufw allow 443/tcp

# Deny Traefik dashboard from external
# (Configure via Traefik auth middleware if exposing)

# Test firewall
sudo ufw status
```

### Secrets Management

```bash
# Keep .env files gitignored
cat .gitignore
# Should contain: applications/proxy/.env, projects/.env

# Store secrets securely
# Do NOT commit: DB passwords, API keys, CSRF tokens

# Rotation
# Change DB password quarterly
# Rotate API tokens annually
```

### TLS/SSL Best Practices

✅ Using Let's Encrypt (trusted CA)  
✅ Auto-renewal (30 days before expiry)  
✅ HTTP → HTTPS redirect  
✅ Security headers (Strict-Transport-Security, X-Frame-Options)  
✅ HSTS preload ready (configure in header)

### Django Security

✅ DEBUG = False  
✅ CSRF protection enabled  
✅ SECURE_SSL_REDIRECT = True  
✅ SECRET_KEY randomized per deployment

---

## Disaster Recovery

### Recovery Procedures

**Database corrupted:**
```bash
# Restore from backup
docker exec -i postgres psql -U structa_user ctc_research_db < backup.sql
docker restart ctc-research-website
```

**Let's Encrypt cert issues:**
```bash
# Restore from backup
cp /home/structa.cloud/applications/proxy/acme/backups/acme_*.json /home/structa.cloud/applications/proxy/acme/acme.json
docker restart default-proxy
```

**Container crashes:**
```bash
# Check logs
docker logs ctc-research-website | tail -100

# Restart
docker restart ctc-research-website

# If persistent, rebuild
docker-compose down
docker-compose up -d ctc-research-website
```

**Full server failure:**
```bash
# On new server, clone repo
git clone <repo> /home/structa.cloud
cd /home/structa.cloud

# Restore database from backup
docker-compose up -d postgres
docker exec -i postgres psql -U structa_user ctc_research_db < backup.sql

# Restore Let's Encrypt certs
mkdir -p applications/proxy/acme
cp backup_acme.json applications/proxy/acme/acme.json
chmod 600 applications/proxy/acme/acme.json

# Start all services
docker-compose up -d
```

**RTO/RPO:**
- **RTO** (Recovery Time Objective): ~10 minutes
- **RPO** (Recovery Point Objective): ~1 hour (depending on backup frequency)

---

## Deployment Checklist

### Pre-Deployment

- [ ] DNS records updated (A records → server IP)
- [ ] SSL certificate obtained (manual or Let's Encrypt)
- [ ] Database backups taken
- [ ] Environment variables configured
- [ ] Docker images built
- [ ] Network configuration tested

### Post-Deployment

- [ ] All containers healthy (`docker ps`)
- [ ] Health checks passing
- [ ] HTTPS working without warnings
- [ ] Static files serving
- [ ] Database migrations ran
- [ ] Admin accessible
- [ ] Send alerts working (if configured)
- [ ] Backups scheduled

---

## Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Check certificate expiry | Weekly | `echo \| openssl s_client...` |
| Database backup | Daily | Automated cron job |
| Review logs | Weekly | `docker logs <container>` |
| Security updates | Monthly | `docker pull <image> && docker-compose up` |
| Full system backup | Monthly | rsync or docker volume backup |
| Traffic analysis | Weekly | Review Traefik/Nginx logs |

---

## References

- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
- [Traefik Networking](https://doc.traefik.io/traefik/routing/entrypoints/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/current/admin.html)
- [Redis Documentation](https://redis.io/docs/)
- [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)
