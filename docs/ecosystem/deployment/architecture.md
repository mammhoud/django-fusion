# System Architecture Documentation

## Overview

This document provides comprehensive documentation of the current system architecture, technology stack, and all project dependencies. The system is built on a modern, well-architected foundation using Wagtail CMS with django-unfold admin interface, providing a robust platform for content management and API services.

**Current Status**: ✅ Fully Modernized
- Framework: Wagtail CMS (not django-seed)
- Admin Interface: django-unfold with Bootstrap 5
- API Framework: Django Ninja
- Database: PostgreSQL with 267 applied migrations
- All components are modern and well-maintained

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet / Users                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │   Reverse Proxy (Nginx or Traefik)     │
        │   - Host header routing                │
        │   - SSL/TLS termination                │
        │   - Request forwarding                 │
        └────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────────┐   ┌─────────────┐   ┌──────────────┐
   │  Docsify    │   │  Frontend   │   │  API Backend │
   │  Service    │   │  Service    │   │  (Django)    │
   │ (nginx:     │   │ (Wagtail +  │   │ (Django      │
   │  alpine)    │   │  django-    │   │  Ninja)      │
   │             │   │  unfold)    │   │              │
   └─────────────┘   └─────────────┘   └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
   ┌─────────────┐                        ┌──────────────┐
   │  LMS Service│                        │ Shared Data  │
   │ (Maintenance)                        │ (PostgreSQL, │
   │             │                        │  Redis, etc) │
   └─────────────┘                        └──────────────┘

Docker Network: All services connected via custom bridge network
Domain Routing:
  - site-docs.structa.cloud → Docsify Service
  - site.structa.cloud → Frontend Service (Wagtail + django-unfold)
  - core.structa.cloud → API Backend (Django Ninja)
  - lms.structa.cloud → LMS Service (Maintenance)
