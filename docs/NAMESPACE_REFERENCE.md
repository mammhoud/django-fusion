# Django-Fusion Namespace Reference

Complete guide to all canonical import paths and module namespaces in django-fusion.

## Package Structure

```
django_fusion/
├── analyzer/              # Template scanning and component analysis
├── comp/                  # Component system (core)
│   ├── cache/            # Component mapping cache
│   ├── routes/           # Routing system (RoutableComponent, Site, etc.)
│   ├── generic/          # Generic class-based views
│   ├── configuration/    # Component manifest & config
│   ├── core/             # Component bootstrap
│   ├── forms/            # Form layout helpers
│   ├── loaders/          # Lazy/HTMX loaders
│   ├── payloads/         # JSON payload service
│   ├── plugins/          # Pluggy hook system
│   ├── static/           # Static file discovery
│   ├── templates/        # Template rendering
│   └── templatetags/     # Django template tags
├── config/                # Configuration
│   └── dynaconf_loader/  # Multi-environment config
├── contrib/               # Shared utilities
│   ├── admin/            # Admin customization
│   ├── cache/            # Cache utilities
│   ├── debug_tools/      # Development tools
│   ├── email_config/     # Email configuration
│   └── privacy/          # Privacy & consent
├── core/                  # Foundational layer
│   ├── cache/            # Cache manager base
│   ├── filters/          # Queryset filters
│   ├── handlers/         # View handlers
│   ├── managers/         # Model managers
│   ├── middlewares/      # Middleware
│   ├── models/           # Base models
│   ├── services/         # Service layer
│   └── utils/            # Utilities
├── health/                # Health check endpoint
├── infrastructure/        # Locale, scripts, tags
├── site/                  # Site layer
│   ├── adapters/         # Auth adapters
│   ├── auth/             # Auth models & forms
│   ├── choices/          # Choice enums
│   ├── context/          # Context processors
│   ├── enums/            # Enums
│   ├── responses/        # HTTP responses
│   ├── schemas/          # Pydantic schemas
│   └── views/            # Site views
├── wagtail/               # Wagtail integration
├── web/                   # Web layer
│   ├── adapters/         # django-allauth adapters
│   ├── backends/         # Auth backends
│   └── views/            # View mixins
└── __init__.py            # Main package exports
```

## Canonical Import Paths

### Routing & Components

```python
# Main routing classes
from django_fusion.comp.routes import (
    Viewset,                    # Base viewset class
    BaseViewset,                # Abstract viewset
    ViewsetMeta,               # Viewset metaclass
    Route,                      # Route descriptor
    route,                      # Route decorator
    menu_path,                  # Menu path helper
    IndexViewMixin,             # Index view mixin
    viewprop,                   # View property descriptor
)

# Site and application
from django_fusion.comp.routes import (
    Site,                       # Top-level site container
    Application,                # Feature grouping
    AppMenuMixin,              # App menu support
)

# Routable components
from django_fusion.comp.routes import (
    RoutableComponent,          # Full page component
    FragmentComponent,          # HTMX fragment component
)

# Model viewsets
from django_fusion.comp.routes import (
    BaseModelViewset,           # Base model viewset
    ModelViewset,              # Full CRUD viewset
    ReadonlyModelViewset,      # Read-only viewset
    ListBulkActionsMixin,      # Bulk actions
    CreateViewMixin,           # Create support
    UpdateViewMixin,           # Update support
    DeleteViewMixin,           # Delete support
    DetailViewMixin,           # Detail view
)

# Fragment detection
from django_fusion.comp.routes import (
    FragmentDetector,           # Fragment detection
    FragmentDetectionMixin,    # Fragment detection mixin
    detect_fragment_strategy,   # Strategy detection
    add_fragment_detection_to_request,  # Add to request
)

# Forms and tables
from django_fusion.comp.routes import (
    FormMixin,                 # Form rendering mixin
    TableMixin,                # Table rendering mixin
    FormTableMixin,            # Combined form+table
    TemplateResolverMixin,     # Template resolution
)
```

### Generic Class-Based Views

```python
from django_fusion.comp.generic import (
    # CRUD views
    ListModelView,             # List/table view
    CreateModelView,           # Create/form view
    DetailModelView,           # Detail view
    UpdateModelView,           # Update/form view
    DeleteModelView,           # Delete view
    
    # Base views
    BaseListModelView,         # Base list view
    BaseBulkActionView,        # Base bulk actions
    
    # Specialized
    TableView,                 # Table rendering view
    SearchableViewMixin,       # Search mixin
    
    # Actions
    Action,                    # Action descriptor
    DeleteBulkActionView,      # Bulk delete
)
```

### Component Cache

