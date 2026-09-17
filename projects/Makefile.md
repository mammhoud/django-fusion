# Makefile Cheatsheet — Structa Cloud

Path: `projects/Makefile`

Run all targets from `projects/` directory: `cd projects && make <target>`
Every command takes `WEBSITE=<site>` — see the site selection table below.

> **Keep in sync:** this cheatsheet mirrors `projects/Makefile`. If you change a
> target, update this file in the same change.

## 🧭 Website Selection (`WEBSITE=`)

| `WEBSITE=` value | SITE | Compose file | Notes |
|------------------|------|--------------|-------|
| `ctc` · `precis-ctc` · `ctc-website` · `ctc-research.com` | `precis-ctc` | `precis/precis-ctc/docker-compose.yml` | Medical research center |
| `precis-main` | `precis-main` | `structa.cloud/docker-compose.yml` | Unified LMS + landing (canonical) |
| `precis-lms` · `precis-landing` | `precis-main` | `structa.cloud/docker-compose.yml` | Legacy aliases → precis-main |
| `structa` · `lms` · `core` · `structa.cloud` | `precis-main` | `structa.cloud/docker-compose.yml` | Legacy aliases → precis-main |
| `loop-crm` · `crm` · `crm.structa.cloud` · `inventory` | `loop-crm` | `loop-crm/docker-compose.yml` | Unified sales + marketing CRM |
| `vresume` · `VResume` · `resume` | `vresume` | *(legacy — not present in checkout)* | Portfolio/VResume (legacy) |
| `cms-fusion` · `cms-full` · `cmsfull` | `cms-fusion` | `docker-compose.yml` | Legacy Fusion CMS (not present) |

> Most Django commands (`check`, `test`, `run-dev`, `migrate`, `collectstatic`)
> **delegate to the site's own backend Makefile** — the site must have a backend
> tree (`precis-ctc`, `precis-main`, `loop-crm`). Legacy sites fall back to the
> generic `uv run <module>` path.

## Quick Reference

### Checks & Validation
| Command | Description |
|---------|-------------|
| `make check` | Django system checks — delegates to the site backend (`make -C <backend> check`) |
| `make check-all` | Backend checks for precis-main + loop-crm, then all Formint editions |
| `make full-site-check` | Full pipeline: assets → collectstatic → migrate → load dumps → verify → website tests |
| `make validate-config` | `docker compose config` + Django `validate_config` if present |
| `make validate-compose-env` | Print compose service/env wiring (no secrets) |
| `make domain-drift` | Run the domain drift check script |

### Testing
| Command | Description |
|---------|-------------|
| `make test` | Backend test suite — delegates to the site backend (`make -C <backend> test`) |
| `make test-local` · `make tests-local` | Run `uv run pytest` locally |
| `make test-fusion` | Run precis-main backend tests |
| `make tests-website` | Run the workspace website suite: `uv run python -m pytest tests/websites` |
| `make tests-unit` / `tests-integration` / `tests-websites` | Delegate to `tests/Makefile` unit / integration / websites targets |

### Development & Server
| Command | Description |
|---------|-------------|
| `make run-dev` | Django dev server — delegates to the site backend (`make -C <backend> dev`) |
| `make run-local` · `make runserver-local` | Alias for `run-dev` |
| `make migrations` / `make migrate` | Make + apply migrations — delegates to the site backend |
| `make server` / `server-gunicorn` / `server-uvicorn` | Container start scripts (gunicorn/uvicorn) |
| `make -C <site>/backend shell` | Django shell — via the site's backend Makefile |

### Docker Build
| Command | Description |
|---------|-------------|
| `make docker-build` | Build the selected site's service (`DOCKER_SERVICE`) |
| `make docker-build-ctc` | Build precis-ctc image |
| `make docker-build-lms` | ⚠️ Legacy alias — builds **precis-main** (lms merged) |
| `make docker-build-vresume` | ⚠️ Legacy — vresume not present in checkout |
| `make docker-build-server` | Alias for `docker-build` |
| `make docker-build-shared-proxy` | Build the shared-proxy Nginx media image |
| `make docker-build-all` | CTC + LMS + VResume + shared-proxy (legacy set) |

### Docker Operations
| Command | Description |
|---------|-------------|
| `make docker-up` | Build + start the selected site service (logs to `logs/deploy/`) |
| `make up` | Alias for `docker-up` |
| `make docker-down` | Stop the selected site's compose project |
| `make docker-logs` | Follow logs for the selected site service |
| `make docker-status` | Compose ps + `docker stats` |
| `make docker-health-check` | Health-check the selected site's container on `DOCKER_HEALTH_PORT` |
| `make probe-health` | Health-check precis-main + loop-crm containers |
| `make docker-logs-all` / `docker-logs-service` | All logs / a specific service |
| `make docker-restart-all` / `docker-start-all` / `docker-stop-all` | Restart / start / stop all services |

### Docker Cleanup
| Command | Description |
|---------|-------------|
| `make docker-clean` | Down + prune unused containers/images/networks/build cache (volumes preserved) |
| `make docker-clean-all` | Clean + remove all unused images/volumes (destructive) |
| `make docker-prune-containers` | Down with `--remove-orphans` |
| `make docker-prune-data` | Down with `--volumes --remove-orphans` (destructive) |

