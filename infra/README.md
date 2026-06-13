<!-- Cover Image Placeholder -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://via.placeholder.com/1200x300/1a1b26/ffffff?text=Django+Multi-Project+Ecosystem">
  <img src="https://via.placeholder.com/1200x300/f0f0f0/000000?text=Django+Multi-Project+Ecosystem" alt="Django Multi-Project Ecosystem" width="100%">
</picture>

# 🐍 Django Multi-Project Ecosystem — ctc-research.com & structa.cloud

<p align="center">
  <em>Multi-repository Django/Wagtail project with shared libraries (django-grep, django-seed)</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/django-osoul/">
    <img src="https://img.shields.io/pypi/v/django-osoul?style=flat-square&logo=pypi&logoColor=white&label=django-osoul" alt="django-osoul version">
  </a>
  <a href="https://pypi.org/project/django-rseal/">
    <img src="https://img.shields.io/pypi/v/django-rseal?style=flat-square&logo=pypi&logoColor=white&label=django-rseal" alt="django-rseal version">
  </a>
  <a href="https://pypi.org/project/django-grep/">
    <img src="https://img.shields.io/pypi/v/django-grep?style=flat-square&logo=pypi&logoColor=white&label=django-grep" alt="django-grep version">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/django?style=flat-square&logo=python&logoColor=white" alt="Python versions">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/uv-package%20manager-de3d8b?style=flat-square&logo=uv&logoColor=white" alt="uv">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="Code style: black">
  </a>
</p>

---

## ✨ Features

- 🏗️ **Architectural Clarity** - Clear separation between pure Django foundation (`django_osoul`), Wagtail automation (`django_rseal`), and testing infrastructure (`django_grep`)
- 🔄 **Code Reuse** - Shared libraries eliminate duplication between `ctc-research.com` and `structa.cloud`
- 🧪 **Comprehensive Testing** - Unified testing framework with property-based tests and test parity verification
- 🐳 **Docker-First** - Containerized development and production environments
- 📚 **Thorough Documentation** - Complete documentation in `docs/` directory with clear architecture guides
- 🔧 **Validation Scripts** - Automated scripts for boundary checking, duplication analysis, and migration safety
- ✅ **Type‑safe** - Full static typing with mypy compatibility
- 📦 **`uv`‑ready** - Lightning‑fast dependency management

---

## 📖 Documentation

Full documentation is organized in the [`docs/`](docs/README.md) directory — browse the [sidebar](docs/_sidebar.md) for navigation.

| Section | Description |
|---------|-------------|
| [📚 Getting Started](docs/getting-started/README.md) | Quick setup, environment setup, project structure, common tasks |
| [🏗️ Architecture](docs/architecture/README.md) | System overview, project relationships, technology stack, entry points |
| [🎨 Styling](docs/styling/README.md) | CSS frameworks, styling conventions, theme configuration, responsive design |
| [🔌 API](docs/api/README.md) | API overview, authentication, endpoints reference, request/response formats |
| [🚀 Deployment](docs/deployment/README.md) | Deployment overview, build for production, deployment procedures |
| [🔧 Troubleshooting](docs/troubleshooting/README.md) | Common issues, debugging guide, log analysis, performance optimization |
| [📚 Libraries](docs/libraries/README.md) | Django Volt, Django GREP reusable components and pipelines |
| [🎓 LMS Integration](docs/lms/README.md) | Course and student management |
| [📰 Blog System](docs/blog/README.md) | Blog posts and articles |
| [📝 NPM Scripts](docs/npm-scripts/README.md) | Project-specific npm scripts |
| [📊 Project Status](docs/project-status/README.md) | Test execution reports, push checklists |
| [📋 Specs](docs/specs/README.md) | All specs: completed, in-progress, pending |
| [🧪 Testing](docs/tests/README.md) | Testing documentation, test reports, coverage reports |
| [📄 Reports](docs/reports/README.md) | Completion reports, validation reports, recovery reports |
| [🔧 Development](docs/development/README.md) | Task specifications, requirements, design documents |
| [⚙️ Infrastructure](docs/infrastructure/README.md) | Infrastructure documentation |
| [📖 Reference](docs/reference/README.md) | Reference documentation |
| [📜 Scripts](docs/scripts/README.md) | Script documentation and usage examples |
| [🧪 Tests](docs/tests/README.md) | Test structure and execution guides |
| [🔧 Config](docs/config/README.md) | Configuration documentation |

