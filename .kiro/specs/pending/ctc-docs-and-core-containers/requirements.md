# Requirements Document

**Category Context: Documentation**
- **Category**: Docs
- **Scope**: Documentation systems, content management, API documentation, user guides
- **Related Specs**: comprehensive-project-documentation, ctc-docs-and-core-containers, docs-plugin-enhancement
- **Common Patterns**: Documentation generation, content management, plugin development, API docs
- **Avoid Duplicates**: Check existing docs specs before creating new documentation features


## Introduction

Add two new Docker containers to the ctc-research project:

1. **docs** — an nginx:alpine container serving the ctc-research project's docsify-style markdown documentation, accessible via the existing Traefik route for `core.structa.cloud` (and other domains already configured in `compose/traefik/dynamic/docs.yml`).

2. **ctc-core** — a Django/Uvicorn container running the ctc-research `core` app, using the same Dockerfile and technology stack as `ctc-django-main`, accessible via a dedicated domain through Traefik.

Both containers must join the external `traefik-net` network and follow the same patterns as existing ctc-research containers.

---

## Glossary

- **Docs_Container**: The nginx:alpine Docker service named `docs` that serves docsify markdown documentation for the ctc-research project.
- **Core_Container**: The Django/Uvicorn Docker service named `ctc-core` that runs the ctc-research core application.
- **Traefik**: The external reverse proxy managing TLS termination and routing via the `traefik-net` Docker network.
- **Traefik_Dynamic_Config**: A YAML file placed in `compose/traefik/dynamic/` that defines HTTP routers and services for Traefik.
- **Docsify**: A client-side documentation framework that renders markdown files via a single-page `index.html`.
- **ctc-research**: The Django/Wagtail project located in the `ctc-research/` directory.
- **traefik-net**: The external Docker network shared by all services routed through Traefik.
- **ctc-django-main**: The existing primary Django container in `ctc-research/docker-compose.yml`, used as the reference pattern for the Core_Container.
- **Nginx_Docsify_Config**: An nginx server block configuration enabling docsify client-side routing (try_files → index.html).

---

## Requirements

### Requirement 1: Docs Container — Service Definition

**User Story:** As a developer, I want a `docs` container serving the ctc-research markdown documentation, so that the documentation is accessible via the existing Traefik routes without changing the Traefik dynamic config.

#### Acceptance Criteria

1. THE Docs_Container SHALL be defined as a service in `ctc-research/docker-compose.yml` with container name `docs`.
2. THE Docs_Container SHALL use the `nginx:alpine` base image.
3. THE Docs_Container SHALL mount the ctc-research project's `docs/` directory to `/usr/share/nginx/html` as a read-only volume.
4. THE Docs_Container SHALL expose port 80 internally (no host port binding).
5. THE Docs_Container SHALL join the external `traefik-net` network.
6. THE Docs_Container SHALL restart unless explicitly stopped (`restart: unless-stopped`).

### Requirement 2: Docs Container — Nginx Configuration

**User Story:** As a developer, I want the docs container to correctly serve docsify markdown files, so that client-side routing works and markdown files are served with the correct content type.

#### Acceptance Criteria

1. THE Docs_Container SHALL use a dedicated nginx configuration file (`compose/nginx/ctc-docsify.conf`) mounted at `/etc/nginx/conf.d/default.conf`.
2. WHEN a request is made to a path that does not match a static file, THE Nginx_Docsify_Config SHALL fall back to serving `/index.html` to support docsify client-side routing.
3. WHEN a request is made for a `.md` file, THE Nginx_Docsify_Config SHALL respond with `Content-Type: text/markdown; charset=utf-8`.
4. THE Nginx_Docsify_Config SHALL enable gzip compression for `text/plain`, `text/css`, `text/javascript`, and `application/json` MIME types.
5. THE Nginx_Docsify_Config SHALL listen on port 80.

### Requirement 3: Docs Container — Traefik Routing

**User Story:** As a developer, I want the docs container to be reachable via the existing Traefik routes, so that no changes to the Traefik dynamic config are required.

#### Acceptance Criteria