```python
from django_fusion.comp.cache import (
    get_component_map_cache,   # Get component map cache
    ComponentMapCache,         # Cache class
)
```

### Component Analyzer

```python
from django_fusion.analyzer import (
    scanner,                   # Template scanner module
    parser,                    # Component parser module
)

from django_fusion.analyzer.scanner import (
    scan,                      # Scan templates
    ScannedFile,              # Scanned template file
)

from django_fusion.analyzer.parser import (
    ParsedTemplate,           # Parsed template
    CompUsage,                # Component usage
    SectionMarker,            # Section marker
    parse_kwargs,             # Parse attributes
)

from django_fusion.analyzer.schemas import (
    Prop,                     # Component property
    Slot,                     # Template slot
)

from django_fusion.analyzer.views import (
    AnalysisView,             # Analysis view
)
```

### Core Layer

```python
# Handlers
from django_fusion.core.handlers import (
    PageHandler,              # Base page handler
)

# Managers
from django_fusion.core.managers import (
    BaseManager,              # Base manager
)

# Models
from django_fusion.core.models import (
    BaseModel,                # Base model
    TimeStampedModel,         # Timestamped model
    UUIDModel,                # UUID model
)

# Services
from django_fusion.core.services import (
    Service,                  # Base service
    CRUDService,              # CRUD service
)

# Cache utilities
from django_fusion.core.cache import (
    get_cache,               # Get cache
    cache_key,               # Cache key builder
    CacheManager,            # Cache manager
)

# Middlewares
from django_fusion.core.middlewares import (
    FusionMiddleware,        # Main middleware
    SiteMiddleware,          # Site middleware
    LanguageMiddleware,      # Language middleware
)

# Utilities
from django_fusion.core.utils import (
    DataUtils,               # Data utilities
    FormattingUtils,         # Formatting utilities
    SecurityUtils,           # Security utilities
)
```

### Web Layer

```python
# View mixins
from django_fusion.web.views import (
    FilterMixin,             # Query filtering
    SearchMixin,             # Search functionality
)

# Auth backends
from django_fusion.web.backends import (
    CustomBackend,           # Custom authentication
)

# Allauth adapters
from django_fusion.web.adapters import (
    AccountAdapter,          # Account adapter
    SocialAdapter,           # Social adapter
)
```

### Site Layer

```python
# Auth
from django_fusion.site.auth import (
    AuthForm,                # Auth form base
    LoginForm,               # Login form
)

# Auth adapters
from django_fusion.site.adapters import (
    RegistrationAdapter,     # Registration adapter
)

# Choices
from django_fusion.site.choices import (
    CartStatus,              # Cart choices
    ContactType,             # Contact choices
    MessageStatus,           # Message choices
)

# Context processors
from django_fusion.site.context import (
    auth_context,            # Auth context processor
    cookies_context,         # Cookies context processor
    htmx_context,            # HTMX context processor
)

# Schemas
from django_fusion.site.schemas import (
    UserSchema,              # User schema
    ResponseSchema,          # Response schema
)

# Views
from django_fusion.site.views import (
    NotificationView,        # Notifications view
    TagManagementView,       # Tag management
)
```

### Configuration

```python
# Dynaconf configuration
from django_fusion.config.dynaconf_loader import (
    DynaconfSettings,        # Dynaconf settings loader
    get_config,              # Get configuration
)

# Package configuration
from django_fusion.config import (
    get_setting,             # Get setting
    SETTINGS,                # Settings object
)
```

### Health Checks

```python
from django_fusion.health import (
    HealthCheckView,         # Main health check
    DatabaseHealthView,      # Database health
    AssetsHealthView,        # Assets health
    CacheHealthView,         # Cache health
)
```

### Wagtail Integration

```python
from django_fusion.wagtail import (
    WagtailBlock,           # Base block
    WagtailSnippet,         # Snippet support
)
```

## Migration Guide: Old → New Namespaces

### Routing Imports

**Old (Deprecated):**
```python
from django_fusion.site.routes import Viewset
from django_fusion import RoutableComponent
```

**New (Current):**
```python
from django_fusion.comp.routes import Viewset, RoutableComponent
```

### Generic CBV Imports

**Old (Deprecated):**
```python
from django_fusion.site.generic import ListModelView
```

**New (Current):**
```python
from django_fusion.comp.generic import ListModelView
```

### Handler Imports

**Old (Deprecated):**
```python
from django_fusion.site import PageHandler
```

**New (Current):**
```python
from django_fusion.core.handlers import PageHandler
```

### View Mixin Imports

**Old (Deprecated):**
```python
from django_fusion.web import FilterMixin
```

