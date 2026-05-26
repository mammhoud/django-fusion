# Project Modernization Design Document

**Category Context: Modernization & Updates**
- **Category**: Modernization
- **Scope**: System upgrades, technology updates, performance optimizations, refactoring
- **Related Specs**: project-modernization, structa-color-update
- **Common Patterns**: Technology stack updates, UI/UX improvements, performance optimization
- **Avoid Duplicates**: Check existing modernization specs before creating new update features


## Overview

The project modernization initiative focuses on two integrated components:

1. **Docsify Documentation System**: Centralized technical documentation with legacy content recovery and organized structure
2. **Docker Multi-Domain Infrastructure**: Containerized services with reverse proxy routing supporting multiple subdomains

The project's core architecture is already modernized with Wagtail CMS and django-unfold admin interface (Bootstrap 5), so framework migration is not required. The modernization effort focuses on documentation centralization and containerized deployment infrastructure.

### Key Objectives

- Centralize and organize technical documentation for improved accessibility
- Implement containerized multi-domain infrastructure with intelligent routing
- Preserve existing functionality and data integrity throughout modernization
- Establish clear processes for ongoing maintenance and documentation updates
- Document the current Wagtail CMS + django-unfold architecture for future reference

---

## Architecture

### System Architecture Diagram

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
   │ (nginx:     │   │ (Django     │   │              │
   │  alpine)    │   │  Frontend)  │   │              │
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
  - site.structa.cloud → Frontend Service
  - core.structa.cloud → API Backend
  - lms.structa.cloud → LMS Service (Maintenance)
```

### Service Architecture

**Reverse Proxy Layer**
- Routes incoming requests based on Host headers
- Terminates SSL/TLS connections
- Forwards requests to appropriate backend services
- Preserves Host headers for backend processing
- Handles 404 responses for unrecognized domains

**Frontend Service**
- Django application with django-volt Bootstrap 5 admin dashboard
- Serves user-facing web interface
- Communicates with API Backend for data operations
- Accessible via site.structa.cloud

**API Backend**
- Django REST API providing core business logic
- Handles data persistence and business operations
- Accessible via core.structa.cloud
- Shared database with Frontend Service

**Docsify Service**
- nginx:alpine container serving static documentation
- Renders markdown files dynamically via Docsify client
- Accessible via site-docs.structa.cloud
- Mounted /docs volume from host

**LMS Service**
- Placeholder service in maintenance mode
- Returns "Coming Soon" status
- Accessible via lms.structa.cloud
- Future implementation planned

### Data Flow

```
User Request (site-docs.structa.cloud)
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

User Request (site.structa.cloud)
    ↓
Reverse Proxy (Host header matching)
    ↓
Frontend Service (Django)
    ↓
API Backend (Django REST)
    ↓
Database (PostgreSQL/SQLite)
    ↓
Response chain back to user
```

---

## Components and Interfaces

### 1. Current Architecture Documentation

#### Wagtail CMS + Django-Unfold Architecture

**Current Framework Status**

The project uses a modern, well-architected stack:

1. **CMS Platform**: Wagtail CMS (comprehensive content management system)
2. **Admin Interface**: django-unfold (modern Bootstrap 5 admin dashboard)
3. **API Framework**: Django Ninja (modern REST API framework)
4. **Authentication**: django-allauth (with social provider support)
5. **Database**: PostgreSQL with 267 applied migrations
6. **Frontend**: Bootstrap 5 with Webpack integration

**Architecture Diagram**

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

**Technology Stack**

- **Framework**: Wagtail CMS (not django-seed)
- **Admin**: django-unfold with Bootstrap 5 (not django-seed admin)
- **API**: Django Ninja (modern REST framework)
- **Auth**: django-allauth with social providers
- **Database**: PostgreSQL with 267 migrations
- **Frontend**: Bootstrap 5 with Webpack
- **Caching**: Redis with django-redis
- **Monitoring**: Prometheus, Sentry, django-silk
- **Logging**: Structured logging with django-structlog

**Compatibility Status**

✅ All components are modern and well-maintained
✅ Bootstrap 5 used throughout (not Bootstrap 3)
✅ No django-seed dependencies found
✅ All 267 migrations applied successfully
✅ All models functional and compatible
✅ Ready for containerization and documentation

#### Library Audit Process

**Audit Scope**

The library audit documents all project dependencies:

1. **Direct Dependencies**
   - All packages listed in pyproject.toml
   - Version numbers and constraints
   - Purpose and usage context
   - Compatibility with current architecture

2. **Transitive Dependencies**
   - Dependencies of direct dependencies
   - Version resolution and conflicts
   - Security vulnerability status
   - Update availability

3. **Compatibility Assessment**
   - Python version compatibility
   - Wagtail CMS compatibility
   - django-unfold compatibility
   - Known issues or deprecations

**Audit Documentation Structure**

Location: `/docs/libraries/dependencies.md`

```markdown
# Project Dependencies Audit

## Summary
- Total Dependencies: X
- Compatible: Y
- Requires Review: Z
- Deprecated: W

## Direct Dependencies

### wagtail
- Version: X.Y.Z
- Purpose: Content Management System
- Compatibility: ✓ Compatible
- Notes: Primary CMS framework

### django-unfold
- Version: X.Y.Z
- Purpose: Modern Admin Dashboard
- Compatibility: ✓ Compatible
- Notes: Bootstrap 5 admin interface

