# Tinker Makefile Reference

Complete guide to all available Make commands for Tinker development and deployment.

## Quick Reference

### 🚀 Getting Started (3 commands)

```bash
make setup          # Full setup: npm install → pip install → migrate → build
make run            # Start development server on http://localhost:5073
make run-full       # Equivalent to: setup + run (all-in-one)
```

### 🐳 Docker (4 commands)

```bash
make docker-build   # Build Docker image
make docker-run     # Start container (http://cypercloud.localhost:5073)
make docker-stop    # Stop container
make docker-logs    # View container logs
```

---

## All Commands

### 🎯 Quick Start Commands

#### `make setup`
**Purpose:** Complete local development setup in one command.

**What it does:**
1. Installs npm dependencies
2. Installs Python packages from requirements.txt
3. Applies database migrations
4. Builds frontend assets (production bundle)
5. Collects static files

**Output:**
```
✅ Setup complete!

Next steps:
  1. Create superuser (optional): make superuser
  2. Start server: make run
  3. Access: http://localhost:5073
```

**Time:** ~2-3 minutes (depends on npm install)

**Example:**
```bash
cd projects/cypercloud
make setup
make run
# → Access http://localhost:5073
```

---

#### `make run`
**Purpose:** Start the development server.

**What it does:**
- Starts Django development server on port 5073
- Watches for Python file changes
- Auto-reloads on code changes
- Shows detailed error messages

**Access:** http://localhost:5073

**Stop:** Press Ctrl+C

**Example:**
```bash
make run
# Django version 4.2.X, using settings 'settings'
# Starting development server at http://127.0.0.1:5073/
# Quit the server with CONTROL-C.
```

---

#### `make run-full`
**Purpose:** Complete setup and run in one command.

**Equivalent to:** `make setup && make run`

**Use when:**
- Fresh clone or new developer
- First-time setup
- Resetting everything from scratch

**Example:**
```bash
cd projects/cypercloud
make run-full
# (Takes ~3 minutes, then starts server)
```

---

### 🐳 Docker Commands

#### `make docker-build`
**Purpose:** Build Docker image for cypercloud.

**What it does:**
1. Reads docker-compose.yml
2. Runs multi-stage Dockerfile
3. Installs dependencies in containers
4. Builds webpack bundles inside container
5. Creates cypercloud:latest image

**Time:** ~5-10 minutes (first build)

**Output:**
```
[+] Building 45.2s (37/37) FINISHED
...
=> exporting to image
=> naming to docker.io/library/cypercloud:latest
```

**Example:**
```bash
make docker-build
# → Creates cypercloud:latest image
```

---

#### `make docker-run`
**Purpose:** Start cypercloud in Docker container.

**What it does:**
1. Starts container from cypercloud:latest
2. Runs database migrations
3. Exposes port 5073 via Traefik
4. Mounts volumes for data persistence

**Access:**
- Via Traefik: http://cypercloud.localhost:5073
- Direct: http://localhost:5073

**Example:**
```bash
make docker-build    # First: build image
make docker-run      # Then: run container
# → Access http://cypercloud.localhost:5073
```

---

#### `make docker-stop`
**Purpose:** Stop the Docker container.

**What it does:**
- Stops running cypercloud container
- Preserves data in volumes (cypercloud-data, cypercloud-static, cypercloud-media)

**Example:**
```bash
make docker-stop
# Stopping cypercloud ... done
```

---

#### `make docker-logs`
**Purpose:** View real-time container logs.

**What it does:**
- Shows output from running container
- Updates as events occur
- Shows errors and requests

**Stop:** Press Ctrl+C

**Example:**
```bash
make docker-logs
# cypercloud  | 🚀 Running Django system checks...
# cypercloud  | ✅ System check identified no issues (0 silenced).
# cypercloud  | 🚀 Applying migrations...
```

---

#### `make docker-shell`
**Purpose:** Open bash shell inside container.

