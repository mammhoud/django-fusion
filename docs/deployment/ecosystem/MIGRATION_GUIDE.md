# Migration Guide

This guide documents all import path changes, app renames, deprecated APIs, and troubleshooting tips resulting from the ecosystem-wide architectural refactoring.

---

## App Renames

All app renames preserve existing database table names via `AlterModelTable` migrations and `ContentType` data migrations. This ensures zero data loss and maintains foreign key relationships.

### App Rename Table

| Old App | New App | AppConfig Label | Both Projects | Database Tables Preserved |
|---------|---------|-----------------|---------------|---------------------------|
| `apps/handlers/` | `apps/accounts/` | `accounts` | Yes | `handlers_person`, `handlers_certificate`, `handlers_message`, etc. |
| `apps/LMS/` | `apps/lms/` | `lms` (ctc-research.com) / `alliance` (structa.cloud) | Yes | `lms_cart`, `lms_enrollment`, `lms_progress`, etc. |
| `apps/pages/` | `apps/content/` | `content` | Yes | `pages_homepage`, `pages_blogpage`, `pages_contentpage`, etc. |

### Migration Strategy

Each app rename follows a three-step migration pattern:

1. **AlterModelTable Migration**: Preserves physical table names while changing the Django app label
2. **ContentType Data Migration**: Updates `django_content_type` records to maintain Django's internal model registry
3. **INSTALLED_APPS Update**: Updates project settings to use new app labels

#### 1. AlterModelTable Migration Example

```python
# accounts/migrations/0001_rename_app_label.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('handlers', '0001_initial'),  # Depends on last handlers migration
    ]

    operations = [
        migrations.AlterModelTable(
            name='person',
            table='handlers_person',  # Preserves original table name
        ),
        migrations.AlterModelTable(
            name='certificate',
            table='handlers_certificate',
        ),
        # ... repeat for all models in the app
    ]
```

#### 2. ContentType Data Migration Example

```python
# accounts/migrations/0002_update_contenttypes.py
from django.db import migrations

def update_contenttypes(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='handlers').update(app_label='accounts')

def reverse_update_contenttypes(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='accounts').update(app_label='handlers')

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_rename_app_label'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(update_contenttypes, reverse_update_contenttypes),
    ]
```

#### 3. INSTALLED_APPS Changes

**Before:**
```python
INSTALLED_APPS = [
    "apps.handlers",
    "apps.LMS",
    "apps.pages",
    ...
]
```

**After:**
```python
INSTALLED_APPS = [
    "apps.accounts",
    "apps.lms",          # ctc-research.com
    "apps.alliance",     # structa.cloud (LMS equivalent)
    "apps.content",
    ...
]
```

### Handling Existing Data and Foreign Keys

#### Foreign Key Preservation
Foreign keys referencing renamed apps continue to work because:
1. **Physical table names unchanged**: `AlterModelTable` preserves `handlers_person`, `lms_cart`, etc.
2. **ContentType records updated**: Django's internal model registry updated via data migration
3. **ForeignKey fields reference models by (app_label, model_name)**: Updated via ContentType migration

#### Data Integrity
No data migration required because:
- Table names remain identical (`handlers_person` → still `handlers_person`)
- Row data remains in same physical tables
- Only Django's app_label metadata changes

#### Reverse Foreign Keys
Existing reverse relationships (e.g., `Person.certificates`) continue to work because:
- Related names unchanged
- Database constraints unchanged
- Django ORM resolves using updated ContentType records

### Migration Safety and Reversibility

#### Safety Features
1. **Zero data loss**: Table names preserved, no data moved or deleted
2. **Atomic operations**: Each migration runs in a transaction
3. **Dependency ordering**: App rename migrations depend on final migration of original app
4. **Backup points**: Git tags created before each major phase (`rollback-phase-6-start`)

#### Reversibility Testing
All app rename migrations are tested for reversibility:

```bash
# Test migration reversal
python manage.py migrate accounts zero  # Reverts accounts rename
python manage.py migrate accounts       # Re-applies rename

# Verify data integrity after reversal
python manage.py check --deploy
python manage.py test accounts.tests
```

#### Rollback Procedure
If migration fails or needs reversal:

1. **Database rollback**:
   ```bash
   python manage.py migrate accounts zero
   python manage.py migrate lms zero
   python manage.py migrate content zero
   ```

2. **Settings rollback**: Revert INSTALLED_APPS to old app names
3. **Import rollback**: Revert code imports to old paths
4. **Git recovery**: Checkout `rollback-phase-6-start` tag

#### Verification Commands
After app rename migrations:

```bash
# Check migration state
python manage.py showmigrations

# Check ContentType records
python manage.py shell -c "
from django.contrib.contenttypes.models import ContentType
for ct in ContentType.objects.filter(app_label__in=['accounts', 'lms', 'alliance', 'content']):
    print(f'{ct.app_label}.{ct.model}')
"

# Verify table names
python manage.py dbshell -c "\dt handlers_*; \dt lms_*; \dt pages_*;"
```

### Cross-Project Consistency

#### Requirement 2: Domain-Driven Module Restructuring
App renames align with domain-driven architecture:
- `handlers` → `accounts`: User management, authentication, roles domain
- `LMS` → `lms`/`alliance`: Learning management system domain
- `pages` → `content`: CMS content management domain

#### Requirement 5: Cross-Project Consistency and Naming Unification
- **Consistent structure**: Both projects use `accounts/`, `content/`, and project-specific LMS (`lms`/`alliance`)
- **Unified naming**: Snake_case app directories (`lms` not `LMS`)
- **Standard patterns**: Same migration strategy for both projects

---

## Changed Import Paths

### Managers