### [Package Name]
- Version: X.Y.Z
- Purpose: [Description]
- Compatibility: [Status]
- Notes: [Any relevant information]

## Transitive Dependencies
[Detailed list with versions]

## Compatibility Issues
[Any identified issues and resolutions]

## Recommendations
[Suggested updates or replacements]
```

#### Backward Compatibility Approach

**Model and Migration Preservation**

- No modifications to existing Django models
- All existing migrations remain unchanged
- New migrations created only for new features
- Database schema remains compatible

**API Endpoint Continuity**

- All existing REST API endpoints continue functioning
- Response formats unchanged
- Authentication mechanisms preserved
- Deprecation warnings added for future changes

**Custom Code Adaptation**

- All custom views and utilities remain functional
- Wagtail CMS integration preserved
- django-unfold admin customizations maintained
- Document any breaking changes for future updates

### 2. Docsify Documentation Component

#### Directory Structure

```
/docs/
├── index.html              # Docsify entry point
├── .nojekyll              # GitHub Pages marker
├── README.md              # Documentation homepage
├── _sidebar.md            # Navigation configuration
├── getting-started/
│   ├── README.md          # Getting started overview
│   ├── installation.md    # Installation guide
│   ├── setup.md           # Initial setup
│   └── configuration.md   # Configuration guide
├── libraries/
│   ├── README.md          # Libraries overview
│   ├── dependencies.md    # Complete dependency audit
│   ├── [package-name].md  # Individual package docs
│   └── migration-notes.md # django-seed → django-volt notes
├── api/
│   ├── README.md          # API overview
│   ├── authentication.md  # Auth documentation
│   ├── endpoints.md       # Endpoint reference
│   └── examples.md        # Usage examples
├── deployment/
│   ├── README.md          # Deployment overview
│   ├── docker-setup.md    # Docker configuration
│   ├── environment.md     # Environment variables
│   ├── migration-guide.md # Configuration migration
│   └── documentation-maintenance.md
├── lms/
│   └── README.md          # LMS placeholder
└── blog/
    └── README.md          # Blog placeholder
```

#### Docsify Configuration

**index.html**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Project Documentation</title>
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify/lib/themes/vue.css">
    <style>
        :root {
            --primary-color: #2c3e50;
            --text-color: #34495e;
            --border-color: #eaeaea;
            --code-theme-background: #f5f5f5;
        }
    </style>
</head>
<body>
    <div id="app"></div>
    <script>
        window.$docsify = {
            name: 'Project Documentation',
            repo: 'https://github.com/[org]/[repo]',
            loadSidebar: true,
            loadNavbar: false,
            coverpage: false,
            onlyCover: false,
            maxLevel: 3,
            subMaxLevel: 2,
            search: {
                maxAge: 86400000,
                paths: 'auto',
                placeholder: 'Search documentation...',
                noData: 'No results found',
                depth: 3,
            },
            plugins: [
                function(hook, vm) {
                    hook.beforeEach(function(html) {
                        return html;
                    });
                }
            ]
        };
    </script>
    <script src="//cdn.jsdelivr.net/npm/docsify/lib/docsify.min.js"></script>
    <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/search.min.js"></script>
    <script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/emoji.min.js"></script>
</body>
</html>
```

**_sidebar.md**

```markdown
- [Home](/)
- Getting Started
  - [Installation](/getting-started/installation.md)
  - [Setup](/getting-started/setup.md)
  - [Configuration](/getting-started/configuration.md)
- Libraries
  - [Overview](/libraries/README.md)
  - [Dependencies](/libraries/dependencies.md)
  - [Migration Notes](/libraries/migration-notes.md)
- API
  - [Overview](/api/README.md)
  - [Authentication](/api/authentication.md)
  - [Endpoints](/api/endpoints.md)
  - [Examples](/api/examples.md)
- Deployment
  - [Overview](/deployment/README.md)
  - [Docker Setup](/deployment/docker-setup.md)
  - [Environment Variables](/deployment/environment.md)
  - [Migration Guide](/deployment/migration-guide.md)
  - [Documentation Maintenance](/deployment/documentation-maintenance.md)
- Future
  - [LMS](/lms/README.md) 🚧
  - [Blog](/blog/README.md) 🚧
```

#### Documentation Sections

**Getting Started**
- Project overview and purpose
- Installation instructions for development environment
- Initial setup and configuration
- Running the application locally
- Common troubleshooting

**Libraries**
- Complete dependency audit with versions
- Purpose and usage of each library
- Compatibility notes with django-volt
- Migration notes from django-seed
- Recommended alternatives for deprecated packages

**API**
- Authentication mechanisms and token management
- Complete endpoint reference with request/response examples
- Error handling and status codes
- Rate limiting and quotas
- Integration examples

**Deployment**
- Docker Compose configuration and usage
- Environment variable documentation
- Multi-domain infrastructure setup
- Configuration migration from django-seed to django-volt
- Troubleshooting deployment issues
- Documentation maintenance procedures

#### Legacy Documentation Recovery

**Recovery Process**

1. **Identify Deleted Files**
   ```bash
   git log --diff-filter=D --summary | grep delete | grep -E "\.(md|rst)$"
   ```

2. **Restore Content**
   ```bash
   git show <commit>:<path-to-file> > recovered-file.md
   ```

3. **Adapt for Django-Volt**
   - Update code examples to use django-volt patterns
   - Replace django-seed-specific configuration
   - Update import statements and module references
   - Verify all examples are functional