1. THE Docs_Container SHALL use container name `docs` so that the existing `docs-service` entry in `compose/traefik/dynamic/docs.yml` (which routes to `http://docs:80`) resolves correctly without modification.
2. WHEN Traefik receives a request for `core.structa.cloud`, `site-docs.structa.cloud`, `site.structa.cloud`, or `lms.structa.cloud`, THE Traefik SHALL route the request to the Docs_Container on port 80.

### Requirement 4: Core Container — Service Definition

**User Story:** As a developer, I want a `ctc-core` container running the ctc-research Django core app, so that the core application is independently deployable and accessible via Traefik.

#### Acceptance Criteria

1. THE Core_Container SHALL be defined as a service in `ctc-research/docker-compose.yml` with container name `ctc-core`.
2. THE Core_Container SHALL use the same `build` configuration as `ctc-django-main` (context `.`, dockerfile `./compose/django/Dockerfile`).
3. THE Core_Container SHALL join the external `traefik-net` network.
4. THE Core_Container SHALL restart unless explicitly stopped (`restart: unless-stopped`).
5. THE Core_Container SHALL load environment variables from the `.env` file via `env_file`.
6. THE Core_Container SHALL set `APP_MODULE=core.asgi:application` to target the core ASGI entry point.
7. THE Core_Container SHALL expose port 5080 internally (distinct from `ctc-django-main`'s port 5070).

### Requirement 5: Core Container — Environment Configuration

**User Story:** As a developer, I want the core container to use the same environment variable conventions as ctc-django-main, so that configuration is consistent and predictable.

#### Acceptance Criteria

1. THE Core_Container SHALL set `RUNNING_ENV=docker`, `SERVER_ENV=production`, `DEBUG=False`.
2. THE Core_Container SHALL set `PORT=5080` and `WORKERS=4`.
3. THE Core_Container SHALL set `DJANGO_SETTINGS_MODULE=configs.settings`.
4. THE Core_Container SHALL set `DB_HOST=postgres` and `DB_NAME=db_ctc` to share the same database as `ctc-django-main`.
5. THE Core_Container SHALL set `REDIS_URL` pointing to the shared Redis instance on a distinct database index (e.g., `/5`).
6. THE Core_Container SHALL set `RUN_SETUP=false` to skip redundant migrations already run by `ctc-django-main`.
7. THE Core_Container SHALL set `ALLOWED_HOSTS` to include the core domain.

### Requirement 6: Core Container — Traefik Routing

**User Story:** As a developer, I want the core container to be accessible via a dedicated domain through Traefik, so that it is reachable over HTTPS with TLS termination.

#### Acceptance Criteria

1. A new Traefik dynamic config file SHALL be created at `compose/traefik/dynamic/ctc-core.yml`.
2. WHEN Traefik receives an HTTP request for the core domain, THE Traefik SHALL redirect it to HTTPS.
3. WHEN Traefik receives an HTTPS request for the core domain, THE Traefik SHALL route it to the Core_Container at `http://ctc-core:5080`.
4. THE ctc-core.yml Traefik config SHALL configure TLS using the `letsencrypt` cert resolver.
5. THE ctc-core.yml Traefik config SHALL apply `compress` and `security-headers` middlewares on the HTTPS router.
6. WHEN Traefik receives a request for `/static/` or `/media/` paths on the core domain, THE Traefik SHALL route it to `ctc-nginx` for static/media file serving, consistent with the pattern used by `ctc-main.yml`.

### Requirement 7: Healthchecks

**User Story:** As an operator, I want both containers to have healthchecks, so that Docker and Traefik can detect unhealthy containers.

#### Acceptance Criteria

1. THE Docs_Container SHALL have a healthcheck that performs an HTTP GET to `http://localhost/` and succeeds with a 2xx response.
2. THE Core_Container SHALL have a healthcheck that performs an HTTP GET to `http://localhost:5080/health/` and succeeds with a 2xx response, consistent with the pattern used by `ctc-django-main`.
3. IF the Docs_Container healthcheck fails 3 consecutive times, THEN THE Docker SHALL mark the container as unhealthy.
4. IF the Core_Container healthcheck fails 3 consecutive times, THEN THE Docker SHALL mark the container as unhealthy.
