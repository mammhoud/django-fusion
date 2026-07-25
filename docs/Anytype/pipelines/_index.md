# Pipelines — CI/CD Workflows

> **Type:** Pipeline 🔄
> **Description:** CI/CD pipeline definitions, build scripts, test workflows, deployment automation, and security scanning across all projects.

---

## Pipeline Categories

| Type | Provider | Trigger | Description |
|------|----------|---------|-------------|
| **CI** | GitHub Actions | Push, PR | Build, lint, test |
| **CD** | Docker Compose | Deploy command | Deploy to production |
| **Test** | GitHub Actions | Push | Run test suites |
| **Security** | GitHub Actions | Schedule | Dependency audit, SAST |
| **Deploy** | Docker | Manual | Production deployment |

---

## Current Pipelines

| Pipeline | File | Type | Status |
|----------|------|------|--------|
| Pytest Core | `.github/workflows/pytest-core.yml` | CI | ✅ Active |
| Deploy CI | `.github/workflows/deploy-ci.yml` | CD | ✅ Active |
| Check Extras | `.github/workflows/check-extras.yml` | CI | ✅ Active |

---

## Related

- → `../objects/pipeline.md` — Pipeline object type
- → `../releases/_index.md` — Related releases
- → `../references/_index.md` — Config references
- → `../README.md` — Master index
