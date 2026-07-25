---
# yaml-language-server: $schema=../schemas/page.schema.json
Object type: Plan
Tags: operations, delivery, production, logistics
Status: Published
Type: Roadmap
Related Plans: product-development, market-research
Related Goals: business-goal
---

# Operational Plan — Delivery & Operations

> **Type:** Plan 📋
> **Emoji:** 📋
> **Description:** Operational processes covering development workflow, production infrastructure, logistics, customer service, and disaster recovery for the Structa Cloud platform.

---

## 1. Development Operations

### 1.1 Development Workflow

```
Anytype Capture → Task Creation → Makefile Target → Code → Test → PR → Review → Deploy
```

| Stage | Tool | Responsible |
|-------|------|-------------|
| Planning | Anytype workspace | Product owner |
| Development | VS Code, Makefile | Developers |
| Testing | pytest, vitest, Django test client | Developers |
| Review | GitHub PRs | Team |
| Deployment | Docker Compose, Makefile | DevOps |

### 1.2 Version Control

- **Repository:** GitHub monorepo with submodules
- **Branch Strategy:** Feature branches → PR → main
- **Release Tagging:** Semantic versioning (v1.2.3)
- **Submodules:** django-fusion, ceptor-ai (pinned versions)

### 1.3 CI/CD Pipelines

| Pipeline | Provider | Purpose |
|----------|----------|---------|
| Pytest Core | GitHub Actions | Run Django test suite |
| Deploy CI | GitHub Actions | Build and deploy containers |
| Check Extras | GitHub Actions | Lint, type-check, security scan |

---

## 2. Production Infrastructure

### 2.1 Service Architecture

```
Traefik Proxy (:443)
  ↓ (SNI routing)
Django App Containers
  ↓
Nginx Media Server
  ↓
PostgreSQL + Redis
```

### 2.2 Deployment Order

| Step | Service | Dependencies |
|------|---------|-------------|
| 1 | PostgreSQL + Redis | None |
| 2 | Application containers | Database ready |
| 3 | Nginx media server | Application running |
| 4 | Traefik proxy | All services healthy |

### 2.3 Environment Configuration

| Environment | Purpose | URL |
|-------------|---------|-----|
| Development | Local dev servers | localhost:50xx |
| Staging | Pre-production testing | staging.structa.cloud |
| Production | Live service | structa.cloud |

---

## 3. Customer Service & Support

| Tier | Response Time | Channels | Included |
|------|:-------------:|----------|----------|
| **Community** | 48 hours | GitHub Issues, Discord | Free tier |
| **Professional** | 8 hours | Email, ticket system | Subscription |
| **Enterprise** | 1 hour | Phone, dedicated Slack | Custom contract |

---

## 4. Disaster Recovery

| Scenario | RTO | RPO | Procedure |
|----------|:---:|:---:|-----------|
| Database corruption | 4 hours | 1 hour | Restore from latest PostgreSQL dump |
| Container failure | 10 minutes | — | Auto-restart via Docker Compose |
| Full service failure | 2 hours | 1 hour | Redeploy from clean state |
| Data center outage | 24 hours | 24 hours | Failover to secondary region |

### Backup Strategy

| Data | Frequency | Retention | Storage |
|------|:---------:|:---------:|---------|
| PostgreSQL dump | Daily | 30 days | S3-compatible |
| Media files | Continuous | — | Docker volumes |
| Configuration | Per change | Git history | GitHub |

---

## 5. Security Operations

| Area | Measure | Frequency |
|------|---------|:---------:|
| Dependency audit | `uv audit`, Dependabot | Weekly |
| SSL certificates | Let's Encrypt auto-renewal | Every 90 days |
| Access review | GitHub team permissions | Quarterly |
| Penetration testing | Third-party security audit | Annually |

---

## Related Docs

- → `product-development.md` — Development lifecycle
- → `market-research.md` — Market context
- → `risk-management.md` — Risk assessment
- → `monitoring.md` — Metrics and monitoring
- → `../architecture/overview.md` — Architecture reference
- → `../guides/deployment.md` — Deployment guide
- → `../README.md` — Master index