**What it does:**
- Connects to running container via bash
- Allows running commands inside container
- Full access to Django management commands

**Example:**
```bash
make docker-shell
# root@container:/app/cypercloud# python manage.py shell
# >>>
```

---

#### `make docker-migrate`
**Purpose:** Run migrations inside Docker container.

**Use when:**
- Container already running
- Need to apply new migrations
- Without restarting container

**Example:**
```bash
make docker-migrate
# Operations to perform:
#   Apply all migrations: chat
# Running migrations:
#   Applying chat.0001_initial... OK
```

---

### 🛠️ Frontend (Webpack) Commands

#### `make install-assets`
**Purpose:** Install npm dependencies.

**What it does:**
- Runs `npm ci` in assets/ directory
- Installs exact versions from package-lock.json
- Preserves consistency across machines

**Time:** ~1-2 minutes

**Example:**
```bash
make install-assets
# added 500+ packages in 1.5s
```

---

#### `make build`
**Purpose:** Production webpack build.

**What it does:**
1. Compiles SCSS to CSS
2. Minifies JavaScript
3. Optimizes images
4. Creates source maps (production)
5. Outputs to assets/bundles/cypercloud/

**Output files:**
```
assets/bundles/cypercloud/
├── app-{hash}.js              (minified app code)
├── vendor-{hash}.js           (minified vendor code)
├── styles-{hash}.css          (minified styles)
└── bundles.json               (manifest)
```

**Use when:**
- Before deployment
- For production-ready assets
- When bundle size matters

**Example:**
```bash
make build
# asset app-abc123.js 245 KiB (gzipped: 65 KiB)
# asset styles-xyz789.css 125 KiB
# ✅ Production build done
```

---

#### `make build-dev`
**Purpose:** Development webpack build.

**What it does:**
1. Compiles SCSS to CSS
2. Includes full source maps
3. Doesn't minify (faster build)
4. Includes dev utilities

**Use when:**
- During development
- Need to debug minified code
- Want faster rebuild time

**Time:** ~30 seconds

**Example:**
```bash
make build-dev
# asset app.js 2.5 MiB
# asset styles.css 500 KiB
# source map: app.js.map
```

---

#### `make watch`
**Purpose:** Watch mode - auto-rebuild on file changes.

**What it does:**
1. Watches assets/static/ for changes
2. Rebuilds on any change
3. Runs in foreground (blocks terminal)

**Stop:** Press Ctrl+C

**Use when:**
- Active development
- Want instant feedback
- Testing style changes

**Example:**
```bash
make watch
# Watching for file changes...
# (Edit a .scss file)
# Built in 2.3s
```

---

#### `make dev`
**Purpose:** Webpack dev server with HMR (Hot Module Replacement).

**What it does:**
1. Starts webpack dev server on port 5093
2. Enables Hot Module Replacement
3. Auto-refreshes browser on changes
4. Serves assets without writing to disk

**Access:** http://localhost:5093

**Stop:** Press Ctrl+C

**Use when:**
- Want fastest feedback loop
- Testing JavaScript changes
- Want browser auto-refresh

**Example:**
```bash
make dev
# <s> [webpack-dev-server] 'ws://localhost:5093/ws'
# <s> [webpack-dev-server] Compiled successfully
```

---

#### `make clean`
**Purpose:** Remove generated bundles.

**What it does:**
- Deletes assets/bundles/cypercloud/
- Removes all compiled assets
- Safe to delete (can rebuild)

**Use when:**
- Cleaning up before fresh build
- Resolving bundle caching issues
- Freeing disk space

**Example:**
```bash
make clean
# 🧹 Removing generated bundles…
# ✅ Bundles cleaned: assets/bundles/cypercloud/
```

---

### 📦 Static Files & Deployment

#### `make collectstatic`
**Purpose:** Collect static files into STATIC_ROOT.