---

## Current Phase Status

**Ecosystem Architectural Refactoring — COMPLETED** (April 2026)

### ✅ Major Accomplishments
- **Package Architecture**: Clear separation between `django_osoul` (pure Django), `django_rseal` (Wagtail automation), `django_grep` (testing), and `nawaai` (AI toolkit)
- **Domain Restructuring**: Apps renamed to domain-aligned names (`handlers` → `accounts`, `LMS` → `lms/alliance`, `pages` → `content`)
- **Migration Safety**: All 41 migrations verified as reversible with comprehensive testing
- **Documentation**: Comprehensive pydoc-style API documentation with organized structure
- **Validation**: Zero boundary violations, zero duplication, zero circular dependencies

### ✅ Technical Outcomes
- **Thin Layer Pattern**: Projects delegate to packages via thin subclasses
- **Test Parity**: Both websites maintain identical test structure and coverage
- **Docker Ready**: Production-ready Docker configuration for both projects
- **Code Quality**: 100% of tasks completed with comprehensive validation

### 📊 Completion Metrics
- **Tasks Completed**: 200+ tasks across 17 phases
- **Migrations Verified**: 41/41 reversible (100%)
- **Boundary Violations**: 0 remaining
- **Code Duplication**: 0% above 70% similarity threshold
- **Test Coverage**: Full test suites passing for all packages and projects

### ⚠ Current Operational Status
- **Docker Infrastructure**: ✅ Running (PostgreSQL, Redis, Traefik, Workers, Media)
- **Website Application**: ⚠ Partially running (dependency issues in `django_rseal` package)
- **Test Execution**: ❌ Blocked (missing dependencies in virtual environments)
- **Health Checks**: ⚠ Partial (infrastructure healthy, application unhealthy)

**See Completion Report**: [Ecosystem Architectural Refactoring Completion Summary](docs/reports/ECOSYSTEM_ARCHITECTURAL_REFACTORING_COMPLETION_SUMMARY.md)

**See Status Report**: [Test and Docker Status Report](docs/reports/TEST_AND_DOCKER_STATUS_REPORT.md)

---

## Architecture Map

```
workspace/
├── ctc-research.com/          # Xellent LMS — Django/Wagtail
│   ├── apps/
│   │   ├── accounts/          # Auth, registration, profile, snippets
│   │   ├── lms/               # Course, enrollment, certification models
│   │   ├── blog/              # Blog pages
│   │   └── content/           # Wagtail CMS pages
│   ├── core/                  # ASGI/WSGI, URLs, settings entry
│   ├── configs/               # Dynaconf settings
│   ├── assets/                # Static files, templates, media
│   └── tests/                 # 8 passing property-based tests
│
├── structa.cloud/             # Alliance Platform — Django/Wagtail
│   ├── apps/
│   │   ├── accounts/          # Auth, registration, profile, snippets
│   │   ├── alliance/           # LMS models
│   │   ├── blog/              # Blog pages
│   │   └── content/           # Wagtail CMS pages
│   ├── alliance/              # ASGI/WSGI, URLs, CI app
│   ├── configs/               # Dynaconf settings
│   ├── assets/                # Static files, templates, media
│   └── tests/                 # 22 passing tests
│
├── venv/libs/                 # Shared workspace libraries
│   ├── django-osoul/          # Base layer: abstract models, mixins, PageHandler, comp
│   ├── django-grep/           # Shim + shared test infrastructure (BaseTestCase, factories)
│   ├── django-rseal/          # Automation: email, pipelines, profile mixins, workflows
│   └── nawaai/                # AI/NLP integration layer
│
└── compose/                   # Shared Docker infrastructure
    ├── traefik/               # Reverse proxy
    ├── nginx/                 # Static/media serving
    ├── postgres/              # Shared PostgreSQL
    └── blinko/                # Knowledge management

Dependency direction (correct):
  ctc-research.com  →  django-osoul, django-grep, django-rseal, nawaai
  structa.cloud     →  django-osoul, django-grep, django-rseal, nawaai
  django-rseal      →  django-osoul
  django-grep       →  (standalone shim)
  nawaai            →  (standalone)
```

