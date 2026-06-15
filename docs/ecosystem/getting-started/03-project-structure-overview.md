# Project Structure Overview

## Directory Structure

```
xellent/
├── docs/                          # Documentation
│   ├── getting-started/          # Getting started guides
│   ├── architecture/             # Architecture documentation
│   ├── api/                      # API documentation
│   ├── deployment/               # Deployment guides
│   ├── libraries/                # Dependencies documentation
│   ├── development/              # Development guides
│   ├── troubleshooting/          # Troubleshooting guides
│   ├── lms/                      # LMS module docs
│   ├── blog/                     # Blog module docs
│   ├── _sidebar.md               # Documentation navigation
│   └── index.html                # Documentation home
│
├── compose/                       # Docker Compose configuration
│   ├── nginx/                    # Nginx reverse proxy
│   ├── postgres/                 # PostgreSQL database
│   ├── traefik/                  # Traefik reverse proxy
│   └── lms/                      # LMS service
│
├── src/                          # Main application source code
│   ├── manage.py                 # Django management script
│   ├── settings.py               # Django settings
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI application
│   │
│   ├── apps/                     # Django applications
│   │   ├── users/               # User management
│   │   ├── courses/             # Course management
│   │   ├── lms/                 # Learning management
│   │   ├── blog/                # Blog functionality
│   │   └── api/                 # API endpoints
│   │
│   ├── templates/               # Django templates
│   │   ├── base.html            # Base template
│   │   ├── home.html            # Home page
│   │   └── ...
│   │
│   ├── static/                  # Static files
│   │   ├── css/                 # Stylesheets
│   │   ├── js/                  # JavaScript
│   │   └── images/              # Images
│   │
│   └── utils/                   # Utility functions
│       ├── decorators.py        # Custom decorators
│       ├── helpers.py           # Helper functions
│       └── validators.py        # Validators
│
├── frontend/                     # Frontend assets
│   ├── src/                     # Source files
│   │   ├── css/                 # Tailwind CSS
│   │   ├── js/                  # JavaScript
│   │   └── components/          # Reusable components
│   ├── dist/                    # Built files
│   ├── package.json             # NPM configuration
│   └── webpack.config.js        # Webpack configuration
│
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   ├── e2e/                     # End-to-end tests
│   ├── fixtures/                # Test fixtures
│   └── conftest.py              # Pytest configuration
│
├── config/                       # Configuration files
│   ├── settings/                # Django settings modules
│   │   ├── base.py              # Base settings
│   │   ├── development.py       # Development settings
│   │   ├── production.py        # Production settings
│   │   └── testing.py           # Testing settings
│   └── env.example              # Example environment file
│
├── scripts/                      # Utility scripts
│   ├── setup.sh                 # Setup script
│   ├── migrate.sh               # Migration script
│   └── deploy.sh                # Deployment script
│
├── .github/                      # GitHub configuration
│   ├── workflows/               # CI/CD workflows
│   └── ISSUE_TEMPLATE/          # Issue templates
│
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker image definition
├── Makefile                     # Make commands
├── requirements.txt             # Python dependencies
├── package.json                 # NPM dependencies
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── README.md                    # Project README
└── LICENSE.md                   # License file
```

## Key Directories

### `/docs`

Contains all project documentation organized by topic:

