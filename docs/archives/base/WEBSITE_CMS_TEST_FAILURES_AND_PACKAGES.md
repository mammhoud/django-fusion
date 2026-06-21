# Website CMS, package, and smoke-test notes

## What was checked

- Root pytest smoke suite: website settings, shared task package structure, and YAML scenario validation.
- CI template validator import path used by `tests/ci/test_template_validation.py`.
- Docker compose topology for the root stack and shared media container.
- GitHub Actions lint/test/docker smoke workflows.

## Fixed failure causes

### Docker smoke: missing `traefik-net`

The Docker smoke workflow failed before containers were created because multiple compose files declared `traefik-net` and `site_network` as external networks. External networks must already exist on a fresh GitHub Actions runner, so `docker compose up` stopped with:

```text
network traefik-net declared as external, but could not be found
```

The canonical compose files now let Compose create these named networks. The root Docker workflow also validates the compose file before booting containers.

### Per-site compose drift

The website smoke tests expect one canonical compose topology under `compose/` plus the root `docker-compose.yml`. The duplicated `ctc-research/docker-compose.yml` and `lms-demo/docker-compose.yml` files had drifted from that topology. Their web services were moved into `compose/docker-compose.yml` as:

- `ctc-research-website` on port `5070`
- `lms-demo-website` on port `5071` behind the `lms` profile
- `vresume-website` on port `5072` behind the `vresume` profile

### Shared media container drift

The shared media service is now named `shared-media`, mounts one workspace media directory at `/var/www/media`, and keeps per-site static directories under `/var/www/sites/<site>/static`. The nginx `/media/` location points at the shared media mount.

### Template validator import failure

`tests/ci/test_template_validation.py` imported `www.core.CI.utils`, but that module did not exist in the workspace import path. A namespace-safe implementation now validates Django template syntax with the configured Django template engine and reports missing context variables as warnings.

## Package usage map

| Package / module | Where it is used | Usage note |
| --- | --- | --- |
| `django` | `configs/`, `tests/`, each website package | Core settings, URL routing, management commands, and template rendering. |
| `wagtail` | `ctc-research/www/core/content`, `lms-demo/www/core/content`, website templates | CMS page models and StreamField-backed content templates. Templates should render page/model fields instead of hard-coded demo copy. |
| `django-osoul` | `pyproject.toml` / `uv.lock` internal source | Internal GitHub-sourced package kept in the workspace dependency set for grep/search-related Django integrations. |
| `django-osoul` | `pyproject.toml`, settings and tests | Shared site/app conventions and compatibility helpers used by the website apps. |
| `crafts-ai` | `pyproject.toml`, `tasks/crafts_ai.py`, account/registration tests | Internal integration package used by task recovery and registration/auth compatibility tests. |
| `pytest` / `pytest-django` | `pyproject.toml`, `tests/` | Root smoke and Django-aware tests. CI now calls `uv run pytest` from the repository root. |
| `ruff` | GitHub Actions lint workflow | Installed in the lint job and run against the repository using `.ruff.toml`. |
| `webpack` / frontend packages | `assets/package.json`, `webpack/` | The workspace-level assets package owns frontend dependencies and builds all site bundles. |

## Remaining environment notes

- `docker compose config` could not be run in this local container because the Docker CLI is not installed here. The GitHub workflow runs this check on `ubuntu-latest`, where Docker Compose is available.
- `uv lock` could not be refreshed locally because outbound package-index access failed while fetching PyPI metadata. No dependency lock change is required for the workflow lint enhancement because Ruff is installed directly in the lint job.
- `uv run ctc-research check` now gets past the previous missing `www.core.content` import path, but it still exposes runtime configuration/admin-check issues in this local development environment: an insecure short development `SECRET_KEY` and an allauth/admin inline relation that Django reports as an unresolved string model during the admin system check. Those are documented separately from the smoke-suite failures fixed here.

## Commands used during verification

```bash
.venv/bin/python -m pytest
.venv/bin/python -m pytest tests/ci/test_template_validation.py -q
.venv/bin/python -m pytest tests/websites tests/docker tests/unit/test_app_structure.py -q
.venv/bin/python -m compileall -q configs tasks tests www
```