```

### Service Architecture

#### Reverse Proxy Layer
- Routes incoming requests based on Host headers
- Terminates SSL/TLS connections
- Forwards requests to appropriate backend services
- Preserves Host headers for backend processing
- Handles 404 responses for unrecognized domains

#### Frontend Service
- Django application with Wagtail CMS and django-unfold admin dashboard
- Serves user-facing web interface with Bootstrap 5
- Communicates with API Backend for data operations
- Accessible via site.structa.cloud

#### API Backend
- Django REST API using Django Ninja framework
- Handles data persistence and business operations
- Provides RESTful endpoints for frontend and external clients
- Accessible via core.structa.cloud
- Shared database with Frontend Service

#### Docsify Service
- nginx:alpine container serving static documentation
- Renders markdown files dynamically via Docsify client-side JavaScript
- Accessible via site-docs.structa.cloud
- Mounted /docs volume from host

#### LMS Service
- Placeholder service in maintenance mode
- Returns "Coming Soon" status
- Accessible via lms.structa.cloud
- Future implementation planned

---

## Technology Stack

### Core Framework

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| CMS Platform | Wagtail | Latest | Comprehensive content management system |
| Admin Interface | django-unfold | Latest | Modern Bootstrap 5 admin dashboard |
| API Framework | Django Ninja | Latest | Modern REST API framework |
| Web Framework | Django | 4.2+ | Core web application framework |
| Python | Python | 3.11+ | Programming language |

### Authentication & Authorization

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Authentication | django-allauth | Latest | User authentication with social providers |
| JWT Tokens | django-ninja-jwt | Latest | JSON Web Token authentication |
| FIDO2 | fido2 | Latest | Hardware security key support |

### Database & Caching

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Primary Database | PostgreSQL | 15+ | Relational database with 267 migrations |
| Database Driver | psycopg | 3.3.2+ | PostgreSQL adapter for Python |
| Caching | Redis | Latest | In-memory data store for caching |
| Django Cache | django-redis | 6.0.0+ | Redis cache backend for Django |

### Frontend & UI

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| CSS Framework | Bootstrap | 5 | Responsive UI framework |
| Webpack | django-webpack-loader | Latest | Asset bundling and loading |
| HTMX | django-htmx | Latest | AJAX interactions without JavaScript |
| Icons | django-heroicons | Latest | Heroicons icon library |
| Font Awesome | wagtail-font-awesome-svg | 2.0+ | Font Awesome SVG icons |

### Content Management

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Rich Text Editor | draftjs-exporter | Latest | Draft.js content export |
| Video Embedding | django-embed-video | Latest | Embed videos in content |
| Newsletter | wagtail-newsletter | Latest | Newsletter management with Mailchimp |
| Content Transfer | wagtail-transfer | 0.11+ | Transfer content between instances |

### Development & Debugging

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Debug Toolbar | django-debug-toolbar | Latest | Development debugging tools |
| Browser Reload | django-browser-reload | 1.21.0+ | Auto-reload on file changes |
| Shell Plus | django-extensions | 4.1+ | Enhanced Django shell |
| Stubs | django-stubs | 5.2.8+ | Type hints for Django |

### Monitoring & Logging

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Error Tracking | Sentry | 2.46.0+ | Error and exception tracking |
| Metrics | django-prometheus | 2.4.0+ | Prometheus metrics collection |
| Request Profiling | django-silk | 5.4.3+ | Request profiling and analysis |
| Structured Logging | django-structlog | Latest | Structured logging with context |
| JSON Logging | python-json-logger | 4.0.0+ | JSON formatted logging |

### Data & Import/Export

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Import/Export | django-import-export | Latest | Data import and export functionality |
| Data Tables | django-tables2 | Latest | HTML table generation |
| Marshmallow | marshmallow | Latest | Object serialization |
| Pydantic | pydantic | Latest | Data validation |
| Pydantic Settings | pydantic-settings | 2.12.0+ | Settings management |

### Background Jobs & Async

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Job Queue | django-rq | Latest | Redis-based job queue |
| File Watching | watchfiles | Latest | File system monitoring |
| Live Reload | livereload | 2.7.1+ | Live reload server |

### Deployment & Infrastructure

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| WSGI Server | gunicorn | 23.0.0+ | Production WSGI server |
| ASGI Server | uvicorn | Latest | ASGI server for async support |
| Static Files | whitenoise | Latest | Static file serving |
| Environment | django-environ | Latest | Environment variable management |
| Dynaconf | dynaconf | Latest | Configuration management with vault support |

### Payment Processing

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Stripe | stripe | 14.3.0+ | Payment processing |
| PayPal | django-paypal | 2.1+ | PayPal integration |

### Testing & Quality

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Testing | pytest-django | 4.12.0+ | Django testing framework |
| Property Testing | hypothesis | 6.151.6+ | Property-based testing |

### Utilities & Tools

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| CLI Framework | click | Latest | Command-line interface creation |
| Logging Colors | colorlog | Latest | Colored logging output |
| Version Management | bumpver | Latest | Version bumping tool |
| Fire CLI | fire | 0.7.1+ | CLI generation from Python objects |
| Virtualenv | virtualenv | 20.35.4+ | Virtual environment management |
| Jinja2 | jinja2 | 3.1.6+ | Template engine |
| YAML | yml | 0.0.1+ | YAML parsing |
| JWT | jwt | Latest | JSON Web Token handling |
| Twilio | twilio | 9.8.7+ | SMS and communication services |
| Cloud Storage | django-storages | 1.14.6+ | Cloud storage backends (S3, etc.) |
| Code Search | django-osoul | Latest | Code search functionality |
| Audit Trail | django-simple-history | Latest | Model change history tracking |
| Color Fields | django-colorfield | Latest | Color picker field |
| Crispy Forms | django-crispy-forms | Latest | Form rendering |
| Bird | django-bird | Latest | Additional utilities |
| Pyrefly | pyrefly | 0.45.2+ | Performance monitoring |

---

## Complete Dependency List

### Direct Dependencies (60+ packages)

```
1. bumpver - Version management and bumping
2. django-rq - Redis-based job queue for Django
3. click - Command-line interface creation
4. colorlog - Colored logging output
5. django - Core web framework
6. django-allauth[socialaccount] - Authentication with social providers
7. django-bird - Additional Django utilities
8. django-browser-reload - Auto-reload on file changes
9. django-colorfield - Color picker field
10. django-crispy-forms - Form rendering
11. django-debug-toolbar - Development debugging tools
12. django-embed-video - Video embedding
13. django-environ - Environment variable management
14. django-extensions - Enhanced Django shell and utilities
15. django-heroicons - Heroicons icon library
16. django-htmx - HTMX integration
17. django-import-export - Data import/export
18. django-ninja - Modern REST API framework
19. django-ninja-extra - Extended Django Ninja features
20. django-ninja-jwt - JWT authentication for Django Ninja
21. django-prometheus - Prometheus metrics collection
22. django-redis - Redis cache backend
23. django-silk - Request profiling and analysis
24. django-simple-history - Model change history tracking
25. django-structlog - Structured logging
26. django-stubs - Type hints for Django
27. django-tables2 - HTML table generation
28. django-unfold - Modern Bootstrap 5 admin dashboard
29. django-volt - Bootstrap 5 admin dashboard starter
30. django-webpack-loader - Webpack asset loading
31. draftjs-exporter - Draft.js content export
32. dynaconf[vault] - Configuration management with vault
33. environ - Environment variable utilities
34. fido2 - FIDO2 hardware security key support
35. fire - CLI generation from Python objects
36. gunicorn - Production WSGI server
37. jwt - JSON Web Token handling
38. livereload - Live reload server
39. marshmallow - Object serialization
40. ninja - Ninja framework utilities
41. psycopg - PostgreSQL adapter
42. psycopg-binary - PostgreSQL adapter (binary)
43. pydantic - Data validation
44. pydantic-settings - Settings management
45. pyrefly - Performance monitoring
46. python-json-logger - JSON formatted logging
47. sentry-sdk[django] - Error and exception tracking
48. structlog - Structured logging
49. twilio - SMS and communication services
50. uvicorn - ASGI server
51. virtualenv - Virtual environment management
52. wagtail - Content management system
53. wagtail-font-awesome-svg - Font Awesome SVG icons
54. wagtail-newsletter[mailchimp] - Newsletter management
55. wagtail-transfer - Content transfer between instances
56. wagtailfontawesome - Font Awesome for Wagtail
57. watchfiles - File system monitoring
58. whitenoise - Static file serving
59. yml - YAML parsing
60. jinja2 - Template engine
61. stripe - Payment processing
62. django-paypal - PayPal integration
63. hypothesis - Property-based testing
64. django-osoul - Code search functionality
65. django-storages[boto3] - Cloud storage backends
66. pytest-django - Django testing framework
```

### Transitive Dependencies

The system includes numerous transitive dependencies pulled in by the direct dependencies above. These are automatically managed by the package manager and include:

- Django core dependencies (sqlparse, asgiref, etc.)
- Wagtail dependencies (Pillow, Django REST Framework, etc.)
- Authentication dependencies (requests, oauthlib, etc.)
- Database dependencies (psycopg2-binary, etc.)
- Monitoring dependencies (prometheus-client, etc.)
- And many others

---

## Compatibility Status

### Framework Compatibility

✅ **Wagtail CMS**: Fully compatible and actively used
- Version: Latest stable
- Status: Primary CMS framework
- All 267 migrations applied successfully
- All models functional

✅ **Django-Unfold**: Fully compatible
- Version: Latest stable
- Status: Modern admin dashboard
- Bootstrap 5 integration complete
- All admin customizations working

✅ **Django Ninja**: Fully compatible
- Version: Latest stable
- Status: Modern REST API framework
- JWT authentication configured
- All API endpoints functional

✅ **Bootstrap 5**: Fully compatible
- Version: 5.x
- Status: Used throughout frontend
- All templates updated
- No Bootstrap 3 legacy code

### Python Version Compatibility

✅ **Python 3.11+**: Fully supported
- Minimum version: 3.11
- All dependencies compatible
- Type hints available
- Modern Python features utilized

### Database Compatibility

✅ **PostgreSQL 15+**: Fully supported
- Version: 15 or higher
- Driver: psycopg 3.3.2+
- 267 migrations applied
- All models functional
- Connection pooling configured

### Deprecated Dependencies

❌ **django-seed**: NOT present
- Status: Removed
- Replacement: django-volt
- Migration: Complete

---

## Architecture Layers

### Presentation Layer
- **Technology**: Bootstrap 5, HTMX, JavaScript
- **Components**: Templates, static assets, client-side logic
- **Responsibility**: User interface rendering and interaction

### Application Layer
- **Technology**: Django, Wagtail CMS, django-unfold
- **Components**: Views, forms, business logic
- **Responsibility**: Request handling and business logic execution

### API Layer
- **Technology**: Django Ninja, Django REST Framework
- **Components**: API endpoints, serializers, authentication
- **Responsibility**: RESTful API provision for frontend and external clients

### Data Layer
- **Technology**: PostgreSQL, Redis, django-redis
- **Components**: Models, migrations, database schema
- **Responsibility**: Data persistence and caching

### Infrastructure Layer
- **Technology**: Docker, Nginx, Traefik
- **Components**: Containers, reverse proxy, networking
- **Responsibility**: Service orchestration and routing

---

## Data Flow

### User Request Flow (Frontend)

```
User Request (site.structa.cloud)
    ↓
