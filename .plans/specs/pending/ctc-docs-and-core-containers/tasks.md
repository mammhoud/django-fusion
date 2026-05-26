# Implementation Plan: ctc-docs-and-core-containers

**Category Context: Documentation**
- **Category**: Docs
- **Scope**: Documentation systems, content management, API documentation, user guides
- **Related Specs**: comprehensive-project-documentation, ctc-docs-and-core-containers, docs-plugin-enhancement
- **Common Patterns**: Documentation generation, content management, plugin development, API docs
- **Avoid Duplicates**: Check existing docs specs before creating new documentation features


## Overview

Add the `docs` and `ctc-core` services to `ctc-research/docker-compose.yml`, create the supporting nginx and Traefik config files, scaffold the docsify `index.html`, update the postgres init scripts, and write property-based tests validating all four correctness properties.

## Tasks

- [ ] 1. Update postgres init scripts to create `db_structa`
  - Add `CREATE DATABASE db_structa;` to `compose/postgres/init.d/00-create-databases.sql`
  - Add `GRANT ALL PRIVILEGES ON DATABASE db_structa TO postgres;` to `compose/postgres/init.d/02-grant-permissions.sql`
  - _Requirements: 5.4 (db_structa must exist before ctc-core starts)_

- [ ] 2. Create `compose/nginx/ctc-docsify.conf`
  - [ ] 2.1 Write the nginx server block
    - `server_name _` (catch-all; Traefik handles domain routing)
    - `listen 80`
    - `root /usr/share/nginx/html`
    - `location /` with `try_files $uri $uri/ /index.html`
    - `location ~* \.md$` block setting `Content-Type "text/markdown; charset=utf-8"`
    - `gzip on` with `gzip_types text/plain text/css text/javascript application/json`
    - _Requirements: 2.1-2.5_

- [ ] 3. Scaffold `ctc-research/docs/index.html`
  - Create minimal docsify `index.html` with CDN script tags so nginx returns 200 on first deploy
  - _Requirements: 1.3 (docs/ bind mount must have a valid index.html)_

- [ ] 4. Add `docs` service to `ctc-research/docker-compose.yml`
  - [ ] 4.1 Define the `docs` service block
    - `image: nginx:alpine`
    - `container_name: docs`
    - Volume: `./docs:/usr/share/nginx/html:ro`
    - Config mount: `../compose/nginx/ctc-docsify.conf:/etc/nginx/conf.d/default.conf:ro`
    - `networks: [traefik-net]`
    - `restart: unless-stopped`
    - Healthcheck: `wget -q --spider http://localhost/`, interval 30s, timeout 10s, retries 3
    - No `ports:` mapping
    - _Requirements: 1.1-1.6, 2.1, 3.1, 7.1, 7.3_

- [ ] 5. Add `ctc-core` service to `ctc-research/docker-compose.yml`
  - [ ] 5.1 Define the `ctc-core` service block
    - `build:` same as `ctc-django-main` (context `.`, dockerfile `./compose/django/Dockerfile`)
    - `container_name: ctc-core`
    - `env_file: [.env]`
    - Environment: `RUNNING_ENV=docker`, `SERVER_ENV=production`, `DEBUG=False`, `PORT=5080`, `WORKERS=4`, `APP_MODULE=core.asgi:application`, `DJANGO_SETTINGS_MODULE=configs.settings`, `DB_HOST=postgres`, `DB_NAME=db_structa`, `REDIS_URL=redis://:${REDIS_PASSWORD:-redis_password}@redis:6379/5`, `RUN_SETUP=true`, `ALLOWED_HOSTS=${ALLOWED_HOSTS:-*}`
    - `networks: [traefik-net]`
    - `restart: unless-stopped`
    - Healthcheck: `wget -q --spider http://localhost:5080/health/`, interval 30s, timeout 10s, retries 3
    - No `ports:` mapping
    - _Requirements: 4.1-4.7, 5.1-5.7, 7.2, 7.4_

- [ ] 6. Checkpoint — Ensure docker-compose.yml is valid
  - Validate YAML syntax and confirm all required fields are present

- [ ] 7. Create `compose/traefik/dynamic/ctc-core.yml`
  - [ ] 7.1 Write the Traefik dynamic config
    - HTTP router `ctc-core-http`: redirect to HTTPS
    - HTTPS router `ctc-core-https`: service `ctc-core-service` at `http://ctc-core:5080`, middlewares `compress`, `csrf-headers`, `security-headers`, TLS certResolver `letsencrypt`
    - Assets router `ctc-core-assets`: PathPrefix `/static/` or `/media/`, service `ctc-nginx-service` at `http://ctc-nginx:80`
    - _Requirements: 6.1-6.6_

- [ ] 8. Write property-based tests in `ctc-research/tests/test_ctc_docs_and_core_containers.py`
  - [ ] 8.1 Implement test helpers: `load_compose()`, `load_traefik_config()`, `extract_redis_db_index()`, `extract_hostname()`
  - [ ] 8.2 Implement Property 1 test — container name matches Traefik service URL hostname
  - [ ] 8.3 Implement Property 2 test — Redis DB index and DB name uniqueness
  - [ ] 8.4 Implement Property 3 test — service configuration completeness
  - [ ] 8.5 Implement Property 4 test — Traefik config routing completeness

- [ ] 9. Final checkpoint — Ensure all tests pass

## Notes

- Property tests use `@given(st.just(...))` with `@settings(max_examples=100)`
- `RUN_SETUP=true` for ctc-core because it has its own `db_structa` database
- Port 5080 is confirmed free (existing: 5070 main, 5055/5056 demo, 5075/5076 rqworkers)