| Before | After |
|--------|-------|
| `from apps.handlers.managers.role_hierarchy import RoleHierarchyManager` | `from django_fusion.core.managers import RoleHierarchyManager` |
| `from apps.handlers.managers.group_access import GroupAccessControl` | `from django_fusion.core.managers import GroupAccessControl` |
| `from apps.handlers.managers.user import UserManager` | `from django_fusion.core.managers import UserManager` |
| `from apps.handlers.managers.group import GroupManager` | `from django_fusion.core.managers import GroupManager` |
| `from apps.handlers.managers import RoleHierarchyManager` | `from django_fusion.core.managers import RoleHierarchyManager` |
| `from apps.handlers.managers import TokenCachedManager` | `from django_fusion.core.managers import TokenCachedManager` |
| `from apps.handlers.managers import BaseManager` | `from django_fusion.core.managers import BaseManager` |
| `from apps.handlers.managers import CachedManager` | `from django_fusion.core.managers import CachedManager` |
| `from apps.handlers.managers import PersonTagCategoryManager` | `from django_fusion.core.managers import PersonTagCategoryManager` |
| `from apps.handlers.managers import PersonTagManager` | `from django_fusion.core.managers import PersonTagManager` |

### Mixins

| Before | After |
|--------|-------|
| `from apps.handlers.mixins.user import UserMixin` | `from django_fusion.mixins import UserMixin` |
| `from apps.handlers.mixins.group import GroupMixin` | `from django_fusion.mixins import GroupMixin` |
| `from apps.handlers.mixins.views import ...` | `from django_fusion.mixins import ...` |
| `from apps.handlers.mixins.models import ...` | `from django_fusion.mixins import ...` |
| `from apps.handlers.mixins.service import ServiceMixin` | `from ceptor_ai.pipelines.mixins.service import ServiceMixin` |
| `from apps.handlers.mixins import CacheMixin` | `from django_fusion.mixins import CacheMixin` |
| `from apps.handlers.mixins import CacheSearchMixin` | `from django_fusion.mixins import CacheSearchMixin` |

### Middleware

| Before | After |
|--------|-------|
| `from apps.handlers.middleware.error_tracker import ErrorTrackerMiddleware` | `from django_fusion.middlewares.error_tracker import ErrorTrackerMiddleware` |
| `from apps.handlers.middleware import ErrorTrackerMiddleware` | `from django_fusion.middlewares import ErrorTrackerMiddleware` |
| `from apps.handlers.middleware.privacy import PrivacyConsentMiddleware` | `from ceptor_ai.contrib.privacy.middleware import PrivacyConsentMiddleware` |
| `from apps.handlers.middleware import SiteMiddleware` | `from django_fusion.middlewares import SiteMiddleware` |
| `from apps.handlers.middleware import ReadonlyExceptionHandlerMiddleware` | `from django_fusion.middlewares import ReadonlyExceptionHandlerMiddleware` |

### Backends

| Before | After |
|--------|-------|
| `from apps.handlers.backends.auth import ...` | `from django_fusion.backends.auth import ...` |
| `from apps.handlers.backends.storage import ...` | `from django_fusion.backends.storage import ...` |
| `from apps.handlers.backends.auth import EmailOrUsernameModelBackend` | `from django_fusion.backends.auth import EmailOrUsernameModelBackend` |

### Adapters

| Before | After |
|--------|-------|
| `from apps.handlers.adapters.allauth import ...` | `from django_fusion.adapters.allauth import ...` |
| `from apps.handlers.adapters.social import ...` | `from django_fusion.adapters.social import ...` |

### Services

| Before | After |
|--------|-------|
| `from apps.handlers.services.user import UserService` | `from django_fusion.core.services.user import UserService` |
| `from apps.handlers.services.group import GroupService` | `from django_fusion.core.services.group import GroupService` |
| `from apps.LMS.services.cart import CartService` | `from apps.lms.services.cart import CartService` (thin subclass of `ceptor_ai.pipelines.services.cart.CartServiceBase`) |
| `from apps.LMS.services.person import PersonService` | `from apps.lms.services.person import PersonService` (thin subclass of `ceptor_ai.pipelines.services.person.PersonServiceBase`) |
| `from apps.LMS.services.message import MessageService` | `from apps.lms.services.message import MessageService` (thin subclass of `ceptor_ai.pipelines.services.message.MessageServiceBase`) |
| `from apps.LMS.services.form_submission import FormSubmissionService` | `from apps.lms.services.form_submission import FormSubmissionService` (thin subclass of `ceptor_ai.pipelines.services.form_submission.FormSubmissionServiceBase`) |

### Handlers

| Before | After |
|--------|-------|
| `from apps.handlers.handlers.base import ...` | `from django_fusion.core.handlers.base import ...` |
| `from apps.handlers.handlers.core import ...` | `from django_fusion.core.handlers.core import ...` |
| `from apps.handlers.handlers.search import ...` | `from django_fusion.core.handlers.search import ...` |
| `from apps.handlers.handlers.mixins.fragment import ...` | `from django_fusion.core.handlers.mixins.fragment import ...` |
| `from apps.handlers.handlers.mixins.page import ...` | `from django_fusion.core.handlers.mixins.page import ...` |
| `from apps.handlers.handlers.mixins.wagtail_page import ...` | `from ceptor_ai.handlers.mixins.wagtail_page import ...` |
| `from apps.handlers.handlers.mixins.wagtail_fragment import ...` | `from ceptor_ai.handlers.mixins.wagtail_fragment import ...` |
| `from apps.handlers.handlers.search import ...` (Wagtail) | `from ceptor_ai.handlers.search import ...` |

### Forms

| Before | After |
|--------|-------|
| `from apps.handlers.forms.base import ...` | `from django_fusion.forms import ...` |
| `from apps.handlers.forms import ...` | `from django_fusion.forms import ...` |
| `from apps.handlers.forms import BaseStyledForm` | `from django_fusion.forms import BaseStyledForm` |
| `from apps.handlers.forms import LayoutMixin` | `from django_fusion.forms import LayoutMixin` |
| `from apps.handlers.forms import SecurityMixin` | `from django_fusion.forms import SecurityMixin` |
| `from apps.handlers.forms import ValidationMixin` | `from django_fusion.forms import ValidationMixin` |
| `from apps.handlers.forms import PasswordVerificationMixin` | `from django_fusion.forms import PasswordVerificationMixin` |
| `from apps.handlers.forms import FormAjaxCompleteMixin` | `from django_fusion.comp.forms import FormAjaxCompleteMixin` |
| `from apps.handlers.forms import FormDependentSelectMixin` | `from django_fusion.comp.forms import FormDependentSelectMixin` |
| `from apps.handlers.forms import ModelForm` | `from django_fusion.comp.forms import ModelForm` |