**What it does:**
1. Copies files from STATICFILES_DIRS
2. Places them in staticfiles/
3. Handles file hashing for cache busting
4. Clears old static files

**Use when:**
- Before deployment
- Preparing for production
- After building new assets

**Example:**
```bash
make collectstatic
# 145 static files copied to '/app/cypercloud/staticfiles'.
```

---

#### `make build-collect`
**Purpose:** Build assets and collect in one command.

**Equivalent to:** `make build && make collectstatic`

**Use when:**
- Ready for deployment
- Single step to prepare everything
- Want production-ready bundle

**Example:**
```bash
make build-collect
# Step 1: Building assets...
# ✅ Production build done
# Step 2: Collecting static...
# 145 static files copied
```

---

#### `make deploy`
**Purpose:** Full deployment pipeline.

**Steps:**
1. Build frontend assets
2. Collect static files
3. Apply database migrations

**Equivalent to:** `make build && make collectstatic && make migrate`

**Use when:**
- Deploying new code to production
- New database schema changes
- Full fresh deployment

**Time:** ~2-3 minutes

**Example:**
```bash
make deploy
# === Step 1: Build assets ===
# ✅ Production build done
# === Step 2: Collect static ===
# 145 static files copied
# === Step 3: Apply migrations ===
# Operations to perform: ...
# ✅ Deploy complete
```

---

### 🗄️ Database Commands

#### `make migrate`
**Purpose:** Apply Django migrations.

**What it does:**
1. Checks for unapplied migrations
2. Applies them in order
3. Updates database schema
4. Runs data migrations if needed

**Use when:**
- First setup
- After pulling new code with migrations
- After creating new migrations

**Example:**
```bash
make migrate
# Operations to perform:
#   Apply all migrations: chat
# Running migrations:
#   Applying chat.0001_initial... OK
```

---

#### `make migrate-new`
**Purpose:** Create new database migration.

**Usage:** `make migrate-new MIGRATION=app_name`

**What it does:**
1. Detects model changes
2. Creates migration file
3. Outputs migration code

**Example:**
```bash
make migrate-new MIGRATION=chat
# Migrations for 'chat':
#   chat/migrations/0002_auto_20260705_1234.py
#     - Add field new_field to Conversation
```

---

#### `make migrate-status`
**Purpose:** Show migration status.

**What it does:**
1. Lists all migrations
2. Shows which are applied
3. Shows which are pending

**Example:**
```bash
make migrate-status
# chat
#  [X] 0001_initial
#  [X] 0002_auto_20260701
#  [ ] 0003_add_new_field
```

---

#### `make db-reset`
**Purpose:** Reset database to fresh state.

**⚠️ WARNING:** This is destructive - deletes all data!

**What it does:**
1. Prompts for confirmation
2. Deletes db.sqlite3
3. Runs fresh migrations
4. Creates clean database

**Use when:**
- Development only
- Starting fresh
- Testing migrations

**Example:**
```bash
make db-reset
# ⚠️  Resetting database...
# Are you sure? (yes/no): yes
# ✅ Database reset complete
```

---

### ⚙️ Django Management

#### `make check`
**Purpose:** Run Django system checks.

**What it does:**
1. Validates Django setup
2. Checks installed apps
3. Validates model definitions
4. Checks URLs, middleware, etc.

**Use when:**
- After configuration changes
- Troubleshooting setup issues
- Before deployment

**Example:**
```bash
make check
# System check identified no issues (0 silenced).
```

---

#### `make check-deploy`
**Purpose:** Check production deployment readiness.

**What it does:**
1. Runs all Django checks
2. Verifies security settings
3. Checks SSL/HTTPS configuration
4. Warns about production issues

**Use when:**
- Before deploying to production
- Verifying security settings

**Example:**
```bash
make check-deploy
# (1_0.W001) All ALLOWED_HOSTS should include 'cypercloud.example.com'
```

---

