# Documentation Overview

This directory contains comprehensive deployment and operational documentation for Structa Cloud.

## Main Documents

### 1. **DEPLOYMENT_GUIDE.md** (636 lines)
**Purpose:** Step-by-step guide for deploying and managing the stack

**Contents:**
- Infrastructure overview & architecture diagram
- Complete project structure breakdown
- Docker build and run instructions
- SSL/TLS setup (Let's Encrypt HTTP-01 & Cloudflare DNS-01)
- Django/Wagtail configuration
- 50+ common commands (Docker, Django, Make, Proxy)
- Troubleshooting guide with solutions

**Use when:**
- Deploying a new instance
- Setting up SSL certificates
- Running Django management commands
- Debugging issues

**Key Sections:**
```
├── Infrastructure Overview (services, ports, status)
├── Project Structure (monorepo layout)
├── Docker Deployment (build, run, env vars)
├── Proxy & SSL Configuration (HTTP-01, DNS-01, self-signed fallback)
├── Django Site Setup (database, Wagtail)
├── Common Commands (80+ commands organized by category)
└── Troubleshooting (10+ common issues with solutions)
```

---

### 2. **INFRASTRUCTURE.md** (525 lines)
**Purpose:** Technical reference for infrastructure, containers, and networking

**Contents:**
- Network topology diagram
- Detailed container specifications (ports, memory, health checks)
- SSL/TLS certificate details & renewal
- DNS resolution configuration
- Storage & volumes
- Resource allocation & performance tuning
- Security considerations
- Disaster recovery procedures
- Maintenance schedule

**Use when:**
- Understanding system architecture
- Allocating resources
- Configuring containers
- Planning backups/recovery
- Optimizing performance

**Key Sections:**
```
├── Network Topology (diagram + flow)
├── Container Details (5 services: proxy, django, postgres, redis, nginx)
├── SSL/TLS Configuration (Let's Encrypt, fallback, renewal)
├── DNS Resolution (current records, verification)
├── Storage & Volumes (backup strategy)
├── Performance & Resources (container limits, monitoring)
├── Security (network isolation, firewall, secrets)
├── Disaster Recovery (RTO/RPO procedures)
└── Maintenance Schedule (weekly, monthly tasks)
```

---

### 3. **CHANGELOG.md**
**Purpose:** Track version history and changes

**Contents:**
- Version numbers
- Release dates
- Features added
- Bugs fixed
- Breaking changes

---

### 4. **README_DOCS.md** (this file)
**Purpose:** Guide to all documentation

---

## Document Map

```
Quick Start?
    ↓
    → Start with DEPLOYMENT_GUIDE.md § Infrastructure Overview

Understanding the system?
    ↓
    → Read INFRASTRUCTURE.md for architecture & containers

Deploying?
    ↓
    → DEPLOYMENT_GUIDE.md § Docker Deployment

Configuring SSL?
    ↓
    → DEPLOYMENT_GUIDE.md § Proxy & SSL Configuration
    → INFRASTRUCTURE.md § SSL/TLS Configuration

Running commands?
    ↓
    → DEPLOYMENT_GUIDE.md § Common Commands

Troubleshooting?
    ↓
    → DEPLOYMENT_GUIDE.md § Troubleshooting

Setting up backups?
    ↓
    → INFRASTRUCTURE.md § Storage & Volumes § Backup Strategy

Recovering from disaster?
    ↓
    → INFRASTRUCTURE.md § Disaster Recovery
```

---

## Quick Reference

### Most Common Tasks

#### Check system health
```bash
docker ps                    # All containers running?
docker stats                 # Resource usage
curl -v https://ctc-research.com/  # Site accessible?
```

#### View logs
```bash
docker logs ctc-research-website --tail 50 -f
docker logs default-proxy --tail 50 -f
```

#### Restart service
```bash
docker restart ctc-research-website
docker-compose restart
```

#### See all available commands
```bash
make help                    # Django/Make commands
docker exec ctc-research-website python manage.py --help
```

---

## Deleted Documents

The following report files were removed (consolidated into main docs):

- ✅ CLOUDFLARE_OPTIONAL_SETUP.md → DEPLOYMENT_GUIDE.md § Cloudflare DNS-01
- ✅ DEPLOYMENT_SUMMARY.md → DEPLOYMENT_GUIDE.md
- ✅ DOCKER_DEPLOYMENT_COMPLETE.md → DEPLOYMENT_GUIDE.md § Docker Deployment
- ✅ FINAL_DEPLOYMENT_VERIFICATION.md → DEPLOYMENT_GUIDE.md § Troubleshooting
- ✅ PROXY_INTEGRATION_COMPLETE.md → INFRASTRUCTURE.md
- ✅ PROXY_TEST_SUITE.md → DEPLOYMENT_GUIDE.md § Common Commands
- ✅ TASK3_COMPLETION_SUMMARY.md → Session summary (deleted)
- ✅ TEMPLATE_OSOUL_ANALYSIS.md → DEPLOYMENT_GUIDE.md § Django Site Setup

---

## Document Structure

### DEPLOYMENT_GUIDE.md Organization

| Section | Lines | Purpose |
|---------|-------|---------|
| Infrastructure Overview | ~40 | Diagram and service table |
| Project Structure | ~80 | Directory tree breakdown |
| Docker Deployment | ~60 | Build and run instructions |
| Proxy & SSL | ~150 | HTTP-01, DNS-01, self-signed |
| Django Site Setup | ~80 | Database, Wagtail, admin |
| Common Commands | ~120 | 80+ organized commands |
| Troubleshooting | ~100 | 10+ issues with solutions |

---

### INFRASTRUCTURE.md Organization

| Section | Lines | Purpose |
|---------|-------|---------|
| Network Topology | ~20 | ASCII diagram |
| Container Details | ~150 | 5 services specified |
| SSL/TLS Configuration | ~50 | Certs, renewal, status |
| DNS Resolution | ~20 | Current records, verification |
| Storage & Volumes | ~60 | Backups, mounts |
| Performance | ~50 | Limits, optimization, monitoring |
| Security | ~40 | Network, firewall, secrets |
| Disaster Recovery | ~50 | Procedures, RTO/RPO |
| Maintenance | ~30 | Schedule and tasks |

---

## Key Configurations Reference

### File Locations

| File | Purpose | Read | Edit |
|------|---------|------|------|
| `proxy/traefik/dynamic.yml` | Global Traefik config | Yes | Yes |
| `proxy/traefik/dynamic/*.yml` | Per-site routers | Yes | Yes |
| `proxy/.env` | Cloudflare credentials | No | Yes |
| `proxy/acme/acme.json` | Let's Encrypt store | No | No |
| `applications/pyproject.toml` | Python dependencies | Yes | Rarely |
| `docker-compose.yml` | Container orchestration | Yes | Sometimes |
| `applications/*/settings.py` | Site Django settings | Yes | Rarely |

---

## Environment Variables

### Critical (Must Set)

```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=<random-string>
ALLOWED_HOSTS=ctc-research.com,www.ctc-research.com
DEBUG=False
```

### Optional (Let's Encrypt)

```
CF_DNS_API_TOKEN=<cloudflare-token>  # For DNS-01
LETSENCRYPT_EMAIL=<your-email>
```

---

## Support & Resources

### Internal Resources
- `DEPLOYMENT_GUIDE.md` — Primary operational reference
- `INFRASTRUCTURE.md` — Technical architecture
- `CHANGELOG.md` — Version history
- `AGENTS.md` — Project agent instructions

### External Resources
- [Traefik Docs](https://doc.traefik.io/)
- [Django Docs](https://docs.djangoproject.com/)
- [Wagtail Docs](https://docs.wagtail.org/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Let's Encrypt](https://letsencrypt.org/)

---

## Maintenance Reminders

**Weekly:**
- [ ] Check certificate expiry: `echo | openssl s_client -connect ctc-research.com:443 -servername ctc-research.com 2>/dev/null | openssl x509 -noout -dates`
- [ ] Review container logs for errors
- [ ] Monitor disk usage: `docker system df`

**Monthly:**
- [ ] Database backup
- [ ] Security updates: `docker pull <image> && docker-compose up`
- [ ] Traffic/performance analysis
- [ ] Full system backup

**Quarterly:**
- [ ] Database password rotation
- [ ] Secrets review and audit

---

## Quick Troubleshooting Index

| Problem | Solution | See |
|---------|----------|-----|
| "This site can't be reached" | Update DNS A records | DEPLOYMENT_GUIDE § Troubleshooting |
| SSL certificate error | Let's Encrypt challenge failed | DEPLOYMENT_GUIDE § SSL Setup |
| "Placeholder Page" shown | django-fusion not installed | DEPLOYMENT_GUIDE § Troubleshooting |
| 502 Bad Gateway | Gunicorn crashed | DEPLOYMENT_GUIDE § Troubleshooting |
| Database connection fails | PostgreSQL down | DEPLOYMENT_GUIDE § Troubleshooting |
| Static files not loading | Nginx misconfigured | DEPLOYMENT_GUIDE § Troubleshooting |

---

## How to Update Documentation

When changes are made to the system:

1. **Update relevant section** in DEPLOYMENT_GUIDE.md or INFRASTRUCTURE.md
2. **Update version** in file header (Last Updated: date)
3. **Add entry** to CHANGELOG.md
4. **Commit** with clear message: `docs: update SSL configuration`

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-05 | 1.0.0 | Initial comprehensive documentation |

---

**Generated:** July 5, 2026  
**Status:** Current  
**Maintained By:** Development Team
