# Syntara (Cypercloud) — Setup & Build Guide

> **Path:** `projects/syntara/`
> **Stack:** Django + Ceptor-AI + Monaco Editor + HTMX (webpack frontend)
> **App port:** 5073 · **Webpack dev server:** 5093

Syntara (historically *Cypercloud*) is an AI chat and customization tool:
converse with an AI, discover templates across configured sites, and modify
them with a code editor and streaming responses. It supports Ollama (local),
OpenAI, Anthropic Claude, and Google Gemini backends.

---

## 1. Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.11 | Backend runtime |
| npm | 10+ | Webpack frontend assets |
| Docker (optional) | latest | Containerized run |
| Ollama (optional) | latest | Local AI backend (default model `gemma3:4b`) |

```bash
python3 --version && npm --version
```

> Syntara is a **self-contained Django project** (own `settings.py`,
> `requirements.txt`, SQLite db) — it does not use the `projects/`
> workspace venv. Install its Python deps directly with pip.

---

## 2. Full local setup (recommended)

The Makefile bundles install → migrate → build → collectstatic:

```bash
cd projects/syntara
make setup
```

`make setup` runs, in order:

1. `make install-assets` — `npm ci` in `assets/` (webpack deps)
2. `pip install -r requirements.txt`
3. `python3 manage.py migrate`
4. `make build` — webpack production build → `assets/bundles/cypercloud/`
5. `make collectstatic` — static files into `STATIC_ROOT`

Then optionally create an admin user and start the server:

```bash
make superuser
make run                 # http://localhost:5073
```

Or do it all at once:

```bash
make run-full            # make setup && make run
```

---

## 3. Manual step-by-step

### 3.1 Python dependencies

```bash
cd projects/syntara
pip install -r requirements.txt
```

### 3.2 Frontend assets

```bash
make install-assets      # npm ci --prefix assets --include=dev
make build               # webpack production → assets/bundles/cypercloud/
```

Development variants:

```bash
make build-dev           # development build with source maps
make watch               # rebuild on file change (webpack --watch)
make dev                 # webpack dev server with HMR on :5093
```

### 3.3 Database

```bash
make migrate             # apply Django migrations
make migrate-status      # showmigrations
make superuser           # createsuperuser
```

### 3.4 Run the app

```bash
make run                 # manage.py runserver 0.0.0.0:5073
```

Verify:

```bash
curl -s http://localhost:5073/ | head -20
open http://localhost:5073/admin
```

---

## 4. Configuration (Dynaconf + env)

Copy `.env.example` → `.env` and set at minimum:

```bash
CYPERCLOUD_SECRET_KEY=generate-a-real-secret
CYPERCLOUD_DEBUG=1
CYPERCLOUD_ALLOWED_HOSTS=*
```

Optional AI backends:

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
```

Useful Make targets:

| Command | Purpose |
|---------|---------|
| `make config-check` | Verify Dynaconf config loads |
| `make config-validate` | Validate models/templates registries |
| `make config-show` | Show current settings (secret masked) |
| `make config-env` | Show environment variable defaults |

---

## 5. Tests, checks & linting

```bash
make check               # python manage.py check
make test                # manage.py test
make test-verbose        # manage.py test --verbosity=2
make lint                # ruff (or pylint fallback)
make format              # black --line-length=88
make check-deploy        # manage.py check --deploy (production readiness)
make ci                  # check + lint + test
```

---

## 6. Production build & deploy

```bash
cd projects/syntara
make build-collect       # build assets + collectstatic
make deploy              # build → collectstatic → migrate (all --noinput)
```

Run with gunicorn (default 2 workers):

```bash
WORKERS=4 make server    # via docker entrypoint or:
gunicorn server:application --bind 0.0.0.0:5073 --workers 2
```

> `server.py` is the Gunicorn entry point; `settings.py` is the Django
> settings module.

---

## 7. Docker

```bash
cd projects/syntara
make docker-build        # docker compose build
make docker-run          # up -d → http://cypercloud.localhost:5073
make docker-logs         # tail cypercloud logs
make docker-shell        # bash inside the container
make docker-migrate      # manage.py migrate inside the container
make docker-stop         # down
```

---

## 8. Database management

```bash
make migrate-new MIGRATION=chat   # makemigrations chat
make db-reset            # interactive — deletes db.sqlite3 + migrate
make clean-db            # delete db.sqlite3 only
make reset               # clean-all + db-reset (full reset)
```

---

## 9. Troubleshooting

### `No module named 'configs'`

Set `PYTHONPATH`:

```bash
export PYTHONPATH="/home/structa.cloud/core:$PYTHONPATH"
python3 manage.py runserver
```

### Ollama connection refused

Check the service and env:

```bash
curl http://localhost:11434/api/tags
echo $OLLAMA_BASE_URL   # inside Docker: http://host.docker.internal:11434
```

### Webpack bundle not found

```bash
make build
make collectstatic
```

### SQLite "database is locked"

Multiple processes on `db.sqlite3` — restart:

```bash
make docker-restart-all    # Docker path
# or locally: stop other manage.py/runserver processes first
```

### Migrations failing after switching envs

```bash
make db-reset
```

---

## See also

- [Project README](../README.md) — features, API endpoints, architecture
- [docs/spa-navigation.md](../docs/spa-navigation.md) — SPA navigation notes
- [API.md](../API.md) — API reference
- [DEPLOYMENT.md](../DEPLOYMENT.md) — deployment notes