- **getting-started/**: Installation and setup guides
- **architecture/**: System design and architecture
- **api/**: API documentation and endpoints
- **deployment/**: Docker and deployment guides
- **libraries/**: Dependencies and library documentation
- **development/**: Development guides and best practices
- **troubleshooting/**: Common issues and solutions
- **lms/**: LMS module documentation
- **blog/**: Blog module documentation

### `/src`

Main application source code:

- **apps/**: Django applications (users, courses, lms, blog, api)
- **templates/**: HTML templates for rendering
- **static/**: CSS, JavaScript, and image files
- **utils/**: Utility functions and helpers

### `/frontend`

Frontend build system and assets:

- **src/**: Source CSS and JavaScript
- **dist/**: Built and minified files
- **package.json**: NPM dependencies and scripts

### `/tests`

Test suite organized by type:

- **unit/**: Unit tests for individual functions
- **integration/**: Integration tests for components
- **e2e/**: End-to-end tests for user workflows
- **fixtures/**: Test data and fixtures

### `/compose`

Docker Compose service configurations:

- **nginx/**: Reverse proxy configuration
- **postgres/**: Database configuration
- **traefik/**: Traefik reverse proxy
- **lms/**: LMS service configuration

## Application Structure

### Django Apps

Each Django app follows this structure:

```
apps/users/
├── __init__.py
├── admin.py              # Admin interface
├── apps.py               # App configuration
├── models.py             # Database models
├── views.py              # View functions
├── urls.py               # URL routing
├── serializers.py        # DRF serializers
├── forms.py              # Django forms
├── tests.py              # Tests
├── migrations/           # Database migrations
└── templates/            # App templates
```

### API Structure

```
apps/api/
├── __init__.py
├── views.py              # API viewsets
├── serializers.py        # API serializers
├── urls.py               # API routing
├── permissions.py        # Custom permissions
├── pagination.py         # Pagination classes
├── filters.py            # Filter classes
└── tests.py              # API tests
```

## Configuration Files

### Django Settings

Settings are organized by environment:

- **base.py**: Common settings
- **development.py**: Development-specific settings
- **production.py**: Production-specific settings
- **testing.py**: Testing-specific settings

### Environment Variables

Configuration via `.env` file:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host/db
REDIS_URL=redis://localhost:6379/0
```

## Build and Deployment

### Docker

- **Dockerfile**: Main application image
- **docker-compose.yml**: Multi-container setup

### Make Commands

```bash
make help              # Show all commands
make dev              # Start development server
make test             # Run tests
make format           # Format code
make lint             # Run linting
```

## Static Files

### CSS

- **Tailwind CSS**: Utility-first CSS framework
- **PostCSS**: CSS processing
- **PurgeCSS**: Remove unused CSS in production

### JavaScript

- **Alpine.js**: Lightweight JavaScript framework
- **HTMX**: HTML over the wire
- **Webpack**: Module bundler

### Images

- **Static images**: `/src/static/images/`
- **Media uploads**: `/media/` (user-uploaded files)

## Testing Structure

### Unit Tests

```
tests/unit/
├── test_models.py
├── test_views.py
├── test_serializers.py
└── test_forms.py
```

### Integration Tests

```
tests/integration/
├── test_api_endpoints.py
├── test_workflows.py
└── test_database.py
```

### End-to-End Tests

```
tests/e2e/
├── test_user_registration.py
├── test_course_enrollment.py
└── test_quiz_submission.py
```

## Important Files

### Root Level

- **manage.py**: Django management script
- **docker-compose.yml**: Container orchestration
- **Makefile**: Development commands
- **requirements.txt**: Python dependencies
- **package.json**: NPM dependencies
- **.env.example**: Environment template

### Configuration

- **settings.py**: Django settings
- **urls.py**: URL routing
- **wsgi.py**: WSGI application

## Naming Conventions

### Python Files

- **models.py**: Database models
- **views.py**: View functions/classes
- **urls.py**: URL routing
- **forms.py**: Django forms
- **serializers.py**: DRF serializers
- **tests.py**: Test cases
- **admin.py**: Admin interface

### Templates

- **base.html**: Base template
- **{app_name}/{model_name}_list.html**: List view
- **{app_name}/{model_name}_detail.html**: Detail view
- **{app_name}/{model_name}_form.html**: Form view

### CSS/JavaScript

- **main.css**: Main stylesheet
- **main.js**: Main JavaScript file
- **components/**: Reusable components

## Related Documentation

- [Installation Guide](01-installation-guide.md)
- [Local Development Setup](02-local-development-setup.md)
- [Development Workflow](../development/01-development-workflow.md)
- [Architecture Overview](../architecture/01-system-architecture-overview.md)
