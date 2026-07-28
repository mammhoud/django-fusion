# First-Time Developer Setup Guide

Complete step-by-step guide to get VResume running locally on your machine.

---

## Prerequisites

### System Requirements

| Item | Version | Check |
|------|---------|-------|
| **Python** | 3.12+ | `python3 --version` |
| **Node.js** | 18+ | `node --version` |
| **npm** | 9+ | `npm --version` |
| **PostgreSQL** | 14+ | `psql --version` |
| **Redis** | 6+ | `redis-cli --version` |
| **Git** | 2.0+ | `git --version` |

### Operating System

- ✅ macOS (Intel/ARM)
- ✅ Linux (Ubuntu 20.04+, Debian 11+)
- ✅ Windows (WSL2 recommended)

### Tools to Install

#### macOS
```bash
brew install python@3.12 node postgresql redis git
brew services start postgresql
brew services start redis
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv node npm postgresql redis-server git
sudo systemctl start postgresql
sudo systemctl start redis-server
```

#### Windows (WSL2)
```bash
# Install WSL2 first, then in terminal:
sudo apt-get update
sudo apt-get install python3.12 python3.12-venv nodejs npm postgresql redis-server
sudo service postgresql start
sudo service redis-server start
```

---

## Step 1: Clone Repository

```bash
# Clone the repo
git clone https://github.com/mammhoud/VResume.git
cd VResume

# Check branch
git branch  # Should show main/master

# Update to latest (optional)
git pull origin main
```

---

## Step 2: Python Environment Setup

### Option A: Using `uv` (Recommended)

```bash
# Install uv package manager
pip install uv

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
uv pip install -r requirements.txt
# or simply
uv install
```

### Option B: Using Standard venv

```bash
# Create virtual environment
python3.12 -m venv .venv

# Activate it
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r v1/pyproject.toml[dev]
# or
pip install django wagtail celery redis django-environ
```

### Verify Installation

```bash
python --version  # Should be 3.12+
pip list | grep django  # Should show Django 5.x
pip list | grep wagtail  # Should show Wagtail 6.x
```

---

## Step 3: Environment Configuration

### Create `.env` File

```bash
# Copy example env file
cp .env.example .env  # If it exists
# or create new
touch v1/.env
```

### Edit `.env` with Sensible Defaults

**v1/.env**:
```env
# ========================================
# Django Settings
# ========================================
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# ========================================
# Database
# ========================================
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=vresume_dev
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Fallback to SQLite for quick testing:
# DATABASE_ENGINE=django.db.backends.sqlite3
# DATABASE_NAME=db.sqlite3

# ========================================
# Redis (for Celery)
# ========================================
REDIS_URL=redis://localhost:6379/0

# ========================================
# Email (for local testing)
# ========================================
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@vresume.local

# ========================================
# Security (development only)
# ========================================
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# ========================================
# Language & Time
# ========================================
LANGUAGE_CODE=en-us
TIME_ZONE=UTC
```

### Verify `.env` is Loaded

```bash
cd v1
python manage.py shell
# In Python shell:
from django.conf import settings
print(settings.DEBUG)  # Should print True
```

---

## Step 4: Database Setup

### Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql postgres

# In psql:
CREATE DATABASE vresume_dev;
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET default_transaction_devel TO '2000';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE vresume_dev TO postgres;
\q
```

### Or Use SQLite (Faster for Testing)

Edit `.env`:
```env
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
```

### Run Migrations

```bash
cd v1

# Apply migrations
python manage.py migrate

# Verify
python manage.py migrate --check
```

---

## Step 5: Create Superuser

```bash
cd v1

# Create admin user
python manage.py createsuperuser

# Prompts:
# Username: admin
# Email: admin@example.com
# Password: <enter something>
```

---

## Step 6: Frontend Setup

### Install Node Dependencies

```bash
cd v1/assets

# Install npm packages
npm install

# Verify
npm list webpack  # Should show webpack version
```

### Build Frontend Assets

```bash
# From v1/assets/:

# Development (watch mode)
npm run watch  # Rebuilds on file changes

# Production (one-time build)
npm run build
```

---

## Step 7: Collect Static Files

```bash
cd v1

# Gather all static files
python manage.py collectstatic --noinput

# Verify
ls -la staticfiles/  # Should have bundles
```

---

## Step 8: Populate Sample Data (Optional)

```bash
cd v1

# Load test data
make populate-data  # or:
python manage.py shell < tests/data_populator.py
```

---

## Step 9: Start Development Server

### In Terminal 1: Django

```bash
cd v1
python manage.py runserver
# or
make dev

# Output:
# Starting development server at http://127.0.0.1:8000/
# Quit the server with CONTROL-C.
```

### In Terminal 2: Frontend Watcher

```bash
cd v1/assets
npm run watch

# Output:
# webpack 5.x.x compiled with X warnings in Xms
```

### In Terminal 3: Celery (Optional, for async tasks)

```bash
cd v1
celery -A core worker -l info