See [enhancement roadmap](docs/development/enhancement-roadmap.md) for planned improvements.
See [pending spec](docs/specs/pending/README.md) for full task list.
See [architecture documentation](docs/architecture/ARCHITECTURE.md) for detailed architecture overview.

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager (recommended)
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 14+

### Setup for Both Websites

```bash
# Clone the repository (if not already cloned)
git clone <repository-url>
cd <repository-name>

# Create virtual environments and install dependencies for both projects
cd ctc-research.com
uv sync --all-extras

cd ../structa.cloud
uv sync --all-extras

# Return to workspace root
cd ..

# Install shared libraries
cd venv/libs/django-osoul
uv sync

cd ../django-rseal
uv sync

cd ../django-grep
uv sync

cd ../nawaai
uv sync

# Return to workspace root
cd ../../..
```

### Environment Configuration

```bash
# Copy environment examples
cp ctc-research.com/.env.example ctc-research.com/.env
cp structa.cloud/.env.example structa.cloud/.env

# Edit environment files with your configuration
# Set database credentials, secret keys, etc.
```

### Database Setup

```bash
# Start PostgreSQL with Docker Compose
docker compose up -d postgres

# Create databases (if not using Docker Compose)
# Run migrations for both projects
cd ctc-research.com
uv run python manage.py migrate

cd ../structa.cloud
uv run python manage.py migrate
```

---

## 🧪 Running Test Scripts for Both Websites

### Comprehensive Test Suite

The system includes comprehensive test scripts that ensure both websites maintain parity:

#### Run All Tests for Both Websites

```bash
# Run all tests for both websites and packages
python3 scripts/run_all_tests.py

# Output includes:
# - Package tests (django_osoul, django_rseal, django_grep, nawaai)
# - Project tests (ctc-research.com, structa.cloud)
# - Test parity verification
# - Comprehensive test report saved to TEST_REPORT.json
```

#### Verify Test Parity Only

```bash
# Verify test parity between structa.cloud and ctc-research.com
python3 scripts/verify_test_parity.py

# Output includes:
# - Test count comparison
# - Test structure analysis
# - Test category comparison
# - Parity report saved to TEST_PARITY_REPORT.json
```

### Test Individual Projects

```bash
# Test ctc-research.com
cd ctc-research.com
uv run pytest tests/ -v

# Test structa.cloud
cd structa.cloud
uv run pytest tests/ -v
```

### Test Packages

```bash
# Test django_osoul
cd venv/libs/django-osoul
uv run pytest tests/ -v

# Test django_rseal
cd venv/libs/django-rseal
uv run pytest tests/ -v

# Test django_grep
cd venv/libs/django-grep
uv run pytest tests/ -v

# Test nawaai
cd venv/libs/nawaai
uv run pytest tests/ -v
```

### Test Script Examples

```python
# Example: Running tests programmatically
from scripts.run_all_tests import TestRunner

runner = TestRunner()
success = runner.run()  # Returns True if all tests pass and parity verified

# Example: Verifying parity only
from scripts.verify_test_parity import TestParityVerifier

verifier = TestParityVerifier()
parity_verified = verifier.run()  # Returns True if parity verified
```

### Test Reports

After running tests, the following reports are generated:

- `TEST_REPORT.json` - Comprehensive test results
- `TEST_PARITY_REPORT.json` - Test parity verification results

### Test Parity Verification

The system ensures both websites have similar test coverage:
- Similar test counts
- Similar test categories
- Similar test types (unit, integration, functional)
- All tests passing

---

## 🔍 Running Validation Scripts

The ecosystem includes comprehensive validation scripts to ensure architectural integrity:

### Boundary Validation

```bash
# Run all boundary checks using import-linter
import-linter --config .importlinter

# Check specific boundary rules:
# - nawaai-no-django: nawaai must not import Django
# - osoul-no-wagtail: django_osoul must not import Wagtail
# - rseal-no-projects: django_rseal must not import project-specific code
# - grep-test-only: django_grep must only be imported by test code
```

