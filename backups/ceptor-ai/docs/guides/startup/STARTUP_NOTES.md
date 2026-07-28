# Structa Cloud — Startup Notes

> Last updated: July 2026

## Quick Start Order

1. **Clone & Environment** — `git clone`, set up `.env` files, install `uv`
2. **Docker Services** — `docker compose up -d postgres redis` (warehouse layer)
3. **Python Dependencies** — `uv sync` from the monorepo root
4. **Database Setup** — `make -C applications migrate WEBSITE=<site>`
5. **Frontend Assets** — `npm --prefix applications/assets ci --include=dev --legacy-peer-deps`
6. **Build Assets** — `make -C applications build-assets WEBSITE=<site>`
7. **Run Dev Server** — `make -C applications run-dev WEBSITE=<site>`

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `WEBSITE` | Select active site: `ctc-research`, `lms-demo`, `vresume` |
| `DJANGO_SITE` | Same as `WEBSITE` (canonical name) |
| `PROJECT_PATH` | Site directory name (used by build tools) |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database credentials |
| `REDIS_URL` | Redis connection string |
| `SITE_DOMAIN` | Primary domain (e.g., `ctc-research.com`) |

## Key Commands

```bash
# Django checks
make -C applications check WEBSITE=ctc-research

# Run site tests
make -C applications tests-website WEBSITE=ctc-research

# Build frontend assets
make -C applications build-assets WEBSITE=vresume

# Docker deployment
make -C applications docker-up WEBSITE=ctc-research
```

## Site Directory Map

| Site | Alias | Directory | Port |
|------|-------|-----------|------|
| CTC Research | `ctc`, `ctc-research` | `applications/ctc-research/` | 5070 |
| LMS Demo | `structa`, `lms-demo` | `applications/lms-demo/` | 5071 |
| VResume | `vresume` | `applications/VResume/` | 5072 |

## See Also

- [Infrastructure Guide](../infrastructure/infrastructure-overview.md)
- [Deployment Guide](../infrastructure/deployment-guide.md)
- [Development Guide](../development/makefile-reference.md)
- [Enhancement Roadmap](../enhancement-roadmap.md)