### Validators / Filters

| Before | After |
|--------|-------|
| `from apps.handlers.filters.validators import UniqueFieldValidator` | `from django_fusion.filters.validators import UniqueFieldValidator` |
| `from apps.handlers.filters.validators import SlugFieldValidator` | `from django_fusion.filters.validators import SlugFieldValidator` |
| `from apps.handlers.filters import BaseFilterMethod` | `from django_fusion.filters import BaseFilterMethod` |
| `from apps.handlers.filters import DictFilterMethod` | `from django_fusion.filters import DictFilterMethod` |

### Contrib Utilities

| Before | After |
|--------|-------|
| `from apps.handlers.contrib.enums import ...` | `from django_fusion.contrib.enums import ...` |
| `from apps.handlers.contrib.choices import ...` | `from django_fusion.contrib.choices import ...` |
| `from apps.handlers.contrib.context import ...` | `from django_fusion.contrib.context import ...` |
| `from apps.handlers.contrib.schemas import ...` | `from django_fusion.contrib.schemas import ...` |
| `from apps.handlers.contrib.responses import ...` | `from django_fusion.contrib.responses import ...` |
| `from apps.handlers.contrib import DEFAULT` | `from django_fusion.contrib import DEFAULT` |
| `from apps.handlers.contrib import camel_case_to_underscore` | `from django_fusion.contrib import camel_case_to_underscore` |

### Wagtail Components

| Before | After |
|--------|-------|
| `from apps.pages.comp.blocks import MediaBlock` | `from ceptor_ai.comp.blocks import MediaBlock` |
| `from apps.pages.comp.blocks import ContentBlock` | `from ceptor_ai.comp.blocks import ContentBlock` |
| `from apps.pages.snippets import ...` | `from ceptor_ai.contrib.snippets import ...` |
| `from apps.pages.wagtail_hooks import ...` | `from ceptor_ai.contrib.wagtail_hooks import ...` |
| `from apps.handlers.comp.blocks import OrganizationChooserBlock` | `from ceptor_ai.comp.blocks import OrganizationChooserBlock` |
| `from apps.handlers.comp.blocks import EventSectionBlock` | `from ceptor_ai.comp.blocks import EventSectionBlock` |
| `from apps.handlers.comp.blocks import ServicesSectionBlock` | `from ceptor_ai.comp.blocks import ServicesSectionBlock` |

### Email Components

| Before | After |
|--------|-------|
| `from apps.handlers.email.selectors import RoleBasedEmailTemplateSelector` | `from ceptor_ai.email.selectors import RoleBasedEmailTemplateSelector` |
| `from apps.handlers.email.registry import EmailTemplateRegistry` | `from ceptor_ai.email.registry import EmailTemplateRegistry` |

### Testing Infrastructure

| Before | After |
|--------|-------|
| `from django.test import TestCase` | `from django_fusion.tests.base import BaseTestCase` |
| `from apps.handlers.tests.factories import ...` | `from django_fusion.tests.factories import ...` |
| `from apps.handlers.tests.assertions import ...` | `from django_fusion.tests.assertions import ...` |
| `from apps.handlers.tests.fixtures import ...` | `from django_fusion.tests.fixtures import ...` |
| `from apps.handlers.tests.mixins import ...` | `from django_fusion.tests.mixins import ...` |
| Custom Hypothesis strategies | `from django_fusion.tests.base import st_email, st_slug, st_uuid` |

### Health Checks

| Before | After |
|--------|-------|
| `from apps.handlers.views.health import HealthCheckView` | `from django_fusion.health.views import HealthCheckView` |
| `from apps.handlers.views.health import DatabaseHealthView` | `from django_fusion.health.views import DatabaseHealthView` |
| `from apps.handlers.views.health import AssetsHealthView` | `from django_fusion.health.views import AssetsHealthView` |
| `from apps.handlers.views.health import MediaHealthView` | `from django_fusion.health.views import MediaHealthView` |
| Custom health check URLs | `path('health/', include('django_fusion.health.urls'))` |

### UI Components

| Before | After |
|--------|-------|
| `from apps.handlers.comp.widgets import ...` | `from django_fusion.comp.widgets import ...` |
| `from apps.handlers.comp.payloads import ...` | `from django_fusion.comp.payloads import ...` |
| `from apps.handlers.comp.site import ComponentViews` | `from django_fusion.site import ComponentViews` |
| `from apps.handlers.comp.site import NotificationMixin` | `from django_fusion.site import NotificationMixin` |
| `from apps.handlers.comp.site import PageHandler` | `from django_fusion.site import PageHandler` |
| `from apps.handlers.comp.forms.layout import LayoutElement` | `from django_fusion.comp.forms.layout import LayoutElement` |
| `from apps.handlers.comp.views.includes import PaginatedBaseView` | `from django_fusion.comp.views.includes import PaginatedBaseView` |

### Models

| Before | After |
|--------|-------|
| `from apps.handlers.models import BaseModel` | `from django_fusion.core.models import BaseModel` |
| `from apps.handlers.models import Person` | `from django_fusion.core.models import Person` |
| `from apps.handlers.models import Certificate` | `from django_fusion.core.models import Certificate` |
| `from apps.handlers.models import Message` | `from django_fusion.core.models import Message` |
| `from apps.handlers.models.manage.company import Organization` | `from apps.accounts.models.manage.company import Organization` |

### Rendering

| Before | After |
|--------|-------|
| `from apps.handlers.rendering import TemplateRenderer` | `from django_fusion.rendering import TemplateRenderer` |

### Package-Level Shims (ceptor_ai re-exports from django_fusion)

These ceptor_ai paths re-export from django_fusion for backward compatibility:

| ceptor_ai path | Actual source |
|-------------------|---------------|
| `ceptor_ai.pipelines.backends` | `django_fusion.backends` |
| `ceptor_ai.pipelines.filters` | `django_fusion.filters` |
| `ceptor_ai.pipelines.managers` | `django_fusion.managers` |
| `ceptor_ai.pipelines.middlewares` | `django_fusion.middlewares` |
| `ceptor_ai.pipelines.mixins` | `django_fusion.mixins` |
| `ceptor_ai.logging_config` | `django_fusion.logging_config` |
| `ceptor_ai.forms` | `django_fusion.forms` |
| `ceptor_ai.contrib` | `django_fusion.contrib` |

Prefer the canonical `django_fusion.*` paths in new code.

---

## Deprecated APIs and Replacements

This section documents all deprecated APIs, their replacements, migration paths, and common errors encountered during migration.

### 1. ServiceMixin (Moved from django_fusion to ceptor_ai)

**Deprecated**: `django_fusion.mixins.service.ServiceMixin`
**Replacement**: `ceptor_ai.pipelines.mixins.service.ServiceMixin`

**Why it was deprecated**: ServiceMixin contained Wagtail dependencies, violating the `django_fusion` package's "no Wagtail" boundary rule. All Wagtail-related code must reside in `ceptor_ai` to maintain clean separation between pure Django foundation logic and Wagtail automation logic.

**Before/After Example**:

```python
# BEFORE (Deprecated)
from django_fusion.mixins.service import ServiceMixin

class MyService(ServiceMixin):
    """Service using deprecated ServiceMixin."""
    def process_data(self):
        # This mixin had Wagtail imports internally
        return self._wagtail_dependent_method()

# AFTER (Replacement)
from ceptor_ai.pipelines.mixins.service import ServiceMixin

class MyService(ServiceMixin):
    """Service using correct ServiceMixin location."""
    def process_data(self):
        # Same functionality, now in correct package
        return self._wagtail_dependent_method()
```

**Migration Path**:
1. Update import statement from `django_fusion.mixins.service` to `ceptor_ai.pipelines.mixins.service`
2. Verify no other `django_fusion` code imports Wagtail components
3. Run boundary checker to ensure compliance: `python scripts/check_boundaries.py`

**Common Migration Errors and Fixes**:
- **ImportError**: `Cannot import name 'ServiceMixin' from 'django_fusion.mixins'`
  - **Fix**: Update import to `from ceptor_ai.pipelines.mixins.service import ServiceMixin`
- **Boundary Violation**: `django_fusion imports wagtail`
  - **Fix**: Move all Wagtail-dependent code from `django_fusion` to `ceptor_ai`
- **Circular Dependency**: ServiceMixin now in `ceptor_ai` but code needs pure Django version
  - **Fix**: Extract pure Django functionality to separate mixin in `django_fusion`, keep Wagtail-dependent parts in `ceptor_ai`

### 2. Seeder Shim (ceptor_ai.seeder → django_fusion.seeder)

**Deprecated**: `ceptor_ai.seeder` (shim module that imported `django_fusion.seeder`)
**Replacement**: `django_fusion.seeder` directly

**Why it was deprecated**: The shim violated the "grep-test-only" boundary rule. `django_fusion` is a testing-only package and must not be imported by production code (`ceptor_ai`). The shim created an indirect dependency that broke this rule.

**Before/After Example**:

```python
# BEFORE (Deprecated)
from ceptor_ai.seeder import DatabaseSeeder  # Indirect import via shim

seeder = DatabaseSeeder()
seeder.seed_test_data()  # Production code importing test infrastructure

# AFTER (Replacement)
# Production code should NOT import seeder functionality
# Test code imports directly from django_fusion
from django_fusion.seeder import DatabaseSeeder

# Only in test files, never in production code
class MyTests(BaseTestCase):
    def setUp(self):
        seeder = DatabaseSeeder()
        seeder.seed_test_data()
```

**Migration Path**:
1. Remove all imports of `ceptor_ai.seeder` from production code
2. Update test code to import `django_fusion.seeder` directly
3. Ensure no production code imports `django_fusion` modules
4. Run boundary checker: `python scripts/check_boundaries.py --rule grep-test-only`

**Common Migration Errors and Fixes**:
- **ImportError**: `No module named 'ceptor_ai.seeder'`
  - **Fix**: Update test code to use `django_fusion.seeder`, remove from production code
- **Boundary Violation**: `ceptor_ai imports django_fusion`
  - **Fix**: Remove the shim module and update all imports
- **Production Code Dependency**: Production code needs seeding functionality
  - **Fix**: Move seeding logic to `django_fusion` or `ceptor_ai` with proper boundaries

### 3. Direct CartService/PersonService/MessageService (Replaced by Thin Subclass Pattern)

**Deprecated**: Monolithic service implementations in project apps
**Replacement**: Thin subclasses of package base classes (`CartServiceBase`, `PersonServiceBase`, `MessageServiceBase`)

**Why it was deprecated**: Duplicated business logic across projects violated DRY principle. The thin subclass pattern centralizes business logic in packages while allowing project-specific customizations.

**Before/After Example**:

```python
# BEFORE (Deprecated - Monolithic implementation)
# apps/lms/services/cart.py
class CartService:
    """Full 200+ line implementation duplicated across projects."""
    @classmethod
    def add_to_cart(cls, user, item, quantity):
        # Business logic duplicated in both projects
        cart = Cart.objects.get_or_create(user=user)
        # 50+ lines of validation, business rules, etc.
        cart.items.add(item, quantity=quantity)
        return cart

    @classmethod
    def remove_from_cart(cls, user, item):
        # Another 50+ lines of duplicated logic
        ...

    # 10+ more methods with duplicated logic

# AFTER (Replacement - Thin subclass pattern)
# apps/lms/services/cart.py
from ceptor_ai.pipelines.services.cart import CartServiceBase
from apps.lms.models import Cart

class CartService(CartServiceBase):
    """
    Thin subclass delegating to ceptor_ai.pipelines.services.CartServiceBase.
    Only contains project-specific overrides.
    """
    cart_model = Cart

    # Optional: Only override if project-specific behavior needed
    @classmethod
    def add_to_cart(cls, user, item, quantity):
        # Add project-specific validation
        if not cls._validate_ctc_requirements(user, item):
            return (False, "CTC requirements not met", None)

        # Delegate to base class implementation
        return super().add_to_cart(user, item, quantity)

    @classmethod
    def _validate_ctc_requirements(cls, user, item):
        """Project-specific validation logic."""
        return user.is_authenticated and item.is_available
```

