# Minimal Solid Architecture (requirements)

This document describes a minimal, production-ready architecture for hosting the two websites with shared configuration and assets.

Core principles

- Single canonical `websites/configs` package used by both sites; avoid per-site symlinks or duplicated config files.
- Per-site Docker images built from the same `Dockerfile.web` with a `PROJECT_PATH` build-arg.
- Persistent `media` volume for user uploads; use MinIO (S3-compatible) for scalability in production.
- Static assets produced by webpack are collected into `STATIC_ROOT` via `collectstatic` and served by Nginx or CDN.
- Use Gunicorn (or Uvicorn) behind Nginx / Traefik; ensure ASGI handling for websockets.

Minimal components

- `Dockerfile.web` (build stage: npm build; runtime stage: copy bundles + install requirements).
- `docker-compose.websites.yml` with services:
  - `web-ctc` and `web-structa` (site containers)
  - `db` (Postgres)
  - `cache` (Redis)
  - `minio` (optional for media)
  - `nginx` (optional; can be replaced by Traefik)

Volumes and mounts

- `configs` mounted read-only into containers at `/app/websites/configs`.
- `media` as a named volume shared or attached to MinIO.
- `static` optional volume for Nginx to serve pre-collected static files.

Operational checks (pre-deploy)

1. `npm ci` and `npm run build:<site>` complete with exit 0 and produce `bundles.json`.
2. `PROJECT_PATH=<site> python manage.py build_assets --no-input` produces bundles under `STATIC_ROOT`.
3. `python manage.py collectstatic --no-input` populates `STATIC_ROOT`.
4. `python manage.py check` passes with zero critical errors.
5. Health endpoint responds (e.g., `/health/` returns 200).

Security & organizational tips

- Do not commit secrets; use environment or secret managers. Keep `.bak` backups outside commits unless necessary.
- Centralize configuration and document any environment overrides clearly in `websites/configs/README.md`.
- Add CI gating on build, test, and asset generation steps to catch regressions early.