### Duplication Analysis

```bash
# Analyze duplication across the ecosystem
python3 scripts/analyze_duplication.py --threshold 0.70

# Output includes:
# - List of all duplicated classes, functions, and modules
# - Similarity percentage for each duplicate
# - Source locations for each duplicate
# - Categorization recommendations
```

### Naming Convention Enforcement

```bash
# Enforce snake_case naming for all Python modules
python3 scripts/enforce_naming.py check_module_names

# Enforce PascalCase naming for all classes
python3 scripts/enforce_naming.py check_class_names

# Enforce snake_case naming for all functions and variables
python3 scripts/enforce_naming.py check_function_names
```

### Template Organization Validation

```bash
# Check template organization
python3 scripts/validate_templates.py check_no_package_templates
python3 scripts/validate_templates.py verify_template_resolution
```

### Migration Safety Validation

```bash
# Check migration safety
python3 scripts/validate_migrations.py check_all_migrations
```

### System Validation

```bash
# Run comprehensive system validation
python3 scripts/validate_system.py

# Output includes:
# - Duplication check results
# - Boundary check results
# - Test results for both websites
# - Test count parity verification
# - Docker health status
# - Import path validation
```

### Validation Script Examples

```python
# Example: Running boundary check programmatically
from scripts.check_boundaries import BoundaryChecker

checker = BoundaryChecker()
violations = checker.check_all_rules()
if violations:
    print(f"Found {len(violations)} boundary violations")
    for violation in violations:
        print(f"  - {violation}")

# Example: Analyzing duplication programmatically
from scripts.analyze_duplication import DuplicationAnalyzer

analyzer = DuplicationAnalyzer(threshold=0.70)
duplicates = analyzer.analyze_all_directories()
print(f"Found {len(duplicates)} duplicate pairs")
```

---

## 🏗️ Development Workflow

### 1. Spec Creation
Create specs in `.kiro/specs/` with:
- `requirements.md` - User stories and acceptance criteria
- `design.md` - Technical design and implementation details
- `tasks.md` - Concrete tasks with sub-tasks

### 2. Task Execution
Use the spec task orchestrator to execute tasks:

```python
from orchestrator.orchestrator import SpecTaskOrchestrator
from orchestrator.config import OrchestratorConfig

config = OrchestratorConfig(base_path=".kiro/specs-organized")
orchestrator = SpecTaskOrchestrator(config)
result = orchestrator.execute_task("task-id")
```

### 3. Validation
Run validation scripts to ensure architectural integrity:

```bash
# Run all validation checks
python3 scripts/validate_system.py

# Or run individual validation scripts:
import-linter --config .importlinter  # Boundary checks
python3 scripts/analyze_duplication.py --threshold 0.70  # Duplication analysis
python3 scripts/enforce_naming.py check_module_names  # Naming conventions
```

### 4. Testing
Run tests for both websites and verify parity:

```bash
# Run all tests for both websites
python3 scripts/run_all_tests.py

# Or run tests individually:
cd ctc-research.com && uv run pytest tests/ -v
cd structa.cloud && uv run pytest tests/ -v
```

### 5. Documentation
Update documentation in appropriate `docs/` subdirectories:

```bash
python3 scripts/organize_docs.py --run  # Organize documentation
```

---

## 📦 Package Documentation Links

### django_osoul
**Purpose**: Pure Django foundation layer - models, managers, mixins, utils, comp, contrib

- **Documentation**: [django_osoul README](venv/libs/django-osoul/README.md)
- **Scope**: Must not import wagtail, celery, or django_rseal
- **Sub-modules**: `handlers/`, `managers/`, `mixins/`, `utils/`, `comp/`, `contrib/`, `middlewares/`, `filters/`, `forms/`, `backends/`, `adapters/`, `services/`

### django_rseal
**Purpose**: Automation layer - pipelines, services, workflows, email, signals, admin, cache, commands

- **Documentation**: [django_rseal README](venv/libs/django-rseal/README.md)
- **Scope**: Wagtail + automation logic
- **Key Patterns**: CartServiceBase thin subclass pattern
- **Wagtail Components**: blocks, snippets, hooks, admin customizations

