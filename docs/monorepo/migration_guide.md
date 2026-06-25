# Migration Guide

Phase-by-phase migration notes for the structa.cloud monorepo.

---

## Phase 3: utilities.py → django-osoul

**When**: If you have code importing from `applications/utilities.py`

The file has been deleted. Update your imports:

```python
# Before
from utilities import get_file_extension, detect_language

# After
from django_osoul.site.utils import get_file_extension, detect_language
```

Full mapping: [packages/django-osoul/usage.md](../packages/django-osoul/usage.md)

---

## Phase 4: Docker Compose Consolidation

**When**: Upgrading from pre-2026-06-16 Docker Compose setup

### Removed files

These per-site compose files were deleted (consolidated into `docker-compose.applications.yml`):

- `compose/docker-compose.ctc-research.yml` — removed
- `compose/docker-compose.lms-demo.yml` — removed
- `compose/docker-compose.vresume.yml` — removed

### What changed

All website services now live in `compose/docker-compose.applications.yml`. The `version:` attribute was removed from all compose files (obsolete in Docker Compose v2+).

### Network migration

All services now share `common` for internal communication. Cross-file `depends_on` references were removed (Docker Compose include limitation — services discover each other via network names).

### Upgrade steps

```bash
# Stop old containers
docker compose down

# Pull new config
git pull

# Restart with consolidated compose
docker compose up -d --build
```

---

## Phase 9: MkDocs → Docsify

**When**: If you have the old MkDocs docs server running

### What changed

| Before (MkDocs) | After (Docsify) |
|-----------------|-----------------|
| Python + `mkdocs-material` | `nginx:1.27-alpine` static serve |
| Port 8000 (Python server) | Port 80 (nginx) |
| Requires `mkdocs build` | No build step — client-side rendering |
| `mkdocs.yml` config | `docs/index.html` + `docs/_sidebar.md` |
| `compose/docs/Dockerfile` → python:3.12-slim | `compose/docs/Dockerfile` → nginx:1.27-alpine |

### Migrate docs service

```bash
# Stop old MkDocs container
docker compose -f applications/compose/docker-compose.docs.yml down

# Rebuild with new Docsify Dockerfile
docker compose -f applications/compose/docker-compose.docs.yml up -d --build
```

### Sidebar format

The old `mkdocs.yml` nav is replaced by `docs/_sidebar.md`:

```markdown
* [Home](README.md)
* **Section**
  * [Page](section/page.md)
```

### Directory structure after migration

```
docs/
├── index.html          ← Docsify bootstrap (replaces mkdocs.yml)
├── _sidebar.md         ← Navigation (replaces nav: in mkdocs.yml)
├── README.md           ← Home page
├── architecture/       ← Architecture docs
├── design/             ← Design system docs
├── development/        ← Developer guides
├── reports/            ← Audit & backlog reports
├── user_guide/         ← Content editor guides
├── packages/           ← Library docs
├── ecosystem/          ← Site-specific docs
├── infrastructure/     ← Infrastructure docs
├── monorepo/           ← Phase tracking
└── Dockerfile          ← nginx:1.27-alpine
```

---

## ctc-research → lms-demo Structure Diff

See [migration-record.md](../migration-record.md) for the detailed structural diff between the `ctc-research` and `lms-demo` site layouts.

---

## Language Support (Phase 7 — Pending)

When Phase 7 is complete, language switching will require:

```python
# Add to INSTALLED_APPS
'django_osoul',

# Add to MIDDLEWARE
'django_osoul.middleware.LanguageMiddleware',

# Add to TEMPLATES context_processors
'django_osoul.context_processors.language_context',
```

Reference: `/data/refrences/django-osoul/`