4. **Integrate into New Structure**
   - Place recovered documentation in appropriate section
   - Update internal links to new /docs structure
   - Add cross-references from related documents
   - Test all links and rendering

**Content Adaptation Examples**

```markdown
# Before (django-seed)
from django_seed import seeder
seeder.add_entity(User, 10)

# After (django-volt)
from django_volt.utils import create_sample_data
create_sample_data(User, 10)
```

#### Placeholder Pages for LMS and Blog

**LMS Placeholder** (`/docs/lms/README.md`)

```markdown
# Learning Management System

🚧 **Coming Soon**

The Learning Management System is currently under development and will be available in Q2 2024.

## Planned Features

- Course management and enrollment
- Student progress tracking
- Assessment tools
- Gradebook integration
- Discussion forums

## Expected Availability

Q2 2024

For questions or to express interest, please contact the development team.
```

**Blog Placeholder** (`/docs/blog/README.md`)

```markdown
# Blog

🚧 **Coming Soon**

The Blog feature is currently under development and will be available in Q3 2024.

## Planned Features

- Article publishing and management
- Category and tag organization
- Comment system
- Social sharing
- Search functionality

## Expected Availability

Q3 2024

For questions or to express interest, please contact the development team.
```

### 3. Docker Multi-Domain Infrastructure Component

#### Docker Compose Structure

**Service Definitions**

