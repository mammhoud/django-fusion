---
# yaml-language-server: $schema=schemas/milestone.schema.json
Object type:
    - Milestone
Creation date: "2024-03-26T22:21:36Z"
Created by:
    - mammhoud
Emoji: "\U0001F4CB"
id: bafyreibllqdhrbx4pvgb67rz2guw2kzb35nmtv3a5isxvqmq4v4ozgzetu
---
# Operational Plan   
**Development Workflow**   
1. **Planning Phase** – Requirements are captured in the Anytype workspace, linked to technical specifications and repo paths.   
2. **Implementation Phase** – Feature branches are created from `main`.   
3. **Testing Phase** – Local testing via `make test-local`; Docker‑based integration tests.   
4. **Review Phase** – Pull request with CI checks (linting, tests, compose validation).   
5. **Deployment Phase** – Merge to `main`; run `make deploy` to production.   
   
**Branching Strategy**   
- `main` – Production‑ready code.   
- `develop` – Integration branch (optional, depending on team size).   
- `feature/<description>` – New features.   
- `fix/<description>` – Bug fixes.   
- `release/<version>` – Release preparation.   
   
### 1.2 Continuous Integration Pipeline   
**GitHub Actions Configuration** (simplified)   
```
name: Structa Cloud CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Django checks
        run: make -C core check WEBSITE=ctc-research

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: structa
          POSTGRES_PASSWORD: test
          POSTGRES_DB: structa_test
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: make -C core test-local

  compose:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Compose config validation
        run: make deploy-preflight

```
 --- 
### 2. Production Operations   
### 2.1 Deployment Process   
**Deployment Stages**   
1. **Pre‑deployment** – `make deploy-preflight` validates Docker Compose configuration.   
2. **Database Migration** – `make -C core migrate WEBSITE=<site>`.   
3. **Static Files** – `make -C core collect-static WEBSITE=<site>`.   
4. **Asset Build** – `make -C core build-assets WEBSITE=<site>`.   
5. **Application Deployment** – Docker containers are updated (rolling or blue‑green).   
6. **Post‑deployment** – Health checks, monitoring setup, and smoke tests.   
   
**Full Deployment Command**   
```
make deploy

```
This executes in sequence:   
1. Databases (PostgreSQL + Redis)   
2. Media storage   
3. Application containers   
4. Task queues (Celery if used)   
5. Documentation deployment   
6. Proxy (Traefik + Nginx)   
   
### 2.2 Infrastructure Management   
**Container Orchestration**   
- **Development**: Docker Compose.   
- **Production**: Swarm Mode or Kubernetes (optional).   
- **Health checks**: Traefik and Docker health checks.   
- **Logging**: Centralised logging (ELK or Loki).   
   
**Service Architecture** (Diagram)   
```
┌─────────────────────────────────────────────────────────┐
│                      Traefik (Proxy)                   │
│                  SSL Termination & Routing              │
├──────────┬────────────────┬─────────────────────────────┤
│   Nginx  │                │                             │
│  Static  │   Application  │   PostgreSQL/Redis          │
│  Files   │   Containers   │   Databases                 │
├──────────┴────────────────┴─────────────────────────────┤
│                    Docker Volumes                       │
└─────────────────────────────────────────────────────────┘

```
### 2.3 Monitoring and Logging   
**Key Metrics**   
- **Application**: Request latency, error rates, user sessions.   
- **Database**: Connection pool, query performance, disk usage.   
- **System**: CPU, memory, disk I/O.   
- **Business**: User registrations, content creation, course enrolments.   
   
**Monitoring Tools**   
- **Prometheus** – metrics collection and aggregation.   
- **Grafana** – visualisation and dashboards.   
- **ELK Stack** – log aggregation and analysis.   
- **Uptime monitoring** – external availability checks.   
   
**Alerting Policy**   
| Priority   <br> | Response Time   <br> |           Example Alert   <br> |
|:----------------|:---------------------|:-------------------------------|
|   **P1**   <br> |  < 15 minutes   <br> |     Service unavailable   <br> |
|   **P2**   <br> |      < 1 hour   <br> |   High error rate (>5%)   <br> |
|   **P3**   <br> |     < 4 hours   <br> | Resource warning (>80%)   <br> |
|   **P4**   <br> |    < 24 hours   <br> |    Non‑critical anomaly   <br> |

 --- 
### 3. Customer Service Operations   
### 3.1 Support Channels   
**Tier 1 (Community)**   
- GitHub Issues – bug reports and feature requests.   
- Discord/Slack – community discussion and troubleshooting.   
- Documentation – self‑service support.   
   
**Tier 2 (Professional)**   
- Email Support – dedicated support for paying customers.   
- Video Calls – issue resolution and training sessions.   
- Ticket System – priority support tracking.   
   
**Tier 3 (Enterprise)**   
- Dedicated Account Manager – relationship management.   
- On‑Call Support – 24/7 availability.   
- Custom Development – feature extensions.   
   
### 3.2 Service Level Agreements (SLA)   
|     Service Tier   <br> |    Response Time   <br> |  Resolution Time   <br> | Availability   <br> |
|:------------------------|:------------------------|:------------------------|:--------------------|
|    **Community**   <br> |  2 business days   <br> |      Best effort   <br> |       No SLA   <br> |
| **Professional**   <br> | 4 business hours   <br> | 8 business hours   <br> |        99.5%   <br> |
|   **Enterprise**   <br> |  1 business hour   <br> | 4 business hours   <br> |        99.9%   <br> |