**New (Current):**
```python
from django_fusion.web.views import FilterMixin
```

## Complete Example

### Old Code (Deprecated)

```python
from django_fusion.site.routes import RoutableComponent, Site, Application
from django_fusion.site.generic import ListModelView
from django_fusion import PageHandler
from django_fusion.web import FilterMixin

class BlogListComponent(FilterMixin, ListModelView, RoutableComponent):
    route_path = "blog/"
    model = Blog
```

### New Code (Current)

```python
from django_fusion.comp.routes import RoutableComponent, Site, Application
from django_fusion.comp.generic import ListModelView
from django_fusion.core.handlers import PageHandler
from django_fusion.web.views import FilterMixin

class BlogListComponent(FilterMixin, ListModelView, RoutableComponent):
    route_path = "blog/"
    model = Blog
```

## Namespace Rules

### 1. Use Canonical Paths

Always use the canonical import paths listed in this document.

```python
# ✅ Correct
from django_fusion.comp.routes import RoutableComponent

# ❌ Wrong
from django_fusion.comp.routes.components import RoutableComponent
from django_fusion import RoutableComponent
```

### 2. Group Related Imports

Import related items in one statement.

```python
# ✅ Good
from django_fusion.comp.routes import (
    RoutableComponent,
    FragmentComponent,
    FormMixin,
    TableMixin,
)

# ❌ Avoid
from django_fusion.comp.routes import RoutableComponent
from django_fusion.comp.routes import FragmentComponent
from django_fusion.comp.routes import FormMixin
```

### 3. Avoid Circular Imports

Import from specific modules, not parent packages.

```python
# ✅ Correct
from django_fusion.comp.routes import Site
from django_fusion.core.handlers import PageHandler

# ⚠️ May cause circular imports
from django_fusion import Site
from django_fusion import PageHandler
```

## Backward Compatibility

### Legacy Imports

Deprecated imports that still work (but will be removed):

```python
# Deprecated but still functional
from django_fusion import RoutableComponent  # Use: from django_fusion.comp.routes
from django_fusion.site.routes import Viewset  # Use: from django_fusion.comp.routes
from django_fusion.site.generic import ListModelView  # Use: from django_fusion.comp.generic
```

### Deprecation Timeline

- **Now**: Canonical paths are preferred
- **v1.0**: Deprecated paths show warnings
- **v2.0+**: Deprecated paths will be removed

### Update Your Code

Search and replace patterns:

| Old Pattern | New Pattern |
|-------------|-------------|
| `from django_fusion.site.routes import` | `from django_fusion.comp.routes import` |
| `from django_fusion.site.generic import` | `from django_fusion.comp.generic import` |
| `from django_fusion import PageHandler` | `from django_fusion.core.handlers import PageHandler` |
| `from django_fusion.web import FilterMixin` | `from django_fusion.web.views import FilterMixin` |

## Common Issues

### Issue 1: ModuleNotFoundError

**Error:**
```
ModuleNotFoundError: No module named 'django_fusion.site.routes'
```

**Solution:**
```python
# Change from:
from django_fusion.site.routes import RoutableComponent

# Change to:
from django_fusion.comp.routes import RoutableComponent
```

### Issue 2: ImportError

**Error:**
```
ImportError: cannot import name 'ListModelView' from 'django_fusion.site'
```

**Solution:**
```python
# Change from:
from django_fusion.site import ListModelView

# Change to:
from django_fusion.comp.generic import ListModelView
```

### Issue 3: Circular Import

**Error:**
```
ImportError: cannot import name due to circular imports
```

**Solution:**
Use specific module paths instead of package-level imports:

```python
# ✅ Use specific paths
from django_fusion.comp.routes import Site
from django_fusion.core.handlers import PageHandler

# ❌ Don't use package-level imports
from django_fusion import Site, PageHandler
```

## Testing Import Paths

Verify your imports are correct:

```python
# Test script
try:
    from django_fusion.comp.routes import RoutableComponent
    print("✅ RoutableComponent imported successfully")
except ImportError as e:
    print(f"❌ Failed to import: {e}")

try:
    from django_fusion.comp.generic import ListModelView
    print("✅ ListModelView imported successfully")
except ImportError as e:
    print(f"❌ Failed to import: {e}")

try:
    from django_fusion.analyzer import scanner, parser
    print("✅ Analyzer imported successfully")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
```

## Related Documentation

- [API_REFERENCE.md](./API_REFERENCE.md) - Complete API reference
- [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) - Component types
- [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) - Routing system
- [ANALYZER_MODULE.md](./ANALYZER_MODULE.md) - Analyzer module

---

**Status**: Current as of django-fusion v2.0+

**Last Updated**: July 2024