### Per-Site Operations
| Command | Description |
|---------|-------------|
| `make precis-ctc-up` | Start CTC Research stack (`docker-up WEBSITE=precis-ctc`) |
| `make structa-up` | Start **precis-main** stack (legacy `structa` alias) |
| `make vresume-up` | ⚠️ Legacy — vresume not present in checkout |
| `make loop-crm-up` | Create networks + start loop-crm stack |
| `make loop-crm-migrate` | Run loop-crm migrations in the container |
| `make collectstatic-site WEBSITE=<site>` | Collect static via the backend Makefile |
| `make migrate-site WEBSITE=<site>` | Migrate via the backend Makefile |
| `make build-assets-site WEBSITE=<site>` | Build assets (delegates to `build-assets`) |
| `make load-dumps-site WEBSITE=<site>` | `tests/scripts/load_dumped_data.py --site <site>` |
| `make populate-data-site WEBSITE=<site>` | `tests/scripts/populate_site_data.py --site <site> --include-shared` |
| `make populate-data-all` | Populate precis-main + loop-crm |
| `make verify-runtime-site WEBSITE=<site>` | `tests/scripts/staging/verify_runtime.py --site <site>` |

### Deployment
| Command | Description |
|---------|-------------|
| `make docker-redeploy` · `make deploy` · `make redeploy` | Build + restart the selected site (precis-ctc delegates to its project Makefile) |
| `make redeploy-with-stack` | Full-stack redeploy (front + back + worker + scheduler) for precis-ctc |
| `make docker-redeploy-with-worker` | Redeploy web + worker if a worker service exists in the compose file |
| `make docker-deploy-full` | Clean + warehouse + traefik + websites |
| `make docker-deploy-websites` | precis-main + loop-crm stacks |
| `make docker-deploy-traefik` / `docker-deploy-warehouse` | Proxy / postgres+redis |
| `make docker-up-prod` / `docker-up-custom` | Up with compose overrides |
| `make run-all` | Warehouse → traefik → websites |

### Assets & Build
| Command | Description |
|---------|-------------|
| `make assets` | Delegate to a site's assets Makefile (precis-ctc only; others exit with a message) |
| `make build-assets` | Per-site dispatch: precis-ctc / precis-main / loop-crm asset pipelines |
| `make build-assets-all` | Build assets for precis-ctc + precis-main + loop-crm |
| `make build-assets-site WEBSITE=<site>` | Build assets for a specific site |

### Delegation Shortcuts (project dirs)
| Command | Description |
|---------|-------------|
| `make website-ctc` | `make -C precis/precis-ctc <target>` |
| `make website-precis` · `website-precis-main` · `website-precis-lms` | `make -C structa.cloud <target>` |
| `make website-structa` | `make -C structa.cloud <target>` (legacy alias) |
| `make website-vresume` | Guarded — skipped when `portfolio/` is absent |
| `make website-formints` · `website-pos` | `make -C formints <target>` |
| `make projects` | Run a target in precis-main, loop-crm, formints |
| `make scripts` · `make script` | Delegate to `tests/scripts/Makefile` (+ `assets/Makefile` if present) |
| `make tests` | Delegate to `tests/Makefile` |

### Utilities
| Command | Description |
|---------|-------------|
| `make help` | Show top-level targets + website selection |
| `make show-targets` | List every target in the Makefile |
| `make show-vars` / `make show-config` | Print resolved variables (SITE, MANAGE, COMPOSE_FILE, …) |
| `make clean` | Remove Python cache + build artifacts + logs (safe, source untouched) |
| `make clean-logs` / `make clean-site-logs` | Clean generated logs (keeps `.gitkeep`) |
| `make clean-docker` | Safe Docker clean for the selected site (down + prune, volumes kept) |
| `make clean-unused` | `clean` + `clean-docker` — everything unused, volumes preserved |
| `make lint` / `format` / `typecheck` | Pylint / Black / mypy over active products |
| `make lint-all` | lint + typecheck |
| `make docs` | List `docs/` contents |
| `make docker-traefik-generate-certs` / `backup-certs` / `restore-certs` | Traefik SSL certificate operations |

## Remarks & Notes

- **Default `WEBSITE` is `ctc`** — `make docker-up` alone targets precis-ctc.
- `structa`/`lms`/`core` and `precis-lms`/`precis-landing` are **legacy aliases that resolve to precis-main** (the merged product). Don't reference `projects/lms/` — it no longer exists.
- `vresume`/`cms-fusion` sites are legacy and **not present in this checkout** — their compose targets report or skip; `website-vresume` prints a notice.
- Check/test/migrate/run-dev **delegate to the site's backend Makefile** — for a quick look at what will run, use `make -n check WEBSITE=structa.cloud`.
- The root `Makefile` forwards unknown targets here (`make check`, `make community-test`, …), and `make structa` / `make precis-main` etc. delegate with a preset `WEBSITE`.
- Sync with `projects/Makefile` when adding/renaming targets; keep canonical paths + aliases documented here.