**Migration Path**:
1. Identify all service classes in project apps (`CartService`, `PersonService`, `MessageService`, `FormSubmissionService`)
2. Replace with thin subclasses of corresponding base classes in `ceptor_ai.pipelines.services`
3. Move business logic to package base classes
4. Keep only project-specific overrides in project services
5. Update all imports to use new service classes
6. Run tests to verify functionality preserved

**Common Migration Errors and Fixes**:
- **Missing Base Class**: `ImportError: cannot import name 'CartServiceBase'`
  - **Fix**: Ensure `ceptor_ai` is installed and import path is correct: `from ceptor_ai.pipelines.services.cart import CartServiceBase`
- **Method Signature Mismatch**: Base class methods have different signatures
  - **Fix**: Update project service methods to match base class signatures, use `super()` to call base implementation
- **Broken Tests**: Tests fail after migration to thin subclass pattern
  - **Fix**: Update test imports and mock references, ensure tests use new service instances
- **Missing Project-Specific Logic**: Business logic lost during migration
  - **Fix**: Carefully extract project-specific logic to overrides, keep common logic in base classes

### 4. Direct TestCase Usage (Replaced by BaseTestCase from django_fusion)

**Deprecated**: `from django.test import TestCase`
**Replacement**: `from django_fusion.tests.base import BaseTestCase`

**Why it was deprecated**: `BaseTestCase` provides unified testing infrastructure including Hypothesis helpers (`st_email`, `st_slug`, `st_uuid`), consistent setup/teardown patterns, and integration with `django_fusion` test ecosystem.

**Before/After Example**:

```python
# BEFORE (Deprecated)
from django.test import TestCase
from hypothesis import given, strategies as st
import re

class UserTest(TestCase):
    """Test using plain TestCase with manual Hypothesis setup."""

    @given(st.emails())
    def test_email_validation(self, email):
        # Manual email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.assertTrue(re.match(pattern, email) is not None)

# AFTER (Replacement)
from django_fusion.tests.base import BaseTestCase
from django_fusion.tests.base import st_email

class UserTest(BaseTestCase):
    """Test using BaseTestCase with django_fusion Hypothesis helpers."""

    @given(st_email())
    def test_email_validation(self, email):
        # st_email() generates valid emails automatically
        self.assertValidEmail(email)
```

**Migration Path**:
1. Replace all `from django.test import TestCase` with `from django_fusion.tests.base import BaseTestCase`
2. Update test class inheritance: `class MyTest(TestCase):` → `class MyTest(BaseTestCase):`
3. Replace custom Hypothesis strategies with `django_fusion` helpers (`st_email`, `st_slug`, `st_uuid`)
4. Update imports for test utilities (`factories`, `assertions`, `fixtures`, `mixins`)
5. Run test suite to verify all tests pass

**Common Migration Errors and Fixes**:
- **ImportError**: `No module named 'django_fusion'`
  - **Fix**: Install `django_fusion` package: `cd venv/libs/django-fusion && uv install`
- **Missing Hypothesis Helpers**: `st_email not found`
  - **Fix**: Import from correct location: `from django_fusion.tests.base import st_email, st_slug, st_uuid`
- **Test Method Conflicts**: BaseTestCase has different setUp/tearDown behavior
  - **Fix**: Review BaseTestCase implementation and adjust test setup accordingly
- **Deprecated Assertions**: Custom assertions no longer available
  - **Fix**: Update to use `django_fusion.tests.assertions` or standard unittest assertions

### 5. Direct Import of Project-Specific Handlers/Blocks (Moved to ceptor_ai)

**Deprecated**: Direct imports from project apps for Wagtail components
**Replacement**: Imports from `ceptor_ai` package

**Why it was deprecated**: Wagtail-specific components (handlers, blocks, snippets, hooks) belong in `ceptor_ai` package, not in project apps. This ensures reusability across projects and clean separation of concerns.

**Before/After Examples**:

```python
# BEFORE (Deprecated - Project-specific imports)
from apps.handlers.handlers.mixins.wagtail_page import WagtailPageHandlerMixin
from apps.handlers.comp.blocks import OrganizationChooserBlock
from apps.pages.snippets import FeaturedSnippet
from apps.pages.wagtail_hooks import register_custom_hooks

# AFTER (Replacement - Package imports)
from ceptor_ai.handlers.mixins.wagtail_page import WagtailPageHandlerMixin
from ceptor_ai.comp.blocks import OrganizationChooserBlock
from ceptor_ai.contrib.snippets import FeaturedSnippet
from ceptor_ai.contrib.wagtail_hooks import register_custom_hooks
```

**Specific Replacements**:

| Deprecated Import | Replacement Import |
|-------------------|-------------------|
| `from apps.handlers.handlers.mixins.wagtail_page import ...` | `from ceptor_ai.handlers.mixins.wagtail_page import ...` |
| `from apps.handlers.handlers.mixins.wagtail_fragment import ...` | `from ceptor_ai.handlers.mixins.wagtail_fragment import ...` |
| `from apps.handlers.handlers.search import ...` (Wagtail) | `from ceptor_ai.handlers.search import ...` |
| `from apps.handlers.comp.blocks import OrganizationChooserBlock` | `from ceptor_ai.comp.blocks import OrganizationChooserBlock` |
| `from apps.handlers.comp.blocks import EventSectionBlock` | `from ceptor_ai.comp.blocks import EventSectionBlock` |
| `from apps.handlers.comp.blocks import ServicesSectionBlock` | `from ceptor_ai.comp.blocks import ServicesSectionBlock` |
| `from apps.pages.comp.blocks import MediaBlock` | `from ceptor_ai.comp.blocks import MediaBlock` |
| `from apps.pages.comp.blocks import ContentBlock` | `from ceptor_ai.comp.blocks import ContentBlock` |
| `from apps.pages.snippets import ...` | `from ceptor_ai.contrib.snippets import ...` |
| `from apps.pages.wagtail_hooks import ...` | `from ceptor_ai.contrib.wagtail_hooks import ...` |

