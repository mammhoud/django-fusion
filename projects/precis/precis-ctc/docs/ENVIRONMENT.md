# CTC Research — Environment & Redeploy

> **Canonical project:** `projects/precis/precis-ctc/`
> **Public domain:** `ctc-research.com`
> **Dispatcher aliases:** `WEBSITE=ctc`, `WEBSITE=precis-ctc`, `WEBSITE=ctc-website`, `WEBSITE=ctc-research.com`

<!-- AI-generated: review needed -->

## 1. Requirements

| Requirement | Purpose | Remarks |
|---|---|---|
| Python 3.11+ | Django/Wagtail backend and management commands | Use the repository’s `uv` workflow where available |
| uv | Python environment and locked dependencies | The checkout’s old site-local venv may be stale; recreate through the approved workspace workflow |
| Node.js 20/22 + npm 10+ | Astro frontend and webpack bundles | Frontend dependencies live in `frontend/`; Django-side asset dependencies live at the CTC project root |
| Docker Compose | Backend, Dramatiq worker, scheduler, frontend, proxy | Required for the production-like stack |
| PostgreSQL | CTC database | Runtime database is `db_precis_ctc`; do not point CTC at Precis/LMS data |
| Redis | cache, Dramatiq broker, queues | `REDIS_URL` and `DRAMATIQ_BROKER_URL` use separate logical databases |
| Traefik + shared Nginx | HTTPS routing and shared static/media files | Shared proxy must be on the external `traefik-net` and `common` networks |

## 2. Environment variable reference

Values below are names and safe defaults only. A matching secret-free template
is available at [`../.env.example`](../.env.example). Secret values belong in
the deployment secret store or an ignored `.env` file; never commit them.

### Site and process

| Variable | Example/default | Required | Remarks |
|---|---|:---:|---|
| `WEBSITE` | `precis-ctc` | yes | Canonical runtime selector |
| `DJANGO_SITE` | `precis-ctc` | yes | Django site identity |
| `PROJECT_PATH` | `precis-ctc` | yes | Container/build project path |
| `SITE_DOMAIN` | `ctc-research.com` | yes | Public domain |
| `SITE_PORT` | `443` | no | External site port |
| `HOST` | `0.0.0.0` | no | Bind address |
| `PORT` | `5070` | no | Backend container port |
| `DEBUG` | `false` | yes in production | Must remain false in production |
| `SERVER_TYPE` | `uvicorn` | no | ASGI/WSGI server selection |
| `WORKERS` | `4` | no | Backend worker count |
| `LOG_LEVEL` | `info` | no | Runtime log level |
| `ALLOWED_HOSTS` | site host list | yes | Include the canonical and archive hosts only when required |
| `CSRF_TRUSTED_ORIGINS` | HTTPS site origins | yes | Include scheme, not only hostname |

### Database and queues

| Variable | Example/default | Required | Remarks |
|---|---|:---:|---|
| `DB_TYPE` | `postgres` | yes | CTC production backend |
| `DB_HOST` | `postgres` | yes | Compose service name |
| `DB_PORT` | `5432` | no | PostgreSQL port |
| `DB_NAME_CTC` | `db_precis_ctc` | yes | CTC database selector |
| `DB_NAME` | `db_precis_ctc` | yes | Effective backend database name |
| `DB_USER` | `admin` | yes | Use secret-store value |
| `DB_PASSWORD` | unset | yes | Secret; never print or commit |
| `REDIS_URL` | `redis://:<secret>@default-redis:6379/0` | yes | Cache/general task database |
| `DRAMATIQ_BROKER_URL` | `redis://:<secret>@default-redis:6379/1` | yes | Single task execution boundary |
| `REDIS_PASSWORD` | unset | yes | Compose interpolation secret |
| `DRAMATIQ_PROCESSES` | `2` | no | Worker process count |
| `DRAMATIQ_THREADS` | `4` | no | Worker thread count |
| `FUSION_TASK_BACKEND` | `dramatiq` | yes | Keep Dramatiq as the execution boundary |
| `FUSION_TASK_MODULES` | comma-separated actor modules | yes | Email, content, course, campaign, and system actors |

### Public API and frontend build

