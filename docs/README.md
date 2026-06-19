# Django Multi-Project Ecosystem Documentation

> Comprehensive documentation for ctc-research.com, structa.cloud, and shared packages

## Quick Links

### 🚀 Getting Started
- [Ecosystem Overview](ecosystem/README.md) - Start here for the big picture
- [Ecosystem Getting Started](ecosystem/getting-started/) - Setup guides
- [structa.cloud Guide](structa-cloud/) - Alliance Platform docs
- [ctc-research.com Guide](ctc-research/) - Research Platform docs

### 📦 Packages
- [Packages Overview](packages/README.md) - Shared packages
- [django-osoul](packages/django-osoul/) - Pure Django foundation
- [django-rseal](packages/django-rseal/) - Wagtail automation
- [django-grep](packages/django-grep/) - Testing infrastructure
- [nawaai](packages/nawaai/) - AI toolkit

### 🛠️ Development
- [Development Guide](ecosystem/development/) - Workflows and standards
- [Deployment Guide](ecosystem/deployment/) - Deployment procedures
- [Architecture](ecosystem/architecture/) - System design

### 🔧 Shared Resources
- [Styling Guide](shared/styling/) - CSS and theming
- [Testing Guide](shared/testing/) - Testing procedures
- [Troubleshooting](shared/troubleshooting/) - Common issues
- [Scripts](shared/scripts/) - Utility scripts

---

## Project Structure

```
docs/
├── ecosystem/           # Shared ecosystem documentation
│   ├── architecture/   # System design
│   ├── deployment/     # Deployment guides
│   ├── development/    # Workflows
│   └── getting-started/# Setup guides
├── ctc-research/        # ctc-research.com specific
│   ├── api/            # API docs
│   ├── getting-started/# Setup
│   ├── lms/            # LMS features
│   └── reference/      # Reference
├── structa-cloud/       # structa.cloud specific
│   ├── alliance/       # Alliance module
│   ├── getting-started/# Setup
│   ├── plugins/        # Plugin architecture
│   └── reference/      # Reference
├── packages/           # Shared packages
│   ├── django-osoul/  # Django foundation
│   ├── django-rseal/  # Wagtail automation
│   ├── django-grep/   # Testing
│   └── nawaai/        # AI toolkit
├── shared/             # Cross-cutting concerns
│   ├── scripts/       # Utility scripts
│   ├── styling/       # CSS guides
│   ├── testing/       # Testing guides
│   └── troubleshooting/# Issues
└── infrastructure/     # Infrastructure docs
    ├── docker/        # Docker setup
    ├── nginx/         # Nginx config
    ├── traefik/       # Traefik config
    ├── postgres/      # Database
    ├── MAKEFILE_DELEGATION_TREE.md # Orchestration docs
    └── SHARED_TASKS_RECOMMENDATIONS.md # Shared Services Docs

---

## Ecosystem Overview

This workspace contains a multi-repository Django ecosystem with:

| Project | Description | Type |
|---------|-------------|------|
| **ctc-research.com** | Xellent LMS platform | Django + Wagtail |
| **structa.cloud** | Alliance Platform | Django + Wagtail |
| **django-osoul** | Pure Django foundation | Shared package |
| **django-rseal** | Wagtail automation | Shared package |
| **django-grep** | Testing infrastructure | Shared package |
| **nawaai** | AI/MCP toolkit | Shared package |

### Dependency Direction

```
ctc-research.com  →  django-osoul, django-grep, django-rseal, nawaai
structa.cloud     →  django-osoul, django-grep, django-rseal, nawaai
django-rseal      →  django-osoul
django-grep       →  (standalone)
nawaai            →  (standalone)
```

---

## Getting Started

### 1. Choose Your Path

**For ctc-research.com:**
```bash
cd ctc-research.com
uv sync --all-extras
```

**For structa.cloud:**
```bash
cd structa.cloud
uv sync --all-extras
```

**For packages:**
```bash
cd venv/libs/django-osoul && uv sync
cd venv/libs/django-rseal && uv sync
cd venv/libs/django-grep && uv sync
cd venv/libs/nawaai && uv sync
```

### 2. Environment Setup

Copy environment examples:
```bash
cp ctc-research.com/.env.example ctc-research.com/.env
cp structa.cloud/.env.example structa.cloud/.env
```

### 3. Database Setup

```bash
docker compose up -d postgres
cd ctc-research.com && uv run python manage.py migrate
cd structa.cloud && uv run python manage.py migrate
```

---

## Common Commands

### Testing
```bash
# Run all tests
python3 shared/scripts/run_all_tests.py

# Test specific project
cd ctc-research.com && uv run pytest tests/ -v
cd structa.cloud && uv run pytest tests/ -v
```

### Validation
```bash
# Run all validation checks
python3 shared/scripts/validate_system.py

# Check architecture boundaries
import-linter --config .importlinter
```

### Docker
```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down
```

---

## Health Check Endpoints

- `GET /health/` - Overall health status
- `GET /health/database/` - Database connectivity
- `GET /health/assets/` - Static assets availability
- `GET /health/media/` - Media files availability

---

## Documentation Standards

### File Naming
- Use **kebab-case** for all documentation files
- Use **01-** prefix for sequential reading order
- Use **README.md** for section overviews

### Section Structure
Each section should have:
1. `README.md` - Overview and quick links
2. Numbered files (01-, 02-, etc.) - Sequential guides
3. Cross-references to related content

### Linking
- Use relative paths for internal links
- Use absolute paths for external links
- Use anchor links for section navigation

---

## Contributing

1. Follow the [development workflow](ecosystem/development/01-development-workflow.md)
2. Run [validation scripts](shared/scripts/README.md) before committing
3. Update documentation in the appropriate section
4. Use the [coding standards](ecosystem/development/coding_standards_and_conventions.md)

---

## License

See [LICENSE.md](LICENSE.md) for details.

---

**Last Updated**: April 2026

**Start with**: [Ecosystem Overview](ecosystem/README.md)