#### `make shell`
**Purpose:** Open Django interactive shell.

**What it does:**
1. Loads Django environment
2. Imports models, ORM, etc.
3. Opens Python REPL

**Use when:**
- Testing model queries
- Data manipulation
- Exploring database

**Example:**
```bash
make shell
# Python 3.11.X (main, Jul  5 2026)
# Type "help", "copyright", "credits" or "license"
# >>> from chat.models import Conversation
# >>> Conversation.objects.all()
```

---

#### `make superuser`
**Purpose:** Create admin superuser.

**Alias:** `make createsuperuser`

**What it does:**
1. Prompts for username
2. Prompts for email
3. Prompts for password (twice)
4. Creates superuser account

**Use when:**
- First setup
- Adding new admin user
- Lost admin access

**Example:**
```bash
make superuser
# Username: admin
# Email address: admin@example.com
# Password:
# Password (again):
# Superuser created successfully.
```

---

### 🔍 Testing & Debugging

#### `make test`
**Purpose:** Run all tests.

**What it does:**
1. Discovers test files
2. Runs all tests
3. Reports results

**Example:**
```bash
make test
# Ran 12 tests in 0.234s
# OK
```

---

#### `make test-verbose`
**Purpose:** Run tests with verbose output.

**What it does:**
1. Shows each test name
2. Shows test results
3. More detailed output

**Example:**
```bash
make test-verbose
# test_conversation_creation (chat.tests.ConversationTestCase) ... ok
# test_message_send (chat.tests.MessageTestCase) ... ok
```

---

#### `make lint`
**Purpose:** Run code linting checks.

**What it does:**
1. Checks code style (PEP 8)
2. Finds unused imports
3. Detects potential bugs
4. Uses ruff or pylint

**Example:**
```bash
make lint
# E501 line too long (120 > 88 characters)
# F841 local variable 'x' is assigned to but never used
```

---

#### `make format`
**Purpose:** Auto-format code.

**What it does:**
1. Runs Black formatter
2. Standardizes code style
3. Fixes formatting issues

**Use when:**
- Before committing code
- Standardizing project style

**Example:**
```bash
make format
# reformatted chat/views.py
# All done! ✨
```

---

### 📚 Project Info & Utilities

#### `make info`
**Purpose:** Display project information.

**Shows:**
- Project location
- Python version
- Django version
- Port configuration
- Database info
- Directory structure
- Quick links

**Example:**
```bash
make info
# ╔════════════════════════════════════════════════════════════╗
# ║   Tinker Project Information                              ║
# ╚════════════════════════════════════════════════════════════╝
# 
# 📍 Location: /home/structa.cloud/projects/cypercloud
# 🐍 Python: Python 3.11.X
# 📦 Django: (4, 2, X, 'final', 0)
# ...
```

---

#### `make env-check`
**Purpose:** Check environment setup.

**Shows:**
- Python version
- Node.js/npm version
- Docker version (if available)
- Django configuration

**Use when:**
- Troubleshooting setup issues
- Verifying dependencies

**Example:**
```bash
make env-check
# Python:
# Python 3.11.0
# Node/npm:
# v20.10.0
# Docker:
# Docker version 24.0.0
```

---

#### `make logs`
**Purpose:** View recent logs.

**Shows:**
- Last 50 lines from all log files
- Build logs
- Deploy logs
- Collectstatic logs

**Example:**
```bash
make logs
# === logs/build.log ===
# asset app-abc123.js 245 KiB
# ✅ Production build done
```

---

### 🧹 Cleanup Commands

#### `make clean-all`
**Purpose:** Complete cleanup.

**What it does:**
1. Deletes webpack bundles
2. Removes Python cache (__pycache__)
3. Removes compiled files (.pyc)

**Safe operation** (no data loss)

**Use when:**
- Before committing code
- Cleaning up development artifacts
- Freeing disk space

---