# Output:
# ready to accept tasks
```

---

## Step 10: Access the Application

### URLs

| URL | Purpose |
|-----|---------|
| http://localhost:8000 | Main site |
| http://localhost:8000/admin | Wagtail CMS admin |
| http://localhost:8000/admin/pages | Page editor |
| http://localhost:8000/admin/snippets/portfolio/tag | Portfolio tags |

### First Login

1. Go to http://localhost:8000/admin
2. Login with superuser credentials
3. Click "Pages" to see home page
4. Click into "Explore all pages" to see structure

---

## Verification Checklist

- [ ] Python 3.12+ installed
- [ ] `uv` installed and venv activated
- [ ] `.env` file created with DB settings
- [ ] PostgreSQL running (or SQLite configured)
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Node dependencies installed (`npm install`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Dev server starts (`python manage.py runserver`)
- [ ] Frontend watcher runs (`npm run watch`)
- [ ] Admin accessible at http://localhost:8000/admin
- [ ] Site loads at http://localhost:8000

---

## Troubleshooting

### Python Issues

**Problem**: `python: command not found`
```bash
# Solution: Use python3
python3 --version
alias python=python3
```

**Problem**: `ModuleNotFoundError: No module named 'django'`
```bash
# Solution: Ensure venv is activated
source .venv/bin/activate
pip install django wagtail
```

### Database Issues

**Problem**: `psycopg2.OperationalError: could not connect to server`
```bash
# Solution: Ensure PostgreSQL is running
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Windows (WSL2):
sudo service postgresql start
```

**Problem**: `FATAL: database "vresume_dev" does not exist`
```bash
# Solution: Create database
createdb -U postgres vresume_dev
```

**Problem**: `AUTH_PASSWORD_VALIDATORS_HELP_TEXT: "auth.password_validation.CommonPasswordValidator"`
```bash
# Solution: This is a warning, safe to ignore
```

### Frontend Issues

**Problem**: `npm: command not found`
```bash
# Solution: Install Node.js
# macOS:
brew install node

# Or download from https://nodejs.org/
```

**Problem**: `webpack compilation failed`
```bash
# Solution: Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

**Problem**: CSS not updating in browser
```bash
# Solution: Hard refresh
# Chrome: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows/Linux)

# Or clear browser cache and restart dev server
```

### Server Issues

**Problem**: `Port 8000 in use`
```bash
# Solution: Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port:
python manage.py runserver 8001
```

**Problem**: `CORS error` or `CSRF verification failed`
```bash
# Solution: Ensure ALLOWED_HOSTS includes localhost
# In .env:
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Problem**: Static files not loading (404 errors)
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput

# And ensure webpack is running:
cd v1/assets && npm run watch
```

---

## Development Commands

### Running Tasks

```bash
cd v1

# Database
make migrate              # Apply migrations
make reset-db             # Reset database (⚠️ destructive)

# Server
make dev                  # Start Django dev server
make r                    # Shortcut: make r

# Frontend
make frontend-install     # Install npm packages
make frontend-watch       # Start webpack watcher
make frontend-production  # Build production assets

# Testing
make test                 # Run tests
make lint                 # Check code style
make fix                  # Auto-fix style issues

# Utilities
make menu                 # Interactive CLI menu
make help                 # Show all commands
```

### Useful Django Commands

```bash
cd v1

# Shell access
python manage.py shell

# Create tables
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run tests
python manage.py test pages

# Check system
python manage.py check

# Load sample data
python manage.py shell < ../tests/data_populator.py

# Export/import data
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

---

## Setting Up an IDE

### VS Code

1. Install extensions:
   - **Python** (Microsoft)
   - **Django** (Baptiste Darthenay)
   - **Pylance** (Microsoft)
   - **Thunder Client** (Ranga Vadass) or **REST Client**

2. Create `.vscode/settings.json`:
```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/node_modules": true,
        "**/.venv": true
    }
}
```

### PyCharm

1. **Open project**: File → Open → Select VResume folder
2. **Configure interpreter**: 
   - PyCharm → Preferences → Project → Python Interpreter
   - Click ⚙️ → Add → Existing Environment → Select `.venv/bin/python`
3. **Enable Django support**:
   - Preferences → Languages & Frameworks → Django
   - Check "Enable Django support"
   - Set Project root to `v1/`
   - Set Settings module to `configs.settings`

---

## Next Steps

- [ ] Read [Architecture Overview](../../index.md)
- [ ] Explore [Wagtail Documentation](https://docs.wagtail.org/)
- [ ] Review [Component Development Guide](./COMPONENT_GUIDE.md)
- [ ] Check out [Makefile Commands](./makefile.md)
- [ ] Join the team Slack/Discord for questions

---

## Getting Help

### Resources

- **VResume Docs**: `/docs` folder in repo
- **Django**: https://docs.djangoproject.com/
- **Wagtail**: https://docs.wagtail.org/
- **HTMX**: https://htmx.org/docs/
- **Bootstrap**: https://getbootstrap.com/docs/5.0/

### Common Questions

**Q: How do I add a new page type?**  
A: Read [Data Models](../../reference/architecture/models.md) and use Wagtail's page workflow.

**Q: Where do I put custom JavaScript?**  
A: See [Component Development Guide](./COMPONENT_GUIDE.md)

**Q: How do I customize styling?**  
A: Edit SCSS files in `v1/assets/static/styles/` and rebuild.

**Q: Can I use Windows?**  
A: Yes, use WSL2 (Windows Subsystem for Linux). Docker is also supported.

---

## Congratulations! 🎉

You're now ready to develop on VResume. Happy coding!
