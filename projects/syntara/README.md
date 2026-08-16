# Cypercloud – AI Chat Customizer

> **Port:** 5073 | **Stack:** Django + Ceptor-AI + Monaco Editor + HTMX

<p align="center">
  <a href="../../docs/sites/cypercloud.md"><img src="https://img.shields.io/badge/docs-site-green" alt="Documentation"/></a>
  <a href="../../CHANGELOG.md"><img src="https://img.shields.io/badge/changelog-root-blue" alt="Changelog"/></a>
  <a href="https://github.com/mammhoud/structa.cloud"><img src="https://img.shields.io/badge/support-github-lightgrey" alt="Support"/></a>
</p>

A Django-based AI chat and customization tool with code editing, template discovery, and Ceptor-AI backend support for multi-site template modification.

## Quick Start

### Local Development

```bash
# Install dependencies
cd projects/cypercloud
make install-assets
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the dev server (port 5073)
make runserver

# Access the app
open http://localhost:5073
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose -f projects/cypercloud/docker-compose.yml up -d

# Access the app
open http://cypercloud.localhost:5073
```

## Features

### 1. Template Discovery
- Scan multiple sites for templates and components
- Display template hierarchy and page structure
- Show sections/blocks within each template

**Configured Sites:**
- CTC Research (`projects/precis-ctc/templates/`)
- LMS Demo (`projects/lms/templates/`)
- VResume (`projects/portfolio/www/pages/templates/`)

### 2. AI Chat Interface
- Real-time conversation with streaming responses
- Code editor with syntax highlighting and formatting
- Version control for generated code
- Multiple AI backend support

**Supported Models:**
- Ollama (local, self-hosted)
- OpenAI GPT
- Anthropic Claude
- Google Gemini

### 3. Ceptor-AI Integration
- AI service orchestration
- MCP (Model Context Protocol) tool execution
- Agent configuration management
- Multi-backend support

### 4. Web-Based Components
- Monaco code editor
- Bootstrap UI components
- HTMX for real-time interactions
- Event streaming (SSE) for AI responses

## Project Structure

```
cypercloud/
├── chat/                      # Django app for chat and customizer
│   ├── models.py              # Conversation, Message models
│   ├── views.py               # Chat, template discovery views
│   ├── urls.py                # Route definitions
│   ├── customizer.py          # Template catalog integration
│   ├── site_data.py           # Site scanning and template loading
│   ├── ceptor.py              # Ceptor-AI service integration
│   ├── services.py            # Business logic (ConversationService)
│   ├── constants.py           # Model choices, display names
│   └── views_stream.py        # SSE streaming endpoints
├── templates/                 # HTML templates
│   ├── chat.html              # Chat interface
│   ├── homepage.html          # Landing page
│   ├── fragments/             # HTMX fragments
│   └── ...
├── assets/                    # Frontend assets
│   ├── static/                # CSS, images, fonts
│   ├── webpack.config.js      # Webpack bundler config
│   ├── package.json           # npm dependencies
│   └── bundles/               # Generated webpack output
├── settings.py                # Django configuration
├── urls.py                    # URL dispatcher
├── server.py                  # Gunicorn entry point
├── Dockerfile                 # Multi-stage container build
├── docker-compose.yml         # Service orchestration
├── docker-entrypoint.sh       # Container startup script
├── Makefile                   # Common tasks
├── requirements.txt           # Python dependencies
├── manage.py                  # Django CLI
└── db.sqlite3                 # Local SQLite database
```

## Configuration

### Environment Variables

**Required:**
```bash
CYPERCLOUD_SECRET_KEY           # Django secret key (auto-generated in dev)
DJANGO_SETTINGS_MODULE=settings
PORT=5073
```

**Optional:**
```bash
CYPERCLOUD_DEBUG=1             # Enable debug mode
CYPERCLOUD_ALLOWED_HOSTS=*     # Allowed hostnames
CYPERCLOUD_WORKERS=2           # Gunicorn worker count
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma3:4b
```