```yaml
version: '3.8'

services:
  reverse-proxy:
    image: nginx:alpine
    container_name: reverse-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./compose/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./compose/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./compose/nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - app-network
    depends_on:
      - frontend
      - api-backend
      - docsify
      - lms
    environment:
      - NGINX_HOST=structa.cloud
      - NGINX_PORT=80

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: frontend-service
    expose:
      - "8000"
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=site.structa.cloud
      - DATABASE_URL=postgresql://user:pass@postgres:5432/frontend_db
    networks:
      - app-network
    depends_on:
      - postgres
    volumes:
      - ./:/app

  api-backend:
    build:
      context: .
      dockerfile: Dockerfile.api
    container_name: api-backend-service
    expose:
      - "8001"
    environment:
      - DEBUG=False
      - ALLOWED_HOSTS=core.structa.cloud
      - DATABASE_URL=postgresql://user:pass@postgres:5432/api_db
    networks:
      - app-network
    depends_on:
      - postgres
    volumes:
      - ./:/app

  docsify:
    image: nginx:alpine
    container_name: docsify-service
    expose:
      - "80"
    volumes:
      - ./docs:/usr/share/nginx/html:ro
      - ./compose/nginx/docsify.conf:/etc/nginx/conf.d/default.conf:ro
    networks:
      - app-network
    environment:
      - NGINX_HOST=site-docs.structa.cloud

  lms:
    image: nginx:alpine
    container_name: lms-service
    expose:
      - "80"
    volumes:
      - ./compose/lms/maintenance.html:/usr/share/nginx/html/index.html:ro
    networks:
      - app-network
    environment:
      - NGINX_HOST=lms.structa.cloud

  postgres:
    image: postgres:15-alpine
    container_name: postgres-db
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_MULTIPLE_DATABASES=frontend_db,api_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./compose/postgres/init.d:/docker-entrypoint-initdb.d
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

#### Docsify Service Configuration

**Nginx Configuration for Docsify** (`compose/nginx/docsify.conf`)

```nginx
server {
    listen 80;
    server_name site-docs.structa.cloud;

    root /usr/share/nginx/html;
    index index.html;

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Serve markdown files with correct content type
    location ~* \.md$ {
        add_header Content-Type "text/markdown; charset=utf-8";
        expires 1h;
    }

    # Docsify client-side routing
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # Error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
```

#### Reverse Proxy Configuration

**Nginx Reverse Proxy** (`compose/nginx/nginx.conf`)

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Upstream definitions
    upstream frontend_backend {
        server frontend:8000;
    }

    upstream api_backend {
        server api-backend:8001;
    }

    upstream docsify_backend {
        server docsify:80;
    }

    upstream lms_backend {
        server lms:80;
    }

    # HTTP to HTTPS redirect (when SSL is configured)
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server block
    server {
        listen 443 ssl http2;
        server_name site.structa.cloud;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://frontend_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 443 ssl http2;
        server_name core.structa.cloud;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 443 ssl http2;
        server_name site-docs.structa.cloud;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://docsify_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    server {
        listen 443 ssl http2;
        server_name lms.structa.cloud;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://lms_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Catch-all for unrecognized domains
    server {
        listen 443 ssl http2 default_server;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        return 404;
    }
}
```

#### Domain Routing Table

| Domain | Service | Port | Purpose | Status |
|--------|---------|------|---------|--------|
| site-docs.structa.cloud | Docsify | 80 | Technical Documentation | Active |
| site.structa.cloud | Frontend | 8000 | User-facing Application | Active |
| core.structa.cloud | API Backend | 8001 | REST API | Active |
| lms.structa.cloud | LMS | 80 | Learning Management | Maintenance |

#### Docker Network Configuration

**Network Architecture**

```
Docker Network: app-network (bridge)
├── reverse-proxy (nginx:alpine)
│   ├── Listens on 0.0.0.0:80 and 0.0.0.0:443
│   └── Routes to internal services via container names
├── frontend (Django application)
│   ├── Exposes port 8000
│   └── Accessible as "frontend" on network
├── api-backend (Django REST API)
│   ├── Exposes port 8001
│   └── Accessible as "api-backend" on network
├── docsify (nginx:alpine)
│   ├── Exposes port 80
│   └── Accessible as "docsify" on network
├── lms (nginx:alpine)
│   ├── Exposes port 80
│   └── Accessible as "lms" on network
└── postgres (PostgreSQL)
    ├── Exposes port 5432
    └── Accessible as "postgres" on network
```

**Network Communication**

- All containers can communicate using container names as hostnames
- Reverse proxy forwards requests to backend services using container names
- Backend services can communicate with database using "postgres" hostname
- No direct external access to backend services (only through reverse proxy)

#### Host Header Preservation Strategy

**Header Forwarding**

The reverse proxy preserves Host headers to maintain domain information:

```nginx
proxy_set_header Host $host;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

**Backend Processing**

Django applications receive original Host header:

```python
# In Django settings
ALLOWED_HOSTS = ['site.structa.cloud', 'core.structa.cloud']

# In views
def get_domain(request):
    return request.META.get('HTTP_HOST')
```

**Benefits**

- Backend services know which domain was requested
- Proper CSRF token validation based on domain
- Correct URL generation for redirects
- Session cookie domain handling

---

## Data Models

### Configuration Data Model

**Django Settings Structure**

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

# Django-Volt specific
INSTALLED_APPS = [
    'django_volt',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
]

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

### Environment Variables Model

**Required Variables**

```
# Django Configuration
SECRET_KEY=<random-secret-key>
DEBUG=False
ALLOWED_HOSTS=site.structa.cloud,core.structa.cloud

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=project_db
DB_USER=postgres
DB_PASSWORD=<secure-password>
DB_HOST=postgres
DB_PORT=5432

# Services
FRONTEND_HOST=site.structa.cloud
API_HOST=core.structa.cloud
DOCS_HOST=site-docs.structa.cloud
LMS_HOST=lms.structa.cloud

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Documentation Data Model

**Markdown File Structure**

```
Document {
  title: string
  path: string
  section: enum(getting-started|libraries|api|deployment|lms|blog)
  content: markdown
  last_updated: datetime
  author: string
  status: enum(draft|published|deprecated)
  related_documents: [Document]
}
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Before writing correctness properties, I need to analyze the acceptance criteria for testability.


### Property 1: Django-Volt Dependency Replacement

*For any* requirements.txt file, after migration, django-seed should not be present and django-volt should be present with a valid version specifier.

**Validates: Requirements 1.1**

### Property 2: Django-Volt Module Availability

*For any* installed django-volt package, all core modules (admin, models, views, forms, templates) should be importable without errors.

**Validates: Requirements 1.2**

### Property 3: Configuration Migration Completeness

*For any* Django settings.py file after migration, no django-seed-specific configuration keys should remain (e.g., DJANGO_SEED_*, legacy template paths).

**Validates: Requirements 1.3**

### Property 4: Database Model Preservation

*For any* existing database model, the model definition and all associated migrations should remain unchanged after framework migration.

**Validates: Requirements 1.4**

### Property 5: Template Adaptation

*For any* custom django-seed template, after adaptation, it should contain django-volt-specific patterns (Bootstrap 5 classes, django-volt template tags) and no django-seed-specific patterns.

**Validates: Requirements 1.7**

### Property 6: Library Audit Completeness

*For any* dependency in requirements.txt, the library audit document should contain an entry with version number, purpose, and compatibility status.

**Validates: Requirements 2.1**

### Property 7: Transitive Dependency Documentation

*For any* transitive dependency identified by pip freeze, it should appear in the library audit document with version information.

**Validates: Requirements 2.2**

### Property 8: Dependency Compatibility Assessment

*For any* dependency in the audit, it should have a documented compatibility status (compatible, requires review, or deprecated).

**Validates: Requirements 2.3**

### Property 9: Incompatibility Documentation

*For any* dependency flagged as incompatible, the audit should document recommended alternatives.

**Validates: Requirements 2.4**

### Property 10: Audit File Existence and Location

The file `/docs/libraries/dependencies.md` should exist and contain a complete library audit with summary section.

**Validates: Requirements 2.5, 2.6**

### Property 11: Deprecated Library Recommendations

*For any* deprecated library in the audit, a modern alternative and migration path should be documented.

**Validates: Requirements 2.7**

### Property 12: Documentation Directory Structure

*For any* required documentation directory (getting-started, libraries, api, deployment, lms, blog), the directory should exist at `/docs/{section}/`.

**Validates: Requirements 3.1, 5.1**

### Property 13: Docsify Configuration

The file `/docs/index.html` should exist and contain Docsify configuration with theme, search functionality, and navigation settings.

**Validates: Requirements 3.2**

### Property 14: Navigation Sidebar Configuration

The file `/docs/_sidebar.md` should exist and contain navigation entries for all documentation sections (getting-started, libraries, api, deployment, lms, blog).

**Validates: Requirements 3.3, 5.6**

### Property 15: Documentation Homepage

The file `/docs/README.md` should exist and contain project overview and links to main documentation sections.

**Validates: Requirements 3.4**

### Property 16: Markdown File Validity

*For any* markdown file in the /docs directory, it should be valid markdown with proper formatting and all internal links should reference existing files.

**Validates: Requirements 3.5**

### Property 17: Placeholder File Existence

*For any* empty documentation section, a placeholder file should exist with section description.

**Validates: Requirements 3.6**

### Property 18: Legacy Documentation Recovery

*For any* deleted django-seed documentation file identified via git log, a recovered and adapted version should exist in the /docs directory.

**Validates: Requirements 4.2**

### Property 19: Link Migration

*For any* internal link in migrated documentation, it should reference the new /docs structure (not old paths).

**Validates: Requirements 4.3**

### Property 20: Code Example Compatibility

*For any* code example in migrated documentation, it should not contain django-seed-specific patterns and should be compatible with django-volt.

**Validates: Requirements 4.4**

### Property 21: Configuration Documentation Translation

*For any* configuration setting in migrated documentation, django-seed-specific settings should be translated to django-volt equivalents.

**Validates: Requirements 4.5**

### Property 22: Deprecation Documentation

*For any* removed feature referenced in documentation, a deprecation note and migration guidance should be present.

**Validates: Requirements 4.6**

### Property 23: Documentation Section Population

*For any* documentation section (getting-started, libraries, api, deployment), required files should exist with appropriate content.

**Validates: Requirements 5.2, 5.3, 5.4, 5.5**

### Property 24: LMS Placeholder Page

The file `/docs/lms/README.md` should exist and contain "Coming Soon" badge and description of planned LMS features.

**Validates: Requirements 6.1, 6.2, 6.5**

### Property 25: Blog Placeholder Page

The file `/docs/blog/README.md` should exist and contain "Coming Soon" badge and description of planned Blog features.

**Validates: Requirements 6.1, 6.2, 6.5**

### Property 26: Placeholder Navigation

The file `/docs/_sidebar.md` should contain entries for LMS and Blog sections.

**Validates: Requirements 6.3**

### Property 27: Docsify Service Configuration

The docker-compose.yaml file should contain a Docsify service definition using nginx:alpine image with /docs volume mount.

**Validates: Requirements 7.1, 7.2**

### Property 28: Docsify Service Port Exposure

The Docsify service in docker-compose.yaml should expose an internal port (not external) for reverse proxy routing.

**Validates: Requirements 7.3, 7.7**

### Property 29: Nginx Docsify Configuration

An nginx configuration file should exist for Docsify with proper mime types, cache headers, and markdown content type settings.

**Validates: Requirements 7.5, 11.1, 11.3, 11.4**

### Property 30: Docsify Service Environment Variables

The Docsify service in docker-compose.yaml should define required environment variables.

**Validates: Requirements 7.6**

### Property 31: Reverse Proxy Routing Rules

The reverse proxy configuration should contain routing rules for all four subdomains (site-docs.structa.cloud, site.structa.cloud, core.structa.cloud, lms.structa.cloud).

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5, 9.2**

### Property 32: Host Header Preservation

The reverse proxy configuration should include proxy_set_header directives to preserve Host headers to backend services.

**Validates: Requirements 8.6, 9.3**

### Property 33: Unrecognized Domain Handling

The reverse proxy configuration should include a catch-all rule that returns 404 for unrecognized domains.

**Validates: Requirements 8.7**

### Property 34: Reverse Proxy Implementation

The reverse proxy should be implemented using either Nginx or Traefik.

**Validates: Requirements 9.1**

### Property 35: SSL/TLS Configuration

The reverse proxy configuration should include SSL/TLS certificate handling and HTTPS enforcement settings.

**Validates: Requirements 9.6**

### Property 36: Reverse Proxy Logging

The reverse proxy configuration should include logging settings for routing decisions.

**Validates: Requirements 9.7**

### Property 37: Docker Network Definition

The docker-compose.yaml file should define a custom Docker network (bridge driver) for all services.

**Validates: Requirements 10.1**

### Property 38: Service Network Connectivity

*For any* service in docker-compose.yaml, it should reference the custom Docker network in its network configuration.

**Validates: Requirements 10.2**

### Property 39: Container Name Resolution

The reverse proxy configuration should use container names (not IP addresses) to resolve backend service addresses.

**Validates: Requirements 10.4**

### Property 40: Nginx Directory Request Handling

The nginx configuration for Docsify should include try_files directive to serve index.html for directory requests.

**Validates: Requirements 11.2**

### Property 41: Nginx Gzip Compression

The nginx configuration for Docsify should include gzip compression settings for text files.

**Validates: Requirements 11.6**

### Property 42: Infrastructure Verification

*For any* deployed infrastructure, HTTP requests to each domain should return appropriate responses (Docsify docs, Frontend app, API responses, maintenance page).

**Validates: Requirements 12.1, 12.2, 12.3, 12.4**

### Property 43: Host Header Preservation in Responses

*For any* request to a domain, the backend service should receive the correct Host header value.

**Validates: Requirements 12.5**

### Property 44: Service Restart Resilience

*For any* service restart, reverse proxy routing should continue to work correctly for all domains.

**Validates: Requirements 12.6**

### Property 45: Service Unavailability Handling

*For any* unavailable backend service, the reverse proxy should return a 502 Bad Gateway or similar error response.

**Validates: Requirements 12.7**

### Property 46: Migration Guide Existence

The file `/docs/deployment/migration-guide.md` should exist and contain documentation of configuration changes from django-seed to django-volt.

**Validates: Requirements 13.1, 13.2**

### Property 47: Migration Guide Examples

The migration guide should contain before/after examples of key configuration files.

**Validates: Requirements 13.3**

### Property 48: Breaking Changes Documentation

The migration guide should list all breaking changes and how to address them.

**Validates: Requirements 13.4**

### Property 49: Migration Troubleshooting

The migration guide should provide troubleshooting steps for common migration issues.

**Validates: Requirements 13.5**

### Property 50: Custom Code Documentation

The migration guide should document custom code changes and rationale.

**Validates: Requirements 13.6**

### Property 51: Environment Documentation Completeness

The file `/docs/deployment/environment.md` should exist and document all required environment variables for each service.

**Validates: Requirements 14.1**

### Property 52: Environment Variable Classification

The environment documentation should specify which variables are required vs optional.

**Validates: Requirements 14.2**

### Property 53: Environment Variable Examples

The environment documentation should provide example values and valid ranges for each variable.

**Validates: Requirements 14.3**

### Property 54: Environment Variable Explanation

The environment documentation should explain the purpose and impact of each variable.

**Validates: Requirements 14.4**

### Property 55: Environment-Specific Documentation

The environment documentation should include separate sections for development, staging, and production environments.

**Validates: Requirements 14.5**

### Property 56: Security Documentation

The environment documentation should note security considerations and best practices for sensitive variables.

**Validates: Requirements 14.6**

### Property 57: Documentation Maintenance Guide

The file `/docs/deployment/documentation-maintenance.md` should exist and document the process for updating documentation.

**Validates: Requirements 15.1, 15.2**

### Property 58: New Section Addition Process

The documentation maintenance guide should specify how to add new documentation sections.

**Validates: Requirements 15.3**

### Property 59: Sidebar Update Process

The documentation maintenance guide should explain how to update the _sidebar.md navigation.

**Validates: Requirements 15.4**

### Property 60: Documentation Review Process

The documentation maintenance guide should document the review process for documentation changes.

**Validates: Requirements 15.5**

### Property 61: Deprecation Handling

The documentation maintenance guide should specify how to handle deprecated documentation.

**Validates: Requirements 15.6**

---

## Error Handling

### Framework Migration Errors

**Dependency Resolution Failures**
- Error: Conflicting dependency versions during django-volt installation
- Handling: Document incompatibilities in library audit, provide alternative packages
- Recovery: Manual resolution with version pinning or package substitution

**Configuration Migration Errors**
- Error: Django settings.py contains incompatible django-seed configurations
- Handling: Identify incompatible settings, provide django-volt equivalents
- Recovery: Update settings.py with django-volt-compatible configuration

**Template Rendering Errors**
- Error: Custom templates fail to render with django-volt
- Handling: Identify template incompatibilities, adapt to django-volt structure
- Recovery: Update templates with django-volt-compatible markup

### Documentation System Errors

**File Not Found Errors**
- Error: Required documentation files missing from /docs structure
- Handling: Create placeholder files with section descriptions
- Recovery: Populate with actual content as documentation is written

**Link Validation Errors**
- Error: Internal links in documentation reference non-existent files
- Handling: Validate all links during documentation generation
- Recovery: Update links to reference correct file paths

**Markdown Parsing Errors**
- Error: Markdown files contain invalid syntax
- Handling: Validate markdown during build process
- Recovery: Fix markdown syntax errors

### Docker Infrastructure Errors

**Service Connection Errors**
- Error: Reverse proxy cannot connect to backend services
- Handling: Verify services are on same Docker network, check container names
- Recovery: Restart services, verify network configuration

**Port Binding Errors**
- Error: Port already in use when starting containers
- Handling: Check for conflicting services, use different ports
- Recovery: Stop conflicting services or modify port mappings

**Volume Mount Errors**
- Error: Documentation volume not properly mounted in Docsify container
- Handling: Verify volume path in docker-compose.yaml
- Recovery: Correct volume path and restart container

**Host Header Forwarding Errors**
- Error: Backend services receive incorrect Host headers
- Handling: Verify proxy_set_header configuration in reverse proxy
- Recovery: Update reverse proxy configuration with correct header forwarding

### Routing Errors

**Domain Not Recognized**
- Error: Request to unrecognized domain returns 404
- Handling: Verify domain is configured in reverse proxy
- Recovery: Add domain routing rule to reverse proxy configuration

**Service Unavailable**
- Error: Backend service is down, reverse proxy returns 502
- Handling: Check service status, restart if needed
- Recovery: Restart service and verify connectivity

**SSL/TLS Errors**
- Error: HTTPS connection fails due to certificate issues
- Handling: Verify certificate files exist and are valid
- Recovery: Update certificate paths or regenerate certificates

---

## Testing Strategy

### Dual Testing Approach

This project requires both unit testing and property-based testing for comprehensive coverage:

**Unit Testing**
- Specific examples demonstrating correct behavior
- Integration points between components
- Edge cases and error conditions
- Configuration file validation
- File existence and structure verification

**Property-Based Testing**
- Universal properties across all inputs
- Comprehensive input coverage through randomization
- Framework migration correctness
- Documentation structure consistency
- Infrastructure routing behavior

### Unit Testing Strategy

**Framework Migration Tests**
- Verify django-volt dependencies are installed
- Verify django-seed dependencies are removed
- Verify settings.py contains django-volt configuration
- Verify existing models are unchanged
- Verify existing migrations are unchanged

**Documentation Structure Tests**
- Verify /docs directory structure exists
- Verify all required files exist (index.html, _sidebar.md, README.md)
- Verify markdown files are valid
- Verify internal links are valid
- Verify placeholder pages contain "Coming Soon" badges

**Docker Configuration Tests**
- Verify docker-compose.yaml is valid YAML
- Verify all services are defined
- Verify Docsify service uses nginx:alpine
- Verify volume mounts are configured
- Verify network is defined

**Reverse Proxy Configuration Tests**
- Verify nginx/traefik configuration is valid
- Verify all domain routing rules are present
- Verify Host header forwarding is configured
- Verify SSL/TLS settings are present
- Verify catch-all 404 rule exists

### Property-Based Testing Strategy

**Property Test Configuration**
- Minimum 100 iterations per property test
- Each test references its design document property
- Tag format: **Feature: project-modernization, Property {number}: {property_text}**

**Framework Migration Properties**
- Property 1: Django-Volt Dependency Replacement
- Property 2: Django-Volt Module Availability
- Property 3: Configuration Migration Completeness
- Property 4: Database Model Preservation
- Property 5: Template Adaptation

**Documentation Properties**
- Property 12: Documentation Directory Structure
- Property 13: Docsify Configuration
- Property 14: Navigation Sidebar Configuration
- Property 16: Markdown File Validity
- Property 18: Legacy Documentation Recovery

**Infrastructure Properties**
- Property 27: Docsify Service Configuration
- Property 31: Reverse Proxy Routing Rules
- Property 32: Host Header Preservation
- Property 37: Docker Network Definition
- Property 42: Infrastructure Verification

### Testing Implementation

**Test Framework Selection**
- Python: pytest with hypothesis for property-based testing
- YAML validation: yamllint or pyyaml
- Markdown validation: markdown-it-py or similar
- Docker: docker-compose validation and container testing

**Test Organization**
```
tests/
├── unit/
│   ├── test_framework_migration.py
│   ├── test_documentation_structure.py
│   ├── test_docker_configuration.py
│   └── test_reverse_proxy_config.py
├── properties/
│   ├── test_framework_properties.py
│   ├── test_documentation_properties.py
│   └── test_infrastructure_properties.py
└── integration/
    ├── test_docker_services.py
    └── test_routing.py
```

**Continuous Integration**
- Run unit tests on every commit
- Run property tests with 100+ iterations
- Validate all configuration files
- Verify documentation structure
- Test Docker Compose configuration

---

## Implementation Approach

### Phase 1: Framework Migration (django-seed → django-volt)

**Duration:** 2-3 weeks

**Tasks:**
1. Audit current django-seed dependencies and configuration
2. Create requirements.txt with django-volt equivalents
3. Update Django settings.py for django-volt
4. Migrate custom templates to django-volt structure
5. Test admin interface rendering
6. Verify existing models and migrations work
7. Document all configuration changes
8. Create migration guide

**Deliverables:**
- Updated requirements.txt with django-volt
- Updated settings.py
- Migrated templates
- Migration guide documentation
- Library audit document

**Testing:**
- Unit tests for dependency replacement
- Configuration validation tests
- Template rendering tests
- Model and migration integrity tests

### Phase 2: Documentation Setup (Docsify initialization and legacy migration)

**Duration:** 2-3 weeks

**Tasks:**
1. Create /docs directory structure
2. Initialize Docsify with index.html and configuration
3. Create _sidebar.md navigation
4. Create README.md homepage
5. Recover legacy django-seed documentation
6. Adapt legacy documentation for django-volt
7. Create placeholder pages for LMS and Blog
8. Organize documentation into sections
9. Create documentation maintenance guide

**Deliverables:**
- Complete /docs directory structure
- Docsify configuration files
- Recovered and adapted legacy documentation
- Placeholder pages with Coming Soon badges
- Documentation maintenance guide

**Testing:**
- Documentation structure validation
- Markdown file validation
- Link validation
- Docsify configuration validation

### Phase 3: Docker Infrastructure (services, reverse proxy, networking)

**Duration:** 2-3 weeks

**Tasks:**
1. Create docker-compose.yaml with all services
2. Configure Docsify service with nginx:alpine
3. Configure reverse proxy (Nginx or Traefik)
4. Set up Docker network for all services
5. Configure domain routing rules
6. Configure Host header preservation
7. Set up SSL/TLS certificates
8. Create environment configuration documentation
9. Test multi-domain routing
10. Verify service communication

**Deliverables:**
- docker-compose.yaml with all services
- Reverse proxy configuration
- Nginx Docsify configuration
- Environment configuration documentation
- Infrastructure verification tests

**Testing:**
- Docker Compose validation
- Service connectivity tests
- Routing tests for all domains
- Host header preservation tests
- SSL/TLS configuration tests

### Phase Dependencies

```
Phase 1: Framework Migration
    ↓
Phase 2: Documentation Setup (can start after Phase 1 begins)
    ↓
Phase 3: Docker Infrastructure (can start after Phase 2 begins)
    ↓
Integration Testing & Deployment
```

### Verification Strategy

**Post-Migration Verification**
1. Verify all django-volt dependencies are installed
2. Verify Django admin interface renders correctly
3. Verify existing models and migrations work
4. Verify API endpoints continue functioning
5. Verify no django-seed references remain

**Post-Documentation Verification**
1. Verify all documentation files are accessible
2. Verify Docsify renders correctly
3. Verify all links are valid
4. Verify search functionality works
5. Verify placeholder pages display correctly

**Post-Infrastructure Verification**
1. Verify all services start correctly
2. Verify reverse proxy routes to correct services
3. Verify Host headers are preserved
4. Verify SSL/TLS works correctly
5. Verify all domains are accessible
6. Verify service communication works
7. Verify error handling (404, 502, etc.)

---

## Technical Decisions

### Reverse Proxy Choice: Nginx vs Traefik

**Decision: Nginx**

**Rationale:**
- Lightweight and efficient for static routing rules
- Simpler configuration for fixed domain routing
- Lower resource overhead
- Mature and stable for production use
- Easier to troubleshoot and debug
- Better suited for this project's fixed routing requirements

**Alternative Considered: Traefik**
- More dynamic configuration capabilities
- Better for microservices with frequent service changes
- More complex setup for this project's needs
- Higher resource overhead

### Docsify Service Base Image: nginx:alpine

**Decision: nginx:alpine**

**Rationale:**
- Minimal image size (< 50MB)
- Efficient resource usage
- Perfect for serving static documentation
- Alpine Linux provides security updates
- Docsify is client-side rendering, nginx just serves files
- Easy to configure for markdown serving

### Configuration Management Approach

**Environment Variables**
- All sensitive configuration via environment variables
- Separate .env files for different environments
- docker-compose.yaml references environment variables
- No hardcoded secrets in configuration files

**Configuration Files**
- nginx.conf for reverse proxy
- docsify.conf for Docsify service
- settings.py for Django applications
- docker-compose.yaml for service orchestration

### Environment Variable Strategy

**Development Environment**
- DEBUG=True
- ALLOWED_HOSTS=localhost,127.0.0.1
- Database: SQLite or local PostgreSQL
- No SSL/TLS required

**Staging Environment**
- DEBUG=False
- ALLOWED_HOSTS=staging.structa.cloud
- Database: PostgreSQL
- SSL/TLS with self-signed certificates

**Production Environment**
- DEBUG=False
- ALLOWED_HOSTS=structa.cloud,site.structa.cloud,core.structa.cloud,site-docs.structa.cloud,lms.structa.cloud
- Database: PostgreSQL with backups
- SSL/TLS with valid certificates

---

## Integration Points

### Service Communication on Docker Network

**Frontend to API Backend**
- Frontend service makes HTTP requests to http://api-backend:8001
- Uses container name for DNS resolution
- Requests include authentication tokens
- Responses contain JSON data

**Reverse Proxy to Backend Services**
- Reverse proxy forwards requests to backend services using container names
- Preserves Host headers for backend processing
- Handles SSL/TLS termination
- Manages connection pooling

**All Services to Database**
- Services connect to PostgreSQL using "postgres" hostname
- Connection pooling for efficiency
- Shared database for data consistency

### Reverse Proxy Routing Based on Host Headers

**Domain Matching**
```
Request arrives with Host: site-docs.structa.cloud
    ↓
Reverse proxy matches against configured rules
    ↓
Routes to Docsify service (http://docsify:80)
    ↓
Preserves Host header in forwarded request
    ↓
Docsify service receives request with original Host header
```

**Routing Table**
| Host Header | Backend Service | Port |
|-------------|-----------------|------|
| site-docs.structa.cloud | docsify | 80 |
| site.structa.cloud | frontend | 8000 |
| core.structa.cloud | api-backend | 8001 |
| lms.structa.cloud | lms | 80 |
| (unrecognized) | - | 404 |

### Documentation Serving Through Docsify

**Request Flow**
```
User requests: https://site-docs.structa.cloud/getting-started/installation.md
    ↓
Reverse proxy routes to Docsify service
    ↓
Nginx serves /docs/getting-started/installation.md
    ↓
Docsify client-side JavaScript processes markdown
    ↓
HTML rendered in browser
```

**File Serving**
- index.html: Docsify entry point with configuration
- _sidebar.md: Navigation structure
- README.md files: Section overviews
- Markdown files: Content pages
- Static assets: CSS, JavaScript, images

### Legacy Documentation Integration

**Recovery Process**
1. Identify deleted files via git log
2. Restore content from git history
3. Adapt for django-volt context
4. Place in appropriate /docs section
5. Update internal links
6. Verify rendering in Docsify

**Integration Points**
- Links from new documentation to recovered content
- Cross-references between sections
- Search functionality includes recovered content
- Navigation sidebar includes recovered pages

---

## Design Review Checklist

- [ ] All 15 requirements are addressed in the design
- [ ] Architecture diagram clearly shows all components and interactions
- [ ] Data flow is documented for all major operations
- [ ] Configuration changes from django-seed to django-volt are specified
- [ ] Docker Compose structure includes all required services
- [ ] Reverse proxy routing rules cover all four domains
- [ ] Host header preservation strategy is documented
- [ ] Error handling covers all major failure scenarios
- [ ] Testing strategy includes both unit and property-based tests
- [ ] Implementation phases are clearly defined with dependencies
- [ ] Technical decisions are justified with rationale
- [ ] Integration points between services are documented
- [ ] Environment variable strategy covers all environments
- [ ] Documentation structure supports all required sections
- [ ] Placeholder pages for LMS and Blog are designed

---

## Next Steps

This design document provides comprehensive guidance for implementation. The next phase will involve:

1. **Requirements Review**: Confirm all requirements are adequately addressed
2. **Design Feedback**: Gather feedback on technical decisions and architecture
3. **Task Creation**: Break down implementation into specific, actionable tasks
4. **Resource Planning**: Allocate team members and timeline
5. **Implementation**: Execute phases in sequence with testing at each stage

The design is ready for review and approval before proceeding to task creation.
