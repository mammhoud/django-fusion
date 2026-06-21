# django-osoul

Pure Django foundation layer — models, managers, mixins, utils, comp, contrib, middlewares, filters, backends, adapters, services.

## Installation

```bash
uv add django-osoul
# or
pip install django-osoul
```

## Directory Tree

```
django-osoul/
├── src/
│   └── django_osoul/
│       ├── backends/        # Auth backends
│       ├── CI/              # CI model helpers
│       ├── comp/            # UI components & templatetags
│       │   ├── adapters/
│       │   ├── management/
│       │   ├── plugins/
│       │   ├── site/
│       │   └── templatetags/
│       ├── contrib/         # Contrib utilities
│       │   ├── choices/
│       │   ├── context/
│       │   ├── enums/
│       │   ├── responses/
│       │   └── schemas/
│       ├── domain/          # Domain entities & value objects
│       ├── filters/         # Form validators & token filters
│       ├── handlers/        # Request handlers
│       ├── managers/        # Custom ORM managers
│       ├── middlewares/     # Django middlewares
│       ├── mixins/          # Model & view mixins
│       ├── models/          # Foundation models
│       ├── services/        # Business logic services
│       ├── templatetags/    # Custom template tags
│       ├── utils/           # Utility functions
│       ├── views/           # View mixins
│       ├── __init__.py
│       ├── conf.py
│       ├── enums.py
│       ├── exceptions.py
│       └── py.typed
├── assets/
│   └── cover.png
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
```

## Usage

```python
# Models
from django_osoul.models import BaseModel, TimeStampedModel, SoftDeleteMixin

class MyModel(TimeStampedModel, SoftDeleteMixin, BaseModel):
    name = models.CharField(max_length=255)

# Managers
from django_osoul.managers import BaseManager, UserManager

# Mixins
from django_osoul.mixins import CacheMixin, SearchMixin

# Utils
from django_osoul.utils import datetime_utils, text, validators

# Middleware — add to MIDDLEWARE in settings.py
# "django_osoul.middlewares.language.LanguageMiddleware"
# "django_osoul.middlewares.site.SiteMiddleware"

# Template tags
# {% load django_osoul_tags %}
```

## Related Packages

- [django-grep](../django-grep/) — Testing framework
- [django-rseal](../django-rseal/) — Automation layer
- [nawaai](../nawaai/) — AI/MCP toolkit
