# 📦 Publishing

> How to publish, deploy, and release Structa Cloud projects to production, GitHub, and package registries.

---

## In This Section

| Page | Content |
|------|---------|
| [Docker Deploy](docker-deploy.md) | Full Docker deployment pipeline: compose files, networks, preflight, health checks |
| [POS Release](pos-release.md) | POS Tauri desktop release process: build matrix, platforms, artifacts |
| [CI/CD](ci-cd.md) | GitHub Actions workflows: deploy-ci, pytest-core, check-extras, POS releases |

---

## Publish Targets

### Git Push (make push)

```bash
make push          # Push repo + lib submodules
make push-libs     # Push only lib submodules
make push-lib LIB=django-fusion  # Push a single lib
```

Requires `github=<token>` in `.env` or `GITHUB_TOKEN` env var.

### Docker Deployment

```bash
make deploy        # Full stack deploy
make deploy-app    # Django apps only
make deploy-proxy  # Traefik proxy
```

Deploys to production Docker host via `docker compose`.

### Coolify

```bash
make deploy-coolify     # Deploy Coolify platform
make upgrade-coolify    # Upgrade Coolify
make backup-coolify     # Backup Coolify data
```

Coolify provides a web UI for managing deployments independently.

### mkdocs Site

```bash
cd docs && mkdocs build          # Build static site
cd docs && mkdocs gh-deploy      # Deploy to GitHub Pages
```

Documentation site: `https://structa.cloud/docs/`

---

## Release Checklist

- [ ] `make verify-release` passes (tag integrity + local smoke)
- [ ] `make push` succeeds (repo + libs)
- [ ] CI passes (`.github/workflows/pytest-core.yml`)
- [ ] `make deploy` succeeds on staging
- [ ] Health probes pass (`make probe-health`)
- [ ] Smoke test: visit each site in browser
- [ ] Bump version: `make bump-app-patch`

---

## CI/CD Pipeline

```
push to generic
    │
    ├── deploy-ci.yml (preflight gate)
    │   ├── markdown-links (validates cross-references)
    │   └── check-extras (validates pyproject.toml extras)
    │
    └── pytest-core.yml
        └── Full test suite from projects/
```

---

## Docker Image Lifecycle

| Image | Dockerfile | Registry |
|-------|-----------|----------|
| precis-ctc-website | `projects/compose/Dockerfile` | Local build |
| lms-website | `projects/compose/Dockerfile` | Local build |
| vresume-website | `projects/compose/Dockerfile` | Local build |
| shared-proxy | `applications/proxy/Dockerfile.nginx` | Local build |
| default-proxy | `applications/proxy/Dockerfile` | Local build |
| shared-worker | `applications/compose/Dockerfile.tasks` | Local build |

---

## Related

| Topic | Path |
|-------|------|
| Infrastructure | [`../infrastructure/`](../infrastructure/) |
| Deployment guide | [`../guides/04-deploy.md`](../guides/04-deploy.md) |
| Clone site | [`../guides/06-clone-site.md`](../guides/06-clone-site.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
