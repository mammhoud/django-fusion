# Django RSeal - Organized Structure

## Overview
Django RSeal is organized into logical modules by use case and functionality. Each module contains related features and services.

## Directory Organization

### Core Modules

#### `/core` - Core Configuration
- `apps.py` - Django app configuration
- `conf.py` - Core settings and configuration

#### `/models` - Data Models
Organized by domain:
- `default.py` - Base model classes
- `cache.py` - Caching mixins
- `tags.py` - Tagging system
- `banner.py` - Banner announcements
- `certification.py` - Certification templates
- `coupon.py` - Coupon management
- `workspace.py` - Workspace configuration

**Subdirectories:**
- `/users` - User profiles, teams, roles
- `/settings` - Global and brand settings, email templates
- `/newsletter` - Newsletter models
- `/contacts` - Contact management
- `/locations` - Branch and location models
- `/enums` - Status and activity type enumerations
- `/tasks` - Background task models

#### `/services` - Business Logic Services
Organized by domain:
- `README.md` - Service documentation

**Subdirectories:**
- `/commerce` - Payment processing, cart management
- `/communication` - Messaging, notifications
- `/content` - Search, content management
- `/email` - Email services and templates
- `/infrastructure` - Jobs, base services, registries

#### `/site` - Web Views & Handlers
- `__init__.py` - View exports
- `mixins.py` - View mixins
- `notifications.py` - Notification views
- `payments.py` - Payment views
- `search.py` - Search views
- `tags.py` - Tag views

**Subdirectories:**
- `/auth` - Authentication views and mixins
- `/views` - Additional view handlers

#### `/email` - Email Management
- `apps.py` - Email app configuration
- `README.md` - Email documentation

**Subdirectories:**
- `/models` - Email template models
- `/services` - Email sending services
- `/processing` - Email processing logic
- `/management` - Management commands
- `/templates` - Email templates

#### `/forms` - Django Forms
- `admin.py` - Admin forms
- `group.py` - Group forms
- `README.md` - Forms documentation

**Subdirectories:**
- `/authentication` - Login, registration forms
- `/newsletter` - Newsletter subscription forms

#### `/blocks` - Wagtail StreamField Blocks
- `base.py` - Base block classes
- `blocks.py` - Block definitions
- `mixins.py` - Block mixins
- `stream_blocks.py` - Stream block configurations
- `README.md` - Blocks documentation

**Subdirectories:**
- `/contact` - Contact form blocks
- `/content` - Content blocks
- `/media` - Media blocks
- `/pages` - Page blocks
- `/partials` - Partial blocks
- `/profile` - Profile blocks

#### `/snippets` - Wagtail Snippets
- `base.py` - Base snippet viewsets
- `banner.py` - Banner snippets
- `certification.py` - Certification snippets
- `coupon.py` - Coupon snippets
- `tags.py` - Tag snippets
- `README.md` - Snippets documentation

**Subdirectories:**
- `/manage` - Management snippets (people, teams, branches)
- `/site` - Site configuration snippets (email, media, social)
- `/newsletter` - Newsletter snippets
- `/tasks` - Task snippets

#### `/handlers` - Event Handlers & Hooks
- `filters_revision.py` - Revision filters
- `snippets_base.py` - Snippet base handlers
- `wagtail_hooks.py` - Wagtail hooks
- `README.md` - Handlers documentation

**Subdirectories:**
- `/models` - Model-specific handlers

#### `/signals` - Django Signals
- `binding.py` - Signal binding
- `handlers.py` - Signal handlers
- `invitations.py` - Invitation signals
- `notification.py` - Notification signals
- `utils.py` - Signal utilities
- `README.md` - Signals documentation

#### `/tasks` - Async Task Management
- `celery.py` - Celery task configuration
- `django_q.py` - Django-Q task configuration
- `README.md` - Tasks documentation

#### `/chat` - Chat Module
- `admin.py` - Chat admin
- `apps.py` - Chat app configuration
- `backends.py` - Chat backends
- `models.py` - Chat models
- `urls.py` - Chat URLs
- `views.py` - Chat views

**Subdirectories:**
- `/migrations` - Database migrations

#### `/newsletter` - Newsletter Management
- `designer.py` - Newsletter designer
- `enhancer.py` - Newsletter enhancer
- `subscription.py` - Subscription management
- `urls.py` - Newsletter URLs

#### `/workflows` - Workflow Orchestration
- `orchestrator.py` - Workflow orchestrator
- `README.md` - Workflows documentation

**Subdirectories:**
- `/orchestrator` - Orchestrator implementations

#### `/routing` - URL Routing
- `urls.py` - URL patterns

#### `/contrib` - Contributed Features
- `README.md` - Contrib documentation

**Subdirectories:**
- `/admin` - Admin customizations
- `/cache` - Caching utilities
- `/core` - Core utilities
- `/debug_tools` - Debug tools
- `/email` - Email utilities
- `/email_config` - Email configuration
- `/privacy` - Privacy utilities
- `/signals` - Signal utilities
- `/snippets` - Snippet utilities