Reverse Proxy (Host header matching)
    ↓
Frontend Service (Django + Wagtail)
    ↓
Django Views/Wagtail Pages
    ↓
API Backend (Django Ninja) [if needed]
    ↓
Database (PostgreSQL)
    ↓
Response chain back to user
```

### API Request Flow

```
API Request (core.structa.cloud)
    ↓
Reverse Proxy (Host header matching)
    ↓
API Backend (Django Ninja)
    ↓
Serializers & Validation
    ↓
Database (PostgreSQL)
    ↓
JSON Response back to client
```

### Documentation Request Flow

```
Documentation Request (site-docs.structa.cloud)
    ↓
Reverse Proxy (Host header matching)
    ↓
Docsify Service (nginx:alpine)
    ↓
/docs volume (markdown files)
    ↓
Docsify client-side rendering
    ↓
HTML response to user
```

---

## Configuration Management

### Environment Variables

**Core Django Settings**
```
SECRET_KEY=<random-secret-key>
DEBUG=False
ALLOWED_HOSTS=site.structa.cloud,core.structa.cloud
```

**Database Configuration**
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_db
DB_USER=postgres
DB_PASSWORD=<secure-password>
DB_HOST=postgres
DB_PORT=5432
```

**Service Hosts**
```
FRONTEND_HOST=site.structa.cloud
API_HOST=core.structa.cloud
DOCS_HOST=site-docs.structa.cloud
LMS_HOST=lms.structa.cloud
```