### Django Settings (`settings.py`)

Key configuration sections:

```python
# Local apps
LOCAL_APPS = ["chat.apps.ChatConfig"]

# Configured sites for template discovery
CUSTOMIZER_APPS = [
    {"slug": "precis-ctc", "name": "CTC Research", "template_root": "..."},
    {"slug": "lms", "name": "LMS Demo", "template_root": "..."},
    {"slug": "VResume", "name": "VResume", "template_root": "..."},
]

# Local database (SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "db.sqlite3",
    }
}

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = "staticfiles/"
```

### Adding More Sites

Edit `settings.py` in `CUSTOMIZER_APPS`:

```python
CUSTOMIZER_APPS = [
    {
        "slug": "my-site",
        "name": "My Site",
        "template_root": _WORKSPACE_DIR / "my-site" / "templates",
    },
]
```

Then restart the app:
```bash
docker-compose restart cypercloud
# or locally: python manage.py runserver
```

## API Endpoints

### Chat Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Chat interface + recent conversations |
| `/` | POST | Create new conversation |
| `/chat/{id}/` | GET | View conversation |
| `/chat/{id}/` | POST | Send message |
| `/chat/{id}/stream/` | GET | SSE stream for Ollama responses |
| `/chat/{id}/ceptor-stream/` | GET | SSE stream for Ceptor AI responses |
| `/chat/{id}/render-markdown/` | POST | Convert markdown to HTML |

### Template Discovery Endpoints

| Endpoint | Method | Response |
|----------|--------|----------|
| `/api/websites/` | GET | List configured sites |
| `/api/pages/{website_slug}/` | GET\|JSON | Pages/templates for site |
| `/fragments/page-navigator/` | GET | HTMX page nav fragment |
| `/fragments/page-cards/{website_slug}/` | GET | HTMX page grid fragment |
| `/fragments/page-sections/{website_slug}/{page_path}/` | GET | HTMX sections fragment |
| `/fragments/sidebar/{website_slug}/` | GET | Template sidebar fragment |

### Ceptor-AI Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ceptor/health/` | GET | Check Ceptor AI status |
| `/api/ceptor/config/preload/` | GET | Get AI configs (agents, models) |
| `/api/ceptor/ai/complete/` | POST | AI completion (stream or non-stream) |
| `/api/ceptor/mcp/{tool_name}/` | GET | Execute MCP tool |

### Example: AI Completion

**Streaming:**
```bash
curl -X POST http://localhost:5073/api/ceptor/ai/complete/?stream=1 \
  -H "Content-Type: application/json" \
  -d '{
    "backend": "openai",
    "model": "gpt-4o",
    "prompt": "Generate a React component for..."
  }'
```

**Non-streaming:**
```bash
curl -X POST http://localhost:5073/api/ceptor/ai/complete/ \
  -H "Content-Type: application/json" \
  -d '{
    "backend": "ollama",
    "model": "gemma3:4b",
    "prompt": "Explain Vue.js reactivity"
  }'
```

## Common Tasks

### View Conversations

```bash
# Django shell
python manage.py shell

# Inside shell:
from chat.models import Conversation
Conversation.objects.all().order_by('-created_at')[:10]
```

### Reset Database

```bash
# Remove old database
rm db.sqlite3

# Fresh migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Build Frontend Assets

```bash
# Production build
make build

# Development build with source maps
make build-dev

# Watch mode (rebuilds on changes)
make watch

# Webpack dev server with HMR
make dev
```

### Collect Static Files

```bash
# Collect to STATIC_ROOT
make collectstatic

# Build + collect in one command
make build-collect
```

### Full Deployment

```bash
# Build → collectstatic → migrate
make deploy
```

### Access Django Shell

```bash
make shell
# or
python manage.py shell
```

## Docker Commands

### Build

```bash
# Build image from projects/ context
docker build -f cypercloud/Dockerfile -t cypercloud:latest .