| Variable | Example/default | Required | Remarks |
|---|---|:---:|---|
| `PUBLIC_SITE_URL` | `https://ctc-research.com` | yes | Astro canonical URL |
| `PUBLIC_BUILD_API_URL` | `https://ctc-research.com` | yes for API builds | Build-time API origin; build has fail-soft fallbacks |
| `PUBLIC_FUSION_API_URL` | empty or backend origin | no | Runtime Fusion API origin |
| `PUBLIC_ENABLE_BACKEND` | `true` | no | Enables live backend roads |
| `FUSION_RENDER_FIRST` | `true` | no | Keeps HTML/fragment road available |
| `MEDIA_URL` | `/media/` | no | Relative path for proxy compatibility |
| `STATIC_URL` | `/static/` | no | Relative path for proxy compatibility |
| `MEDIA_ROOT` | `/app/media` in Compose | yes | Shared host tree is mounted here |
| `CTC_MEDIA_SOURCE_DIR` | `/app/media/media` | no | Restored archive source directory |
| `CTC_MEDIA_CONTENT_DIR` | `/app/media/ctc-content` | no | Prepared website copy directory |
| `CTC_MEDIA_DUMP_IMAGE_DIR` | `/app/media/original_images` | no | Wagtail dump-compatible image aliases |
| `CTC_MEDIA_MANIFEST_PATH` | CTC fixture manifest | no | Source-controlled archive metadata |
| `STATIC_ROOT` | `/app/precis-ctc/assets/staticfiles` | yes | Named collected-static volume |

### Email

| Variable | Example/default | Required | Remarks |
|---|---|:---:|---|
| `EMAIL_BACKEND` | Django SMTP backend | yes for delivery | Use console backend only in local development |
| `EMAIL_HOST` | `smtp.gmail.com` | yes for Gmail | Use an app password, not a personal password |
| `EMAIL_PORT` | `587` | yes | STARTTLS |
| `EMAIL_USE_TLS` | `true` | yes | Do not combine with implicit SSL on port 587 |
| `EMAIL_USE_SSL` | `false` | yes | Use true only with the appropriate SSL port |
| `EMAIL_HOST_USER` | approved sender address | yes | Secret-store value |
| `EMAIL_HOST_PASSWORD` | unset | yes | Secret; never commit or print |
| `DEFAULT_FROM_EMAIL` | approved sender address | yes | Must align with the authenticated sender/provider policy |
| `SERVER_EMAIL` | approved sender address | no | Error notification sender |
| `EMAIL_TEST_RECIPIENT` | approved test mailbox | no | Use only for an explicitly authorized test |

The Gmail app password supplied during the session is intentionally not
recorded in this document or any repository file.

## 3. Shared asset topology

```text
projects/assets/
├── media/
│   └── ctc-research/
│       ├── media/              # restored CTC archive source
│       ├── ctc-content/        # normalized website copy (prepared)
│       └── original_images/    # dump-compatible Wagtail image paths
├── bundles/
│   └── ctc-research/          # webpack output and bundles.json
└── static/                    # shared static source files
```

The CTC backend writes media to `/app/media` in Compose. Run
`python manage.py prepare_ctc_media` to prepare the restored archive from
`/app/media/media/` into `/app/media/ctc-content/` and create aliases in
`/app/media/original_images/`; this command does not load the database dump.
The shared proxy reads the same host tree at `/var/www/media/ctc-research`.
Collected static files are
mounted at `/var/www/sites/ctc-research/static`; Nginx exposes:

- `/media/ctc-research/`
- `/static/bundles/ctc-research/`
- `/sites/ctc-research/static/`
- `/static/` through the host-selected static root

## 4. Checks and redeploy

### Local checks

```bash
cd projects/precis/precis-ctc/frontend
npm run check

cd ../../../../
python3 application/scripts/staging/verify_ctc_assets.py --site precis-ctc

cd projects/precis/precis-ctc
python3 scripts/generate_locales.py --dry-run
```

Use the repository’s normal `uv`/pytest command for backend tests when the
workspace environment is available. Do not install packages globally merely to
run a local check.

### Full CTC stack redeploy

```bash
cd projects/precis/precis-ctc
make redeploy
```

This target runs backend and frontend checks, builds `backend`, `worker`, and
`frontend`, then recreates `backend`, `worker`, `scheduler`, and `frontend`.
It does not remove volumes and does not load/replace fixtures.

Dispatcher form:

```bash
cd projects
make redeploy-with-stack WEBSITE=precis-ctc
```

The existing dispatcher command `make redeploy WEBSITE=precis-ctc` remains the
web-service deployment path. Use `redeploy-with-stack` when the worker and
scheduler must be recreated too.

### Static and bundle release order

```bash
cd projects/precis/precis-ctc
make build-assets
cd backend
make collectstatic
```

Build bundles before `collectstatic`; do not edit generated `bundles.json` or
hashed output by hand.

## 5. Safety and rollback

- Do not run `docker compose down --volumes` during a normal redeploy.
- Do not pass `FORCE_LOAD_DUMPS=true` or `load_data --replace` against a shared database without an approved backup and change window.
- If the new stack is unhealthy, inspect `docker compose ps` and service logs, then roll back the image/configuration change; preserve the database and shared media volume.
- Verify proxy paths after a rollout with a non-sensitive public media asset and `/health/`.

## Remarks & Notes

- This environment map describes the current CTC Compose wiring; deployment platforms may inject equivalent variables through a different secret manager.
- The host-side shared media directory is runtime content and may be absent in a clean clone until fixtures/media backup restoration is performed.
- Never use the Gmail test recipient or sender credentials as a substitute for a production mail approval process.