### 3.3 Customer Service Workflow   
1. **Ticket Creation** – customer submits via GitHub, email, or Discord.   
2. **Categorisation** – priority and category assigned.   
3. **Assignment** – assigned to appropriate team member.   
4. **Investigation** – issue reproduced and root cause identified.   
5. **Resolution** – fix applied or workaround provided.   
6. **Verification** – customer confirms resolution.   
7. **Documentation** – solution documented for future reference.   
 --- 
   
### 4. Development and Production Workflow Mapping   
|              Phase   <br> |               Activity   <br> |              Repo Location   <br> |   Anytype Workspace   <br> |
|:--------------------------|:------------------------------|:----------------------------------|:---------------------------|
|       **Ideation**   <br> |           Capture idea   <br> |                          –   <br> |       Tasks, Vision   <br> |
|       **Planning**   <br> | Requirements gathering   <br> |                          –   <br> | Product Development   <br> |
|         **Design**   <br> |       Component design   <br> | `core/libs/django-fusion/`   <br> |        Architecture   <br> |
| **Implementation**   <br> |                 Coding   <br> |             `core/<site>/`   <br> |     Sprint Planning   <br> |
|        **Testing**   <br> |             Validation   <br> |                   `tests/`   <br> |   Quality Assurance   <br> |
|         **Review**   <br> |           Pull request   <br> |                     GitHub   <br> |         Code Review   <br> |
|     **Deployment**   <br> |      Production launch   <br> |      `applications/proxy/`   <br> |    Release Planning   <br> |
|    **Maintenance**   <br> |                Support   <br> |                    `docs/`   <br> |     Support Tickets   <br> |

### Useful Make Commands   
```
# Development
make -C core run-dev WEBSITE=<site>       # Start development server
make -C core build-assets WEBSITE=<site>  # Build frontend assets
make -C core migrate WEBSITE=<site>       # Run migrations
make -C core shell WEBSITE=<site>         # Django shell
make -C core check WEBSITE=<site>         # Django checks

# Testing
make -C core test-local                   # Run tests locally
make -C core test-parallel                # Run tests in parallel
make deploy-preflight                     # Validate compose config

# Deployment
make deploy                               # Full deployment
make deploy-databases                     # Deploy databases
make deploy-media                         # Deploy media storage
make deploy-apps                          # Deploy applications
make deploy-proxy                         # Deploy proxy

# Utilities
make -C core update-translations WEBSITE=<site>  # Update translations
make -C core compile-translations WEBSITE=<site> # Compile translations

```
 --- 
### 5. Disaster Recovery and Business Continuity   
### 5.1 Backup Strategy   
- **Database Backups**   
    - Daily full backup at 02:00 UTC.   
    - Hourly incremental via WAL archiving.   
    - Retention: 30 days daily, 12 months monthly.   
- **Media and File Backups**   
    - Continuous replication to S3‑compatible storage.   
    - Daily snapshots to backup location.   
    - Retention: 90 days.   
- **Configuration Backups**   
    - Versioned in Git (on change).   
    - Environment variables and secrets stored in a secure vault.   
    - Retention: infinite (versioned).   
   
### 5.2 Recovery Procedures   
|                Scenario   <br> | Recovery Time Objective (RTO)   <br> | Recovery Point Objective (RPO)   <br> |
|:-------------------------------|:-------------------------------------|:--------------------------------------|
| **Database corruption**   <br> |                       2 hours   <br> |                     15 minutes   <br> |
|    **Full system loss**   <br> |                       4 hours   <br> |                       24 hours   <br> |
|  **Data centre outage**   <br> |                       8 hours   <br> |                       24 hours   <br> |
|         **DDoS attack**   <br> |                        1 hour   <br> |                       1 minute   <br> |

**Recovery Steps**   
1. **Assessment** – identify extent of failure and data loss.   
2. **Infrastructure** – provision replacement infrastructure.   
3. **Data Restoration** – restore latest valid backup.   
4. **Application Deployment** – deploy application containers.   
5. **Verification** – validate system functionality.   
6. **Cutover** – redirect traffic to restored environment.   
 --- 
   
### 6. Customer Fulfilment Process   
### 6.1 User Onboarding Workflow   
1. **Account Creation** – user registers (email verification required), organisation account setup.   
2. **Site Selection** – choose site type (CTC Research, LMS Demo, VResume), select customisation options, configure initial content.   
3. **Template Customisation** – access Tinker UI, select theme, colors, layout, preview changes in real‑time.   
4. **Content Creation** – Wagtail admin access, AI‑assisted content generation, media upload.   
5. **Launch** – domain configuration (subdomain or custom), site activation, user training and documentation.   
   
### 6.2 Support Ticket Workflow   
|                 Priority   <br> |   Response Time   <br> |     Workaround   <br> |                  Resolution   <br> | Communication   <br> |
|:--------------------------------|:-----------------------|:----------------------|:-----------------------------------|:---------------------|
|        **P1 (Critical)**   <br> |       Immediate   <br> |  Within 1 hour   <br> |              Within 4 hours   <br> | Email & phone   <br> |
|       **P2 (Important)**   <br> |  Within 2 hours   <br> | Within 4 hours   <br> |             Within 24 hours   <br> |         Email   <br> |
|           **P3 (Minor)**   <br> |  Within 8 hours   <br> |            N/A   <br> |             Within 72 hours   <br> |         Email   <br> |
| **P4 (Feature Request)**   <br> | Within 24 hours   <br> |            N/A   <br> | Within 2 weeks (evaluation)   <br> |         Email   <br> |

 --- 
**See also:**   
- [Risk Management](.md) – for backup and recovery procedures.   
- [Website Applications](.md) – for details on the components being deployed.   