**Security Settings**
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Settings Structure

The Django settings are organized as follows:

```python
# Core settings
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Installed Apps
INSTALLED_APPS = [
    'django_unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'wagtail',
    'wagtail.admin',
    'wagtail.search',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.contrib.redirects',
    'wagtail.contrib.forms',
    'wagtail.contrib.table_block',
    'wagtail.contrib.typed_table_block',
    'wagtail.search.backends.database',
    'django_ninja',
    'django_allauth',
    'django_allauth.account',
    'django_allauth.socialaccount',
    # Project apps
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

---

## Deployment Architecture

### Docker Services

**Reverse Proxy Service**
- Image: nginx:alpine
- Ports: 80, 443
- Role: Route requests to backend services
- Configuration: nginx.conf

**Frontend Service**
- Image: Custom Django image
- Port: 8000 (internal)
- Role: Serve user-facing application
- Framework: Django + Wagtail + django-unfold

**API Backend Service**
- Image: Custom Django image
- Port: 8001 (internal)
- Role: Provide REST API
- Framework: Django + Django Ninja

**Docsify Service**
- Image: nginx:alpine
- Port: 80 (internal)
- Role: Serve documentation
- Volume: /docs

**LMS Service**
- Image: nginx:alpine
- Port: 80 (internal)
- Role: Maintenance mode placeholder
- Status: Coming Soon

**Database Service**
- Image: postgres:15-alpine
- Port: 5432 (internal)
- Role: Data persistence
- Volume: postgres_data

### Docker Network

All services are connected via a custom bridge network (`app-network`):

```
Docker Network: app-network (bridge)
├── reverse-proxy (nginx:alpine)
├── frontend (Django application)
├── api-backend (Django REST API)
├── docsify (nginx:alpine)
├── lms (nginx:alpine)
└── postgres (PostgreSQL)
```

### Domain Routing

| Domain | Service | Port | Purpose |
|--------|---------|------|---------|
| site-docs.structa.cloud | Docsify | 80 | Technical Documentation |
| site.structa.cloud | Frontend | 8000 | User-facing Application |
| core.structa.cloud | API Backend | 8001 | REST API |
| lms.structa.cloud | LMS | 80 | Learning Management (Maintenance) |

---

## Performance Considerations

### Caching Strategy

- **Redis**: In-memory caching for frequently accessed data
- **Django Cache**: Configured with django-redis backend
- **Static Files**: Served with whitenoise for efficiency
- **Browser Cache**: Cache headers configured for static assets

### Database Optimization

- **Connection Pooling**: Configured for efficient database access
- **Query Optimization**: Django ORM with select_related and prefetch_related
- **Indexing**: Proper database indexes on frequently queried fields
- **Migrations**: 267 applied migrations with optimized schema

### Monitoring & Metrics

- **Prometheus**: Metrics collection via django-prometheus
- **Sentry**: Error tracking and monitoring
- **Django Silk**: Request profiling and analysis
- **Structured Logging**: Comprehensive logging with context

---

## Security Considerations

### Authentication & Authorization

- **django-allauth**: Multi-provider authentication
- **JWT Tokens**: Secure token-based authentication
- **FIDO2**: Hardware security key support
- **Session Management**: Secure session handling

### Data Protection

- **SSL/TLS**: HTTPS encryption for all traffic
- **CSRF Protection**: Django CSRF middleware
- **SQL Injection Prevention**: Django ORM parameterized queries
- **XSS Prevention**: Template auto-escaping

### Infrastructure Security

- **Reverse Proxy**: Single entry point for all traffic
- **Docker Network**: Isolated network for services
- **Environment Variables**: Sensitive data in environment
- **No Direct Access**: Backend services not directly exposed

---

## Maintenance & Updates

### Dependency Management

- **Regular Updates**: Keep dependencies current
- **Security Patches**: Apply security updates promptly
- **Compatibility Testing**: Test updates before deployment
- **Version Pinning**: Pin critical dependencies

### Monitoring & Alerts

- **Error Tracking**: Sentry for exception monitoring
- **Performance Metrics**: Prometheus for system metrics
- **Request Profiling**: Django Silk for request analysis
- **Logging**: Structured logging for debugging

### Backup & Recovery

- **Database Backups**: Regular PostgreSQL backups
- **Volume Backups**: Docker volume backups
- **Configuration Backups**: Version control for configs
- **Disaster Recovery**: Documented recovery procedures

---

## Future Considerations

### Planned Enhancements

- **LMS Service**: Full Learning Management System implementation
- **Blog Service**: Blog platform with content management
- **Advanced Analytics**: Enhanced analytics and reporting
- **Mobile App**: Native mobile application support

### Scalability

- **Horizontal Scaling**: Multiple frontend/API instances
- **Load Balancing**: Advanced load balancing strategies
- **Database Replication**: Master-slave database setup
- **Caching Layers**: Additional caching strategies

### Technology Evolution

- **Python Updates**: Upgrade to newer Python versions
- **Django Updates**: Keep Django framework current
- **Dependency Updates**: Regular dependency updates
- **New Features**: Adopt new framework features

---

## Summary

The system architecture is built on a modern, well-maintained technology stack with:

- ✅ Wagtail CMS for content management
- ✅ django-unfold for modern admin interface
- ✅ Django Ninja for REST API
- ✅ PostgreSQL for data persistence
- ✅ Redis for caching
- ✅ Docker for containerization
- ✅ Nginx for reverse proxy routing
- ✅ 60+ direct dependencies with comprehensive functionality
- ✅ 267 applied database migrations
- ✅ Bootstrap 5 throughout frontend
- ✅ Comprehensive monitoring and logging

The architecture is production-ready, scalable, and maintainable with clear separation of concerns and modern best practices throughout.