**Migration Path**:
1. Identify all Wagtail component imports in project code
2. Update import statements to use `ceptor_ai` paths
3. Verify components exist in `ceptor_ai` package
4. Move any missing components from projects to `ceptor_ai`
5. Update templates referencing Wagtail components
6. Run tests to verify functionality preserved

**Common Migration Errors and Fixes**:
- **ImportError**: `No module named 'ceptor_ai.handlers.mixins.wagtail_page'`
  - **Fix**: Ensure `ceptor_ai` is installed and the component exists in the package
- **Missing Component**: Component not yet moved to `ceptor_ai`
  - **Fix**: Move the component from project to `ceptor_ai`, update all references
- **Template Errors**: Templates reference old import paths
  - **Fix**: Update template `{% load %}` tags and component references
- **Circular Dependencies**: `ceptor_ai` imports project-specific code
  - **Fix**: Ensure `ceptor_ai` has no project imports, move shared code to packages

### 6. Additional Deprecated Patterns

**Deprecated**: Direct use of project-specific model managers
**Replacement**: Import managers from `django_fusion.managers`

**Example**:
```python
# BEFORE (Deprecated)
from apps.accounts.managers import UserManager

# AFTER (Replacement)
from django_fusion.core.managers import UserManager
```

**Deprecated**: Project-specific middleware implementations
**Replacement**: Import middleware from `django_fusion.middlewares` or `ceptor_ai.contrib`

**Example**:
```python
# BEFORE (Deprecated)
from apps.accounts.middleware import ErrorTrackerMiddleware

# AFTER (Replacement)
from django_fusion.middlewares.error_tracker import ErrorTrackerMiddleware
```

**Deprecated**: Project-specific form base classes
**Replacement**: Import forms from `django_fusion.forms`

**Example**:
```python
# BEFORE (Deprecated)
from apps.accounts.forms import BaseStyledForm

# AFTER (Replacement)
from django_fusion.forms import BaseStyledForm
```

---

## Migration Validation Checklist

After updating deprecated APIs, verify:

1. **Boundary Rules**: Run `python scripts/check_boundaries.py` - zero violations
2. **Import Errors**: Run `python -c "import django_fusion; import ceptor_ai; import django_fusion"` - no errors
3. **Test Suite**: Run full test suite for all packages and projects - all tests pass
4. **Template Resolution**: Verify all templates render correctly
5. **Service Functionality**: Test key service methods (cart operations, user management, messaging)
6. **Health Checks**: Verify `/health/` endpoints return HTTP 200
7. **Database Operations**: Test CRUD operations on key models
8. **Admin Interface**: Verify Django admin and Wagtail admin work correctly

---

## Settings Changes

## Settings Changes

### MIDDLEWARE

```python
# Before
MIDDLEWARE = [
    ...
    "apps.handlers.middleware.ErrorTrackerMiddleware",
    "apps.handlers.middleware.PrivacyConsentMiddleware",
    ...
]

# After
MIDDLEWARE = [
    ...
    "django_fusion.middlewares.error_tracker.ErrorTrackerMiddleware",
    "ceptor_ai.contrib.privacy.middleware.PrivacyConsentMiddleware",
    ...
]
```

### AUTHENTICATION_BACKENDS

```python
# Before
AUTHENTICATION_BACKENDS = [
    "apps.handlers.backends.auth.CustomAuthBackend",
]

# After
AUTHENTICATION_BACKENDS = [
    "django_fusion.backends.auth.CustomAuthBackend",
]
```

### ACCOUNT_ADAPTER / SOCIALACCOUNT_ADAPTER

```python
# Before
ACCOUNT_ADAPTER = "apps.handlers.adapters.allauth.CustomAccountAdapter"
SOCIALACCOUNT_ADAPTER = "apps.handlers.adapters.social.CustomSocialAccountAdapter"

# After
ACCOUNT_ADAPTER = "django_fusion.adapters.allauth.CustomAccountAdapter"
SOCIALACCOUNT_ADAPTER = "django_fusion.adapters.social.CustomSocialAccountAdapter"
```

### Health Check URLs

```python
# Before — custom health check views
urlpatterns = [
    path("health/", views.health_check),
]

# After — unified health check from django_fusion
from django.urls import path, include

urlpatterns = [
    path("health/", include("django_fusion.health.urls")),
]
```

---

## Troubleshooting

This section covers common issues encountered during migration and how to resolve them.

### 1. Common Import Errors

#### ImportError: No module named 'apps.handlers'

The `handlers` app was renamed to `accounts`. Update your import:

```python
# Before
from apps.handlers.managers import RoleHierarchyManager

# After
from django_fusion.core.managers import RoleHierarchyManager
```

Also update `INSTALLED_APPS` to use `apps.accounts` instead of `apps.handlers`.

#### ImportError: No module named 'apps.LMS'

The `LMS` app was renamed to `lms` (lowercase). Update your import:

```python
# Before
from apps.LMS.models import Cart

# After
from apps.lms.models import Cart
```

#### ImportError: No module named 'apps.pages'

The `pages` app was renamed to `content`. Update your import:

```python
# Before
from apps.pages.models import HomePage

# After
from apps.content.models import HomePage
```

#### ImportError: ModuleNotFoundError for django_fusion, ceptor_ai, or django_fusion

Ensure packages are installed and in your Python path:

```bash
# Install all packages
cd venv/libs/django-fusion && uv install
cd venv/libs/ceptor-ai && uv install
cd venv/libs/django-fusion && uv install

# Verify imports work
python -c "import django_fusion; import ceptor_ai; import django_fusion; print('All imports successful')"
```

