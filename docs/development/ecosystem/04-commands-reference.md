# Django Project Commands

## Main Menu & Help
- `make help` - 📚 Display this help message
- `make menu` - 🎛️ Interactive development menu
- `make docs` - 📖 Generate commands documentation

## Development Server
- `make dev` - 🚀 Start Django development server (Uvicorn)
- `make run` - 🏃‍♂️ Alias for dev
- `make server` - 🌐 Alias for dev

## Frontend Build System
- `make frontend-install` - 📦 Install frontend dependencies
- `make frontend-build` - 🔨 Build frontend (development)
- `make frontend-production` - 🏭 Build frontend (production with PurgeCSS)
- `make frontend-watch` - 👁️ Watch frontend (development)
- `make frontend-start` - 📦 Alias for frontend-watch
- `make css-purge` - 🧹 Run PurgeCSS manually
- `make css-analyze` - 📊 Analyze CSS bundle size

## Setup & Sync
- `make setup` - ⚡ Full project setup (first time)
- `make install` - 📥 Install/update Python dependencies

## Database
- `make migrate` - 🗃️ Run database migrations
- `make migrations` - 📝 Alias for migrate
- `make db-shell` - 🐚 Open database shell (PostgreSQL)
- `make reset-db` - 💣 Reset database (DANGER: deletes all data!)
- `make reset-migrations` - 💣 Reset database (DANGER: deletes all data!)

## Static Files
- `make static` - 🧹 Collect static files
- `make collectstatic` - 📁 Alias for static

## User Management
- `make superuser` - 👑 Create Django superuser
- `make createsuperuser` - 👤 Alias for superuser

## Testing & Quality
- `make test` - 🧪 Run Django tests
- `make test-coverage` - 📊 Run tests with coverage
- `make check` - 🔍 Run Django system checks

## Python Sync System
- `make sync-interactive` - 🔄 Interactive sync (choose environment/direction)
- `make sync` - 📡 Alias for sync-interactive
- `make sync-demo` - 🎯 Sync demo environment
- `make sync-main` - 🚀 Sync main environment
- `make sync-push` - 📤 Push to current environment
- `make sync-pull` - 📥 Pull from current environment
- `make sync-full` - ⚡ Full sync with all steps
- `make sync-quick` - ⚡ Quick sync (minimal steps)
- `make sync-config` - ⚙️ Save current sync configuration
- `make sync-test` - 🧪 Test sync without changes
- `make sync-clean` - 🧹 Clean sync artifacts

## Token Management (Python Sync)
- `make token-list` - 🔐 List available tokens from all sources
- `make token-save` - 💾 Save current token to secure storage
- `make token-test` - 🧪 Test current token validity
- `make token-from-env` - 📁 Load token from .env file
- `make token-config` - ⚙️ Configure token sources

## Code Quality & Formatting
- `make format` - 🎨 Format code with ruff
- `make lint` - 🔍 Fast linting (imports only)
- `make fix` - 🔧 Fix all fixable issues with ruff
- `make fix-unused` - 🧹 Remove unused imports and variables
- `make clean-imports` - 📦 Alias for fix-unused

## Shell & Debugging
- `make shell` - 🐚 Open Django shell
- `make shell-plus` - 🐍 Alias for shell
- `make debug` - 🐛 Start debug shell (ipdb)

## Docker Management
- `make up` - 🐳 Start Docker containers
- `make down` - ⏹️ Stop Docker containers
- `make docker-logs` - 📋 Show Docker container logs
- `make docker-restart` - 🔄 Restart Docker containers

## Cleanup
- `make clean` - 🧹 Clean Python, frontend, and sync cache
- `make clean-python` - 🐍 Clean Python cache and build files
- `make clean-frontend` - 🎨 Clean frontend build artifacts
- `make clean-sync` - 🔄 Clean sync artifacts
- `make clean-docker` - 🐳 Clean Docker resources
- `make clean-all` - 💥 Complete cleanup (everything)

## Utility & Info
- `make status` - 📊 Show project status
- `make env-check` - 🌍 Check environment configuration
- `make version` - 🏷️ Show project versions

## Pipeline Shortcuts
- `make push-demo` - 📤 Push to demo
- `make push-main` - 📤 Push to main
- `make pull-demo` - 📥 Pull from demo
- `make pull-main` - 📥 Pull from main
- `make deploy` - 🚀 Full deployment pipeline
- `make rollback` - ↩️ Rollback last deployment

## Shortcuts (for quick typing)
- `make s` - setup
- `make d` - dev
- `make r` - run
- `make t` - test
- `make c` - check
- `make m` - migrate
- `make f` - format
- `make l` - lint
- `make x` - fix
- `make fb` - frontend-build
- `make fp` - frontend-production
- `make fw` - frontend-watch
- `make fi` - frontend-install
- `make cl` - clean
- `make cla` - clean-all
- `make du` - up
- `make dd` - down
- `make dl` - docker-logs
- `make dr` - docker-restart
- `make sh` - shell
- `make sp` - shell-plus
- `make st` - static
- `make cs` - collectstatic
- `make su` - superuser
- `make csu` - createsuperuser
- `make fu` - fix-unused
- `make ci` - clean-imports
- `make rm` - reset-migrations
- `make sync-i` - sync-interactive
- `make sync-d` - sync-demo
- `make sync-m` - sync-main
- `make build` - 🔨 Build everything (frontend + static)

## Key Features

### Python Sync System
- **Interactive sync** with environment selection (demo/main/custom)
- **Token management** with secure storage (encrypted)
- **Multiple workflows**: quick, standard, full
- **Git integration** with automatic commits
- **Docker container sync** with automatic restart
- **Bi-directional sync**: push, pull, or smart sync

### Frontend Build System
- **PostCSS pipeline** with Tailwind CSS
- **PurgeCSS integration** for production builds
- **Development watcher** with hot reload
- **CSS analysis** tools for optimization
- **Production-ready builds** with minification

### Development Tools
- **Interactive menu** for easy navigation
- **Comprehensive testing** with coverage reports
- **Code quality** with Ruff formatting and linting
- **Database management** with migration tools
- **Docker integration** for containerized development

### Environment Management
- **Token discovery** from multiple sources
- **Configuration management** with JSON files
- **Environment validation** and checking
- **Secure storage** for sensitive data

## Quick Start

1. **Initial Setup:**
   ```bash
   make setup