#### `/adapters` - External Adapters
- `social.py` - Social media adapters

**Subdirectories:**
- `/adapters` - Adapter implementations

#### `/middlewares` - Django Middlewares
- `privacy_consent.py` - Privacy consent middleware

#### `/management` - Management Commands
- `README.md` - Management commands documentation

**Subdirectories:**
- `/commands` - Custom management commands

#### `/mcp_designer` - MCP Designer
- `apps.py` - MCP app configuration
- `mcp_server.py` - MCP server
- `signals.py` - MCP signals
- `utils.py` - MCP utilities
- `README.md` - MCP documentation

**Subdirectories:**
- `/management` - MCP management commands

#### `/templatetags` - Django Template Tags
- `apps.py` - Template tags app
- `rseal_chat.py` - Chat template tags

**Subdirectories:**
- `/components` - Component template tags

#### `/scripts` - Utility Scripts
- `superuser.py` - Superuser creation script
- `README.md` - Scripts documentation

#### `/migrations` - Database Migrations
- `README.md` - Migrations documentation

#### `/exceptions` - Custom Exceptions
- `RSealException` - Base exception
- `EmailSendError` - Email sending errors
- `TemplateNotFoundError` - Template not found
- `WorkflowError` - Workflow errors
- `AIIntegrationError` - AI integration errors
- `TaskExecutionError` - Task execution errors

### Root Files

- `__init__.py` - Package initialization
- `apps.py` - Django app configuration
- `conf.py` - Configuration
- `exceptions.py` - Custom exceptions
- `urls.py` - Main URL configuration
- `user_signals.py` - User signal handlers
- `wagtail_hooks.py` - Wagtail hooks
- `README.md` - Package documentation

## Import Patterns

### Canonical Imports

```python
# Models
from django_rseal.models import Person, DefaultBase, BaseTag
from django_rseal.models.users import Team, Role
from django_rseal.models.settings import EmailTemplate, Newsletter

# Services
from django_rseal.services.commerce import StripeGateway, PayPalGateway
from django_rseal.services.email import EmailService
from django_rseal.services.infrastructure import BaseService, TokenService

# Views & Site
from django_rseal.site import LoginView, RegisterView
from django_rseal.site.auth import PrivacyModalView
from django_rseal.site.views import NotificationView

# Forms
from django_rseal.forms.authentication import LoginForm, RegisterForm

# Blocks & Snippets
from django_rseal.blocks import BaseStreamBlock
from django_rseal.snippets import BaseSnippetViewSet

# Exceptions
from django_rseal.exceptions import EmailSendError, WorkflowError

# Signals
from django_rseal.signals import bind_custom_metadata
```

## Module Dependencies

```
core/
  └─ Configuration & settings

models/
  ├─ Depends on: core/
  └─ Used by: services/, site/, handlers/

services/
  ├─ Depends on: models/, core/
  └─ Used by: site/, handlers/, tasks/

site/
  ├─ Depends on: models/, services/, forms/
  └─ Used by: urls.py, routing/

forms/
  ├─ Depends on: models/
  └─ Used by: site/, handlers/

blocks/ & snippets/
  ├─ Depends on: models/, forms/
  └─ Used by: handlers/, wagtail_hooks.py

handlers/
  ├─ Depends on: models/, services/, blocks/, snippets/
  └─ Used by: wagtail_hooks.py

signals/
  ├─ Depends on: models/, services/
  └─ Used by: apps.py, user_signals.py

tasks/
  ├─ Depends on: models/, services/
  └─ Used by: services/, handlers/

chat/
  ├─ Depends on: models/, services/
  └─ Standalone module

newsletter/
  ├─ Depends on: models/, services/, email/
  └─ Standalone module

workflows/
  ├─ Depends on: models/, services/
  └─ Standalone module

contrib/
  ├─ Depends on: models/, services/
  └─ Optional utilities

email/
  ├─ Depends on: models/, services/
  └─ Used by: services/, handlers/
```

## Adding New Features

When adding new features:

1. **Determine the domain** (e.g., commerce, communication, content)
2. **Add models** to `/models/{domain}/` if needed
3. **Add services** to `/services/{domain}/` for business logic
4. **Add views** to `/site/` or `/site/{domain}/` for web handlers
5. **Add forms** to `/forms/{domain}/` if needed
6. **Add blocks/snippets** to `/blocks/{domain}/` or `/snippets/{domain}/`
7. **Add signals** to `/signals/` if needed
8. **Add management commands** to `/management/commands/` if needed

## Backward Compatibility

As of version 1.0, backward compatibility with `django_rseal.pipelines` has been removed.
All imports should use the canonical paths documented above.

Migration guide:
- `django_rseal.pipelines.models` → `django_rseal.models`
- `django_rseal.pipelines.services` → `django_rseal.services`
- `django_rseal.pipelines.site` → `django_rseal.site`
- `django_rseal.pipelines.forms` → `django_rseal.forms`