#### `make clean-pycache`
**Purpose:** Remove Python cache files.

**What it does:**
1. Deletes all __pycache__ directories
2. Removes all .pyc files

**Safe operation** (will be regenerated)

**Example:**
```bash
make clean-pycache
# 🧹 Removing Python cache...
# ✅ Cache cleaned
```

---

#### `make clean-db`
**Purpose:** Delete SQLite database.

**⚠️ WARNING:** Destructive operation!

**What it does:**
1. Prompts for confirmation
2. Deletes db.sqlite3
3. All data lost

**Use when:**
- Testing migrations
- Fresh start
- Development only

---

### 🎯 Composite Tasks (Workflows)

#### `make reset`
**Purpose:** Full reset to clean state.

**Equivalent to:** `make clean-all && make db-reset`

**What it does:**
1. Cleans build artifacts
2. Cleans Python cache
3. Deletes database
4. Runs fresh migrations

**Use when:**
- Want completely fresh start
- Troubleshooting weird issues
- Starting over after major changes

---

#### `make dev-setup`
**Purpose:** Complete development setup.

**Steps:**
1. Install npm dependencies
2. Build development assets (with source maps)
3. Run migrations
4. Shows next steps

**Example:**
```bash
make dev-setup
# ✅ Development setup complete
#
# Start developing:
#   Terminal 1: make run              (Django server)
#   Terminal 2: make watch            (Webpack watch)
#   Browser: http://localhost:5073
```

---

#### `make prod-setup`
**Purpose:** Production-ready setup.

**Equivalent to:** `make install-assets && make deploy`

**Steps:**
1. Install npm dependencies
2. Build production assets
3. Collect static files
4. Run migrations

---

#### `make ci`
**Purpose:** Run CI/CD checks.

**What it does:**
1. Django system checks
2. Code linting
3. Run tests

**Use in CI/CD pipelines**

---

## Usage Patterns

### 🚀 Fresh Start
```bash
make setup
make run
```

### 💻 Daily Development
```bash
make run          # Terminal 1: Django server
make watch        # Terminal 2: Webpack watch
```

### 🔄 With HMR (Hot Module Reload)
```bash
make run          # Terminal 1: Django server
make dev          # Terminal 2: Webpack dev server
```

### 🐳 Docker Development
```bash
make docker-build
make docker-run
make docker-logs
```

### 📦 Deployment
```bash
make deploy
make docker-build
make docker-run
```

### 🧪 Before Commit
```bash
make format
make lint
make test
```

### 🔧 Troubleshooting
```bash
make check
make env-check
make info
```

---

## Tips & Tricks

### Change Port
```bash
make run PORT=8000
```

### Change Workers (Gunicorn)
```bash
make deploy WORKERS=4
```

### View Full Logs
```bash
make logs | less
```

### Run Specific Test
```bash
python manage.py test chat.tests.ConversationTestCase.test_create
```

### Custom Django Command
```bash
python manage.py shell_plus
python manage.py dumpdata > backup.json
```

### Parallel Development
```bash
# Terminal 1
make run

# Terminal 2
make watch

# Terminal 3
make docker-run
```

---

## Troubleshooting Make Commands

### "Command not found"
- Ensure you're in `projects/cypercloud/` directory
- Check `which make` (should be `/usr/bin/make` or similar)

### "No targets specified"
- Syntax: `make target` (not `make -target`)
- Use `make help` to see all targets

### Permission denied
- Make may need to change permissions: `chmod +x /usr/bin/make`
- Or run with `bash -c 'make target'`

### Makefile modified
- If Makefile won't run after edit, check indentation
- Makefile uses **TAB** characters (not spaces)

---

## Next Steps

1. **Read:** `README.md` for feature overview
2. **Setup:** `make setup` for local development
3. **Run:** `make run` to start the server
4. **Deploy:** `make deploy` for production
5. **Learn:** `make info` to understand project structure
