# Core Code Extraction: Quick Reference Guide

**Version:** 1.0
**Date:** April 14, 2026
**Purpose:** Quick lookup for what to extract and what to keep

---

## Quick Decision Matrix

### Models

| Model Type | Extract? | Location | Notes |
|-----------|----------|----------|-------|
| BaseModel | ✅ Yes | django-osoul | Base with timestamps, UUID |
| TimestampedModel | ✅ Yes | django-osoul | Mixin for timestamps |
| SluggedModel | ✅ Yes | django-osoul | Mixin for slugs |
| PublishableModel | ✅ Yes | django-osoul | Mixin for publish status |
| User (project-specific) | ❌ No | Website | Keep in project |
| Post (project-specific) | ❌ No | Website | Keep in project |
| Comment (project-specific) | ❌ No | Website | Keep in project |

### Forms

| Form Type | Extract? | Location | Notes |
|-----------|----------|----------|-------|
| BaseForm | ✅ Yes | django-osoul | Base form class |
| BaseModelForm | ✅ Yes | django-osoul | Base model form |
| Common validators | ✅ Yes | django-osoul | Reusable validators |
| UserForm (project) | ❌ No | Website | Project-specific |
| PostForm (project) | ❌ No | Website | Project-specific |

### Views

| View Type | Extract? | Location | Notes |
|-----------|----------|----------|-------|
| BaseView | ✅ Yes | django-osoul | Base view class |
| BaseModelView | ✅ Yes | django-osoul | Base model view |
| Mixins | ✅ Yes | django-osoul | Reusable mixins |
| UserView (project) | ❌ No | Website | Project-specific |
| PostView (project) | ❌ No | Website | Project-specific |

### Utilities

| Utility | Extract? | Location | Notes |
|---------|----------|----------|-------|
| String helpers | ✅ Yes | django-osoul | Formatting, slugs |
| Date helpers | ✅ Yes | django-osoul | Date/time utilities |
| Validation helpers | ✅ Yes | django-osoul | Common validators |
| Permission helpers | ✅ Yes | django-osoul | Permission checks |
| Project-specific utils | ❌ No | Website | Keep in project |

### Email

| Component | Extract? | Location | Notes |
|-----------|----------|----------|-------|
| Email sending logic | ✅ Yes | crafts-ai | Core email utilities |
| Email templates (base) | ✅ Yes | crafts-ai | Reusable templates |
| Email scheduling | ✅ Yes | crafts-ai | Task scheduling |
| Project emails | ❌ No | Website | Project-specific |

### Tasks

| Component | Extract? | Location | Notes |
|-----------|----------|----------|-------|
| Task base classes | ✅ Yes | crafts-ai | Base task class |
| Task scheduling | ✅ Yes | crafts-ai | Scheduling utilities |
| Task monitoring | ✅ Yes | crafts-ai | Monitoring logic |
| Project tasks | ❌ No | Website | Project-specific |

### Testing

| Component | Extract? | Location | Notes |
|-----------|----------|----------|-------|
| UserFactory | ✅ Yes | django-osoul | Reusable factory |
| BaseModelFactory | ✅ Yes | django-osoul | Base factory |
| Common fixtures | ✅ Yes | django-osoul | Reusable fixtures |
| Project tests | ❌ No | Website | Project-specific |

---

## Extraction Workflow

### Step 1: Identify
```
Is this code reusable across multiple projects?
├─ YES → Extract to package
└─ NO → Keep in website
```

### Step 2: Check for Duplication
```
Is this code duplicated across projects?
├─ YES → Consolidate and extract
└─ NO → Extract if reusable
```

### Step 3: Determine Package
```
Which package does this belong to?
├─ Base models/forms/utilities → django-osoul
├─ Email/tasks/workflows → crafts-ai
├─ Testing utilities → django-osoul
└─ AI/MCP → nawaai
```

### Step 4: Extract
```
1. Create in package
2. Create deprecation shim in website
3. Update imports
4. Run tests
5. Verify no circular imports
```

---

## Common Extraction Patterns

### Pattern 1: Base Model Class

**Before (in website):**
```python
# ctc-research.com/apps/core/models.py
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**After (in django-osoul):**
```python
# venv/libs/django-osoul/src/django_osoul/models/base.py
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

**Deprecation Shim (in website):**
```python
# ctc-research.com/apps/core/models.py
from django_osoul.models import BaseModel

# Keep old import path working
__all__ = ['BaseModel']
```

---

### Pattern 2: Utility Function

**Before (in website):**
```python
# ctc-research.com/apps/core/utils.py
def slugify_text(text):
    """Convert text to slug."""
    return text.lower().replace(' ', '-')
```

**After (in django-osoul):**
```python
# venv/libs/django-osoul/src/django_osoul/utils/text.py
def slugify_text(text):
    """Convert text to slug."""
    return text.lower().replace(' ', '-')
```

**Deprecation Shim (in website):**
```python
# ctc-research.com/apps/core/utils.py
from django_osoul.utils.text import slugify_text

# Keep old import path working
__all__ = ['slugify_text']
```