#### ImportError: Cannot import name 'ServiceMixin' from 'django_fusion.mixins'

`ServiceMixin` was moved to `ceptor_ai` due to Wagtail dependencies:

```python
# Before
from django_fusion.mixins.service import ServiceMixin

# After
from ceptor_ai.pipelines.mixins.service import ServiceMixin
```

### 2. Migration Reversal Issues

#### Error: "Cannot reverse migration" or "Migration has no reverse operation"

All migrations should have reverse operations. If you encounter this:

1. Check the migration file for missing `operations.reverse()` methods
2. Run `python scripts/validate_migrations.py` to identify problematic migrations
3. For app rename migrations, ensure both `AlterModelTable` and `ContentType` updates are reversible

#### Error when rolling back app rename migrations

App rename migrations preserve table names via `AlterModelTable`. If rollback fails:

```bash
# Check migration state
python manage.py showmigrations

# Manually inspect the migration
python manage.py sqlmigrate accounts 0001_rename_app_label

# If needed, create a manual rollback migration
python manage.py makemigrations --empty accounts --name rollback_rename
```

#### Data loss during migration reversal

Always backup before migration operations:

```bash
# Create database backup
python manage.py dumpdata --all --output=backup_before_migration.json

# Create media backup
tar -czf media_backup_before_migration.tar.gz media/
```

### 3. Template Reference Problems

#### TemplateDoesNotExist: Template not found after refactoring

Templates remain in projects only, not packages. Check:

1. Template paths in project `templates/` directories
2. `{% include %}` and `{% extends %}` statements reference correct paths
3. View `render()` calls use correct template paths

#### Static file references broken

Static files follow the same pattern as templates:

1. Reusable static assets are in packages' `static/` directories
2. Project-specific static files remain in project `static/` directories
3. Update `{% static %}` tags to reference new paths

#### Template tags not loading

Templatetags placement:

1. Reusable templatetags moved to packages (`django_fusion/templatetags/` or `ceptor_ai/templatetags/`)
2. Project-specific templatetags remain in project `templatetags/` directories
3. Update `{% load %}` statements with new module names

### 4. Boundary Violation Errors

#### django_fusion imports Wagtail (boundary violation)

If you see `django_fusion imports wagtail` error:

1. Run `python scripts/check_boundaries.py` to find all violations
2. Move Wagtail-dependent code from `django_fusion` to `ceptor_ai`
3. Update all imports in both packages and projects
4. Common violations: `ServiceMixin`, Wagtail block classes, Wagtail-specific handlers

#### django_fusion imported by production code (grep-test-only violation)

`django_fusion` is for testing only. If production code imports it:

1. Find the production file importing `django_fusion`
2. Move the import to a test file, or
3. Use the production equivalent (e.g., `django_fusion.middlewares` instead of `django_fusion.tests`)

#### nawaai imports Django (nawaai-no-django violation)

`nawaai` must be pure Python with zero Django imports:

1. Refactor Django-dependent code out of `nawaai`
2. Use dependency injection or pure Python alternatives
3. Move Django integration to `django_fusion` or `ceptor_ai`

#### Circular import detected

Circular dependencies break the dependency direction:

1. Run `python scripts/detect_cycles.py` to find all cycles
2. Apply suggested break strategies: extract interface, dependency injection, or event-based communication
3. Common cycles: between `django_fusion` and `ceptor_ai`, or within domain modules

### 5. Test Failures After Migration

#### TestCase import errors

All tests should use `django_fusion` infrastructure:

```python
# Before
from django.test import TestCase

# After
from django_fusion.tests.base import BaseTestCase
```

#### Factory import errors

Factories moved to `django_fusion`:

```python
# Before
from apps.handlers.tests.factories import UserFactory

# After
from django_fusion.tests.factories import UserFactory
```

#### Assertion import errors

Assertions moved to `django_fusion`:

```python
# Before
from apps.handlers.tests.assertions import assert_user_has_role

# After
from django_fusion.tests.assertions import assert_user_has_role
```

#### Hypothesis strategy errors

Use `django_fusion` Hypothesis helpers:

```python
# Before: Custom strategies
from hypothesis import strategies as st

# After: Use django_fusion helpers
from django_fusion.tests.base import st_email, st_slug, st_uuid
```

#### Health check test failures

Health checks unified in `django_fusion`:

```python
# Before: Custom health check views
path('health/', views.health_check)

# After: Use django_fusion health URLs
path('health/', include('django_fusion.health.urls'))
```

### 6. Database Migration Issues

#### Migration errors after app rename

App renames use `AlterModelTable` to preserve table names:

1. Verify `AlterModelTable` migration exists for each renamed app
2. Verify `ContentType` data migration exists and runs successfully
3. Check migration dependencies are correct

```bash
# Check migration state
python manage.py showmigrations

# Apply specific migration
python manage.py migrate accounts 0001_rename_app_label

# Check for unapplied migrations
python manage.py migrate --plan
```

#### Foreign key constraint errors

When renaming apps, foreign keys reference old app labels:

1. Data migrations update `ContentType` records
2. Check `django_content_type` table for correct app_label values
3. Run `python manage.py update_contenttypes` if needed

#### Table already exists errors

`AlterModelTable` preserves physical table names. If you see "table already exists":

1. Check for duplicate `CreateModel` operations
2. Verify `AlterModelTable` correctly renames the app_label only
3. Check migration dependencies and order

#### Migration reversal data loss

To safely test migration reversal:

```bash
# Backup data first
python manage.py dumpdata --all --output=before_reversal.json

# Test reversal
python manage.py migrate accounts zero

# Verify data integrity
python manage.py loaddata before_reversal.json

# Re-apply migration
python manage.py migrate accounts
```

#### Migration dependencies incorrect

Check migration dependencies in `dependencies` list:

```python
# Correct: depends on previous migration in same app
dependencies = [
    ('accounts', '0001_initial'),
]

# Incorrect: circular or missing dependencies
dependencies = [
    ('content', '0002_some_migration'),  # Wrong app
]
```