# Or use docker-compose
docker-compose -f cypercloud/docker-compose.yml build
```

### Run

```bash
# Start service (detached)
docker-compose -f cypercloud/docker-compose.yml up -d

# View logs
docker-compose -f cypercloud/docker-compose.yml logs -f cypercloud

# Run one-off command
docker-compose -f cypercloud/docker-compose.yml exec cypercloud python manage.py shell

# Stop service
docker-compose -f cypercloud/docker-compose.yml down
```

### Database & Migrations

```bash
# Inside container: apply migrations
docker-compose -f cypercloud/docker-compose.yml exec cypercloud python manage.py migrate

# Fresh database
docker-compose -f cypercloud/docker-compose.yml exec cypercloud python manage.py migrate --run-syncdb

# Create superuser
docker-compose -f cypercloud/docker-compose.yml exec cypercloud python manage.py createsuperuser
```

## Troubleshooting

### "No module named 'configs'"

**Cause:** Running outside container without proper Python path setup.

**Fix:** Set `PYTHONPATH`:
```bash
export PYTHONPATH="/home/structa.cloud/core:$PYTHONPATH"
python manage.py runserver
```

### "Connection refused" on Ollama

**Cause:** Ollama service not running or wrong URL.

**Fix:** Check environment variable:
```bash
# Inside container
echo $OLLAMA_BASE_URL  # Should be http://host.docker.internal:11434 on Docker

# Outside container (local dev)
curl http://localhost:11434/api/tags
```

### Webpack bundle not found

**Cause:** Assets not built.

**Fix:**
```bash
make build
make collectstatic
```

### Database locked (SQLite)

**Cause:** Multiple processes accessing db.sqlite3 simultaneously.

**Fix:** Restart the service:
```bash
docker-compose -f cypercloud/docker-compose.yml restart cypercloud
```

## Development Workflow

### Add a New View

1. Define in `chat/views.py`
2. Register in `chat/urls.py`
3. Create template in `templates/`
4. Add to navigation if needed

### Modify Template Catalog

1. Edit `CUSTOMIZER_APPS` in `settings.py`
2. Or update `site_data.py` for dynamic discovery

### Add AI Backend

1. Update `constants.py` with model choices
2. Add backend handler in `ceptor.py`
3. Update views to support new backend

### Frontend Changes

1. Modify `.scss` or `.js` in `assets/static/`
2. Run `make watch` during development
3. Build for production: `make build`
4. Collect static: `make collectstatic`

## Performance Notes

- **SQLite:** Fine for development; consider PostgreSQL for production
- **Webpack:** Production builds are optimized; dev builds include source maps
- **Gunicorn:** Uses uvicorn workers for async support; 2 workers by default
- **Workers:** Auto-recycle after 1000 requests to flush stale caches
- **Static Files:** Served by Nginx in production, Django dev server in local dev

## Security Considerations

- **CSRF Protection:** Enabled by default; POST requests require valid token
- **Session Security:** Uses Django session framework with secure cookies
- **Secret Key:** Must be set to random value in production
- **Debug Mode:** Should be OFF in production
- **Allowed Hosts:** Configure for your domain

## Integration with Structa Cloud

Cypercloud integrates with the larger Structa ecosystem:

- **Shared Libraries:** `django-fusion`, `ceptor-ai` via local imports
- **Shared Templates:** Can load templates from `projects/assets/templates/`
- **Shared Settings:** Uses `configs.site.configure_site_environment()`
- **Multi-Site:** Discovers templates from CTC Research, LMS Demo, VResume
- **Docker Network:** Connects to `common` and `traefik-net` networks

## Contributing

- Follow PEP 8 for Python code
- Use Black formatting (88 char lines)
- Add tests for new features
- Document API changes
- Run `make check` before committing

## License

Part of Structa Cloud. See root LICENSE file.

<!-- @tested Cypercloud - Docker build, Django checks, migrations, AI chat endpoints tested -->