---

### Pattern 3: Form Base Class

**Before (in website):**
```python
# ctc-research.com/apps/core/forms.py
class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
```

**After (in django-osoul):**
```python
# venv/libs/django-osoul/src/django_osoul/forms/base.py
class BaseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
```

**Deprecation Shim (in website):**
```python
# ctc-research.com/apps/core/forms.py
from django_osoul.forms import BaseForm

# Keep old import path working
__all__ = ['BaseForm']
```

---

## Duplication Examples

### Example 1: Duplicate Utility Functions

**ctc-research.com:**
```python
def format_phone(phone):
    return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
```

**structa.cloud:**
```python
def format_phone(phone):
    return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
```

**Action:** Extract to django-osoul, remove from both websites

---

### Example 2: Duplicate Email Logic

**ctc-research.com:**
```python
def send_welcome_email(user):
    subject = "Welcome!"
    message = f"Hello {user.name}"
    user.email_user(subject, message)
```

**structa.cloud:**
```python
def send_welcome_email(user):
    subject = "Welcome!"
    message = f"Hello {user.name}"
    user.email_user(subject, message)
```

**Action:** Extract to crafts-ai, remove from both websites

---

### Example 3: Duplicate Form Validation

**ctc-research.com:**
```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already exists")
    return email
```

**structa.cloud:**
```python
def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already exists")
    return email
```

**Action:** Extract to django-osoul, remove from both websites

---

## Extraction Checklist

### Before Starting
- [ ] Code categorized (core vs. project-specific)
- [ ] Duplication identified
- [ ] Extraction sequence planned
- [ ] Backward compatibility planned
- [ ] Tests prepared

### During Extraction
- [ ] Code moved to package
- [ ] Deprecation shims created
- [ ] Imports updated
- [ ] Tests run and passing
- [ ] No circular imports detected

### After Extraction
- [ ] Websites still work
- [ ] All tests passing
- [ ] No duplication remains
- [ ] Documentation updated
- [ ] Backward compatibility verified

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Extracting Project-Specific Code
```python
# DON'T extract this - it's project-specific
class CTCResearchUser(models.Model):
    """CTC Research specific user model"""
    research_level = models.IntegerField()
    department = models.CharField(max_length=100)
```

### ✅ Correct: Extract Only Base Code
```python
# DO extract this - it's reusable
class BaseUser(models.Model):
    """Base user model for all projects"""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True
```

---

### ❌ Mistake 2: Creating Circular Dependencies
```python
# DON'T do this
# django-osoul imports from crafts-ai
from crafts_ai.email import send_email

# crafts-ai imports from django-osoul
from django_osoul.models import BaseModel
```

### ✅ Correct: Maintain Dependency Direction
```
django-osoul (foundation)
    ↓
crafts-ai (automation, depends on osoul)
    ↓
nawaai (AI, optional)
```

---

### ❌ Mistake 3: Forgetting Deprecation Shims
```python
# DON'T just move code without shims
# This breaks existing code
```

### ✅ Correct: Create Deprecation Shims
```python
# In website, create shim
from django_osoul.models import BaseModel
import warnings

warnings.warn(
    "Importing from website.models is deprecated. "
    "Use django_osoul.models instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## Quick Commands

### Find Duplicate Code
```bash
# Find duplicate Python files
find . -name "*.py" -type f -exec md5sum {} \; | sort | uniq -d -w32

# Find duplicate functions
grep -r "^def " ctc-research.com structa.cloud --include="*.py" | \
  cut -d: -f2 | sort | uniq -d
```

### Check for Circular Imports
```bash
# Test imports
python -c "import django_osoul; import crafts_ai"

# Check specific module
python -m py_compile venv/libs/django-osoul/src/django_osoul/__init__.py
```

### Update Imports
```bash
# Replace old import paths
sed -i 's/from website\.models import/from django_osoul.models import/g' \
    ctc-research.com/**/*.py
```

### Run Tests
```bash
# Run all tests
pytest ctc-research.com/tests/ structa.cloud/tests/ -v

# Run specific test
pytest ctc-research.com/tests/test_models.py -v
```

---

## Decision Tree

```
Is this code reusable?
├─ NO → Keep in website
└─ YES
    ├─ Is it duplicated?
    │  ├─ YES → Consolidate and extract
    │  └─ NO → Extract if it fits a package
    │
    └─ Which package?
       ├─ Base models/forms/utilities → django-osoul
       ├─ Email/tasks/workflows → crafts-ai
       ├─ Testing utilities → django-osoul
       └─ AI/MCP → nawaai
```

---

## Next Steps

1. **Review this guide** with the team
2. **Use the decision matrix** for each code component
3. **Follow the extraction workflow** for each item
4. **Verify with the checklist** after each extraction
5. **Avoid common mistakes** listed above

---

**Document Status:** ✅ Complete
**Last Updated:** April 14, 2026
**Ready for Use:** Yes