### 7. Service Layer Issues

#### CartService/PersonService/MessageService not found

Services moved to thin subclass pattern:

```python
# Before: Monolithic implementation
class CartService:
    def add_to_cart(self, user, item, quantity):
        # 100+ lines of business logic
        pass

# After: Thin subclass
from ceptor_ai.pipelines.services.cart import CartServiceBase
from apps.lms.models import Cart

class CartService(CartServiceBase):
    """Delegates to ceptor_ai.pipelines.services.CartServiceBase."""
    cart_model = Cart
    # Only project-specific overrides here
```

#### Service method signatures changed

Base service classes in packages have standardized signatures:

1. Check method signatures in package base classes
2. Update thin subclass method overrides to match
3. Use `super().method()` to call base implementation

#### Missing service dependencies

Services may depend on other services or managers:

1. Check service `__init__` methods for required dependencies
2. Update dependency injection in project service subclasses
3. Ensure all dependencies are imported from correct packages

### 8. Verification and Recovery

#### How to verify migration success

Run verification commands:

```bash
# Check boundary violations
python scripts/check_boundaries.py

# Check for remaining duplication
python scripts/analyze_duplication.py --threshold 0.70

# Run import linter
import-linter --config .importlinter

# Run all tests
cd venv/libs/django-fusion && uv run pytest tests/ -v
cd venv/libs/ceptor-ai && uv run pytest tests/ -v
cd venv/libs/django-fusion && uv run pytest tests/ -v
cd ctc-research.com && uv run pytest tests/ -v
cd structa.cloud && uv run pytest tests/ -v
```

#### How to recover from failed migration

Use git history and backups:

```bash
# Find when a file was moved
git log --follow --name-only -- venv/libs/django-fusion/src/django_fusion/managers/role_hierarchy.py

# Revert to a rollback point
git checkout rollback-phase-1-start

# Restore from backup
python manage.py loaddata backup_before_migration.json
tar -xzf media_backup_before_migration.tar.gz
```

#### How to get help

If you encounter issues not covered here:

1. Check `ARCHITECTURE.md` for package responsibilities
2. Review `MIGRATION_GUIDE.md` for import path changes
3. Run verification commands to identify specific issues
4. Check git history for original file locations
5. Use rollback points to restore working state

---

## Verification Commands

```bash
# Check boundary violations
python scripts/check_boundaries.py

# Check for remaining duplication
python scripts/analyze_duplication.py --threshold 0.70

# Run import linter
import-linter --config .importlinter

# Run tests for all packages
cd venv/libs/django-fusion && uv run pytest tests/ -v
cd venv/libs/ceptor-ai && uv run pytest tests/ -v
cd venv/libs/django-fusion && uv run pytest tests/ -v
cd venv/libs/nawaai && uv run pytest tests/ -v

# Run tests for projects
cd ctc-research.com && uv run pytest tests/ -v
cd structa.cloud && uv run pytest tests/ -v
```

---

## Migration Examples

### Example 1: Updating a Manager Import

**Before:**
```python
from apps.handlers.managers.role_hierarchy import RoleHierarchyManager

manager = RoleHierarchyManager()
permissions = manager.get_all_permissions_for_role('admin')
```

**After:**
```python
from django_fusion.core.managers import RoleHierarchyManager

manager = RoleHierarchyManager()
permissions = manager.get_all_permissions_for_role('admin')
```

### Example 2: Updating a Service to Thin Subclass Pattern

**Before:**
```python
# apps/lms/services/cart.py
class CartService:
    @classmethod
    def add_to_cart(cls, user, item, quantity):
        # 100+ lines of business logic
        cart = Cart.objects.get_or_create(user=user)
        cart.items.add(item, quantity=quantity)
        return cart
```

**After:**
```python
# apps/lms/services/cart.py
from ceptor_ai.pipelines.services.cart import CartServiceBase
from apps.lms.models import Cart

class CartService(CartServiceBase):
    """Delegates to ceptor_ai.pipelines.services.CartServiceBase."""
    cart_model = Cart

    # Only project-specific overrides
    @classmethod
    def add_to_cart(cls, user, item, quantity):
        # Add project-specific validation
        if not cls._validate_ctc_requirements(user, item):
            return (False, "CTC requirements not met", None)

        # Delegate to base class
        return super().add_to_cart(user, item, quantity)
```

### Example 3: Updating Test Infrastructure

**Before:**
```python
from django.test import TestCase
from apps.handlers.tests.factories import UserFactory

class MyTest(TestCase):
    def test_user_creation(self):
        user = UserFactory()
        self.assertEqual(user.username, 'testuser')
```

**After:**
```python
from django_fusion.tests.base import BaseTestCase
from django_fusion.tests.factories import UserFactory

class MyTest(BaseTestCase):
    def test_user_creation(self):
        user = UserFactory()
        self.assertEqual(user.username, 'testuser')
```

### Example 4: Updating Health Check URLs

**Before:**
```python
# configs/urls.py
from django.urls import path
from apps.handlers.views.health import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view()),
]
```

**After:**
```python
# configs/urls.py
from django.urls import path, include

urlpatterns = [
    path('health/', include('django_fusion.health.urls')),
]
```

---

## Summary of Key Changes

1. **App Renames**: `handlers` → `accounts`, `LMS` → `lms`/`alliance`, `pages` → `content`
2. **Package Extraction**: Business logic moved to `django_fusion` (pure Django) and `ceptor_ai` (Wagtail + automation)
3. **Thin Layer Pattern**: Projects now delegate to package base classes
4. **Testing Unification**: All tests use `django_fusion` infrastructure
5. **Health Check Unification**: Health endpoints provided by `django_fusion.health`
6. **Boundary Enforcement**: Strict import rules enforced by import-linter
7. **Zero Duplication**: All shared logic in packages, no duplication across projects

This migration guide should help developers update their code after the architectural refactoring. For additional help, refer to `ARCHITECTURE.md` for package responsibilities and design patterns.