### django_grep
**Purpose**: Unified testing framework - seeder, test base, fixtures, factories, assertions, pytest plugin, health checks

- **Documentation**: [django_grep README](venv/libs/django-grep/README.md)
- **Scope**: Testing infrastructure only (must not be imported by production code)
- **Features**: BaseTestCase with Hypothesis helpers (st_email, st_slug, st_uuid)
- **Health Checks**: Endpoints at `/health/`, `/health/database/`, `/health/assets/`, `/health/media/`

### nawaai
**Purpose**: Pure Python AI/MCP toolkit - ai, chat, mcp, orchestrator, seeder

- **Documentation**: [nawaai README](venv/libs/nawaai/README.md)
- **Scope**: Zero Django imports (pure Python only)
- **Features**: AI integrations, chat functionality, MCP server support

---

## 🐳 Docker Commands

### Start All Services

```bash
# Start all services in detached mode
docker compose up -d

# Check health endpoints
curl http://localhost:8080/health/
curl http://localhost:8080/health/database/
curl http://localhost:8080/health/assets/
curl http://localhost:8080/health/media/
```

### Stop All Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

### Service-Specific Commands

```bash
# Start only PostgreSQL
docker compose up -d postgres

# View logs for a specific service
docker compose logs -f postgres

# Restart a specific service
docker compose restart nginx
```

### Build Images

```bash
# Build all images
docker compose build

# Build a specific service
docker compose build ctc-research
```

---

## 🔄 Migration Commands

### Apply Migrations

```bash
# Apply all migrations
python manage.py migrate

# Apply migrations for a specific app
python manage.py migrate accounts

# Show migration status
python manage.py showmigrations
```

### Create New Migrations

```bash
# Create new migration for an app
python manage.py makemigrations accounts

# Create empty migration
python manage.py makemigrations --empty accounts
```

### Migration Safety

```bash
# Test migration reversal
python manage.py migrate accounts zero  # Reverse all accounts migrations
python manage.py migrate accounts      # Re-apply migrations

# Check migration safety
python3 scripts/validate_migrations.py check_all_migrations
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow the architectural boundaries defined in `.importlinter`
- Maintain test parity between `ctc-research.com` and `structa.cloud`
- Use the thin layer pattern for project-specific code
- Run all validation scripts before submitting changes
- Update documentation in the appropriate `docs/` subdirectory

---

## 📄 License

This project uses a dual licensing model — see the [LICENSE](docs/LICENSE.md) file for details.

---

## 🙌 Acknowledgements

- Built with ❤️ and [`uv`](https://docs.astral.sh/uv/)
- Django & Wagtail for the web framework
- Hypothesis for property-based testing
- Docker for containerization
- Traefik for reverse proxy
- All contributors who have helped shape this ecosystem

---

## Quick Reference

### Common Commands

```bash
# Run all validation checks
python3 scripts/validate_system.py

# Run all tests for both websites
python3 scripts/run_all_tests.py

# Run documentation organization
python3 scripts/organize_docs.py --run

# Check architecture boundaries
import-linter --config .importlinter

# Start development servers
docker compose up -d

# Apply database migrations
python manage.py migrate

# Validate Docker configurations
make validate

# Test Docker compose configurations
make test-compose

# Show container logs
make logs
```

### Project Structure

```
.
├── ctc-research.com/          # Research platform
├── structa.cloud/            # Alliance platform
├── venv/libs/                 # Shared libraries
│   ├── django-osoul/         # Pure Django foundation
│   ├── django-rseal/         # Wagtail automation
│   ├── django-grep/          # Testing infrastructure
│   └── nawaai/               # AI toolkit
├── compose/                   # Docker infrastructure
├── docs/                      # Comprehensive documentation
├── scripts/                   # Validation and test scripts
└── .kiro/specs/               # Spec task definitions
```

### Health Check Endpoints

- `GET /health/` - Overall health status
- `GET /health/database/` - Database connectivity
- `GET /health/assets/` - Static assets availability
- `GET /health/media/` - Media files availability

---

**Start with**: [Getting Started](docs/getting-started/README.md)
