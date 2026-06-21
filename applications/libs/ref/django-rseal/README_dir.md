# django-rseal

Automation layer — pipelines, services, workflows, email, signals, admin, cache, commands.

## Installation

```bash
uv add django-rseal
# or
pip install django-rseal
```

## Directory Tree

```
django-rseal/
├── src/
│   └── django_rseal/
│       ├── ai/              # AI adapter
│       ├── chat/            # Chat app (models, views, urls)
│       ├── comp/            # Wagtail StreamField blocks
│       │   └── blocks/
│       ├── contrib/         # Admin, cache, signals, snippets
│       │   ├── admin_site/
│       │   ├── cache/
│       │   ├── debug_tools/
│       │   ├── email_config/
│       │   ├── privacy/
│       │   └── signals/
│       ├── email/           # Email models, registry, selectors
│       ├── email_tools/     # CSV manager, extractor, sender
│       ├── handlers/        # Wagtail hooks & snippet handlers
│       ├── management/      # Management commands
│       ├── mcp_designer/    # MCP server designer
│       ├── migrations/      # Database migrations
│       ├── newsletter/      # Newsletter designer & enhancer
│       ├── pipelines/       # Core automation pipelines
│       │   ├── backends/
│       │   ├── filters/
│       │   ├── forms/
│       │   ├── managers/
│       │   ├── mixins/
│       │   ├── models/
│       │   ├── routes/
│       │   ├── services/
│       │   ├── signals/
│       │   ├── site/
│       │   ├── snippets/
│       │   └── utils/
│       ├── routes/          # URL routing helpers
│       ├── scripts/         # Utility scripts (superuser etc.)
│       ├── seeder/          # Database seeding
│       ├── services/        # CSV, email, queue, invitation, report
│       ├── tasks/           # Celery & Django-Q task definitions
│       ├── templates/       # HTML templates
│       ├── workflows/       # Workflow orchestration
│       ├── __init__.py
│       ├── exceptions.py
│       ├── models.py
│       └── py.typed
├── tests/
│   ├── email/
│   ├── integration/
│   └── unit/
├── media/
│   └── email_templates/
├── assets/
│   └── cover.png
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## Usage

```python
# Thin subclass pattern — inject your project models
from django_rseal.pipelines.services.cart import CartServiceBase
from myapp.models import Cart, CartItem

class CartService(CartServiceBase):
    cart_model = Cart
    cart_item_model = CartItem

# Email service
from django_rseal.services import EmailService
EmailService.send(template="welcome", to="user@example.com", context={})

# Queue manager
from django_rseal.services import EmailQueueManager
queue = EmailQueueManager()
queue.enqueue(email_id=42)

# Celery tasks
from django_rseal.tasks.celery import send_email_task
send_email_task.delay(email_id=42)

# INSTALLED_APPS
INSTALLED_APPS = [
    "django_rseal.pipelines",
    "django_rseal.chat",
    "django_rseal.email_tools",
    "django_rseal.newsletter",
    "django_rseal.tasks",
    "django_rseal.seeder",
    "django_rseal.ai",
]
```

## Related Packages

- [django-grep](../django-grep/) — Testing framework
- [django-osoul](../django-osoul/) — Pure Django foundation
- [nawaai](../nawaai/) — AI/MCP toolkit
