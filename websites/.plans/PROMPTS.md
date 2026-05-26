# Structa Cloud Development Prompts

This file contains prompts for building and maintaining the structa.cloud project structure from scratch.

## Core Entry Points

### Create ASGI Entry Point
```
Create the ASGI entry point (www/asgi.py) for structa.cloud with:
- Django ASGI application setup
- WebSocket support
- Proper environment configuration
- Reference: .kiro/steering/structa-cloud-core.md
```

### Create URL Configuration
```
Create the main URL configuration (www/urls.py) for structa.cloud with:
- Health check endpoints
- Admin panel configuration
- Allauth integration
- Wagtail CMS URLs
- i18n_patterns for internationalization
- Reference: .kiro/steering/structa-cloud-core.md
```

### Create WebSocket Handler
```
Create the WebSocket handler (www/websocket.py) for structa.cloud with:
- Connection handling
- Message processing
- Disconnect handling
- Reference: .kiro/steering/structa-cloud-core.md
```

## Alliance Module

### Create Alliance Module
```
Create the alliance module (www/alliance/) for structa.cloud with:
- Module initialization
- Alliance-specific URLs
- Alliance templates
- CI/CD utilities
- Reference: .kiro/steering/structa-cloud-alliance.md
```

### Create Alliance URLs
```
Create the alliance URL configuration (www/alliance/urls.py) with:
- App URL includes
- Wagtail integration
- i18n support
- Reference: .kiro/steering/structa-cloud-alliance.md
```

### Create Alliance Templates
```
Create the alliance templates (www/alliance/templates/) with:
- Base template with inheritance
- Home page template
- Reusable components
- Reference: .kiro/steering/structa-cloud-alliance.md
```

## Plugin System

### Create Plugin Base Class
```
Create the plugin base class (plugins/base.py) for structa.cloud with:
- Plugin interface definition
- Installation/uninstallation methods
- URL registration
- Middleware registration
- Reference: .kiro/steering/structa-cloud-plugins.md
```

### Create Plugin Loader
```
Create the plugin loader (plugins/loader.py) for structa.cloud with:
- Plugin discovery
- Dynamic loading
- Plugin registry
- Reference: .kiro/steering/structa-cloud-plugins.md
```

### Create Plugin Hook System
```
Create the plugin hook system (plugins/hooks.py) for structa.cloud with:
- Signal registration
- Hook execution
- Plugin lifecycle hooks
- Reference: .kiro/steering/structa-cloud-plugins.md
```

## Management Commands

### Create verify_deployment Command
```
Create the verify_deployment management command (www/alliance/CI/management/commands/verify_deployment.py) with:
- Docker container health checks
- Database connectivity tests
- Static file verification
- URL accessibility tests
- Reference: .kiro/steering/structa-cloud-alliance.md
```

### Create build_assets Command
```
Create the build_assets management command (www/alliance/CI/management/commands/build_assets.py) with:
- Webpack bundling
- Django collectstatic
- Asset verification
- Production/development modes
```

### Create load_fixtures Command
```
Create the load_fixtures management command (www/alliance/CI/management/commands/load_fixtures.py) with:
- Fixture file loading
- Error handling
- Progress reporting
```

## Configuration

### Create Django Settings
```
Create the Django settings structure (www/configs/settings/) with:
- Base settings (apps.py, paths.py, assets.py, auth.py, etc.)
- Environment-specific settings (ENV/_core.yml, database.yml, security.yml)
- CD settings for continuous deployment
- Reference: .kiro/steering/structa-cloud-core.md
```

### Create Docker Configuration
```
Create the Docker configuration (docker-compose.yml) with:
- Web service definition
- Database service
- Redis service
- Nginx configuration
- APP_MODULE: "www.alliance.asgi:application"
```

## Full Project Setup

### Setup Complete Project
```
Setup the complete structa.cloud project structure following .kiro/specs/structa-cloud-full-project.md:
1. Create www/ directory with all subdirectories
2. Create core entry points (asgi.py, urls.py, websocket.py, wsgi.py)
3. Create alliance/ module with CI/CD utilities
4. Create apps/ directory structure
5. Create configs/ directory with settings
6. Create components/ directory
7. Create plugins/ directory
8. Create assets/ directory structure
9. Create Docker configuration
10. Create management commands
11. Set up testing infrastructure
12. Configure internationalization
```

### Update Imports
```
Update all Python imports in www/ directory to use www. prefix:
- from apps. → from www.apps.
- from core. → from www.core.
- from components. → from www.components.
- from alliance. → from www.alliance.
```

### Update Configuration
```
Update configuration files to use www. paths:
- ROOT_URLCONF: "core.urls" → "www.alliance.urls"
- ASGI_APPLICATION: "core.asgi:application" → "www.alliance.asgi:application"
- APP_MODULE in docker-compose.yml: "core.asgi:application" → "www.alliance.asgi:application"
```

## Testing

### Create Test Suite
```
Create comprehensive test suite in www/alliance/CI/tests/ with:
- Unit tests for models
- Integration tests for views
- Selenium tests for UI
- Coverage configuration
```

### Configure Pytest
```
Configure pytest (pytest_simple.ini, conftest.py) with:
- Django integration
- Test paths configuration
- Fixtures
- Coverage reporting
```

## Documentation

### Create README
```
Create comprehensive README.md with:
- Project overview
- Installation instructions
- Development setup
- Deployment guide
- API documentation
```

### Create Specification
```
Create SPECIFICATION.md with:
- Architecture overview
- Directory structure
- Configuration options
- Usage examples
```

## Usage Examples

### Development Setup
```bash
# Clone the repository
git clone <repo_url>
cd websites/structa.cloud

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
npm install

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# In another terminal, start webpack
npm run webpack:watch
```

### Docker Deployment
```bash
# Build and start containers
docker compose up -d --build

# Check logs
docker compose logs -f website

# Run management commands
docker compose exec website python manage.py verify_deployment
docker compose exec website python manage.py build_assets --production
```

### Production Deployment
```bash
# Build assets for production
python manage.py build_assets --production

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput

# Restart services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Best Practices

1. **Always use www. prefix for imports**
   - Never use relative imports across module boundaries
   - Use absolute imports with www. prefix

2. **Keep core entry points minimal**
   - Delegate to www/alliance/ for application logic
   - Use settings from www/configs/settings/

3. **Use plugin system for extensibility**
   - Don't modify core code for new features
   - Create plugins in plugins/ directory

4. **Test before deployment**
   - Run verify_deployment command
   - Test in staging environment
   - Use build_assets for asset compilation

5. **Document changes**
   - Update PROMPTS.md with new commands
   - Update README.md with new features
   - Update SPECIFICATION.md with new structure
