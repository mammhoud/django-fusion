# 🛠️ Customization Methods

> In-depth guide to customizing Structa Cloud projects — beyond the basic tag system.

> ⚠️ **Historical**: examples referencing `pos-solo/`/`pos-full/` predate the
> merge into `projects/pos/formint-pos/`.

---

## Method Overview

| Method | Risk | Best For |
|--------|------|----------|
| Template Override | 🟢 Low | HTML/CSS changes |
| Config Override | 🟢 Low | Behavior changes via settings |
| Hook Extension | 🟡 Medium | Extending business logic |
| Model Extension | 🟡 Medium | Adding database fields |
| Plugin Development | 🟡 Medium | New features without touching core |
| Core Modification | 🔴 High | Only when absolutely necessary |

---

## 1. Template Override (🟢 Low Risk)

Django's template resolution order enables safe overrides by placing site templates higher in the search path.

### Resolution Order

```
1. projects/<site>/templates/          ← Your overrides go here
2. projects/<site>/assets/templates/   ← Site-specific assets
3. projects/assets/templates/          ← Shared templates
4. projects/<site>/plugins/*/templates/ ← Plugin templates
5. libs/django-fusion/src/.../templates/ ← Framework templates
```

### Example: Override a Course Card

```bash
# 1. Find the original template
rg "course_card" projects/assets/templates/

# 2. Copy to your site's template dir (matching path structure)
mkdir -p projects/lms/templates/components/
cp projects/assets/templates/components/course_card.html \
   projects/lms/templates/components/course_card.html

# 3. Edit freely — your version wins
```

```django
{# projects/lms/templates/components/course_card.html #}
{% extends "components/course_card.html" %}

{% block course_title %}
  <div class="my-custom-card">
    <span class="card__badge">{{ course.level }}</span>
    <h3>{{ course.title }}</h3>
  </div>
{% endblock %}

{% block course_footer %}
  {{ block.super }}
  <button class="btn--quick-enroll">Enroll Now</button>
{% endblock %}
```

### Template Override Rules

- Match the **exact directory path** from the source
- Use `{% extends %}` + `{% block %}` for partial overrides
- Don't modify shared templates directly — they affect all sites
- Check `projects/assets/templates/` first — that's where most shared templates live

---

## 2. Config Override (🟢 Low Risk)

Use Dynaconf settings layers to change behavior without touching code.

### Settings Layering

```yaml
# 1. Shared base (projects/configs/base/)
# 2. Site default (projects/<site>/configs/settings.yml)
# 3. Environment override (projects/<site>/configs/settings.development.yml)
# 4. Production override (projects/<site>/configs/settings.production.yml)
# 5. .env file (secrets, tokens)
```

### Example: Add an AI Model

```yaml
# projects/cypercloud/configs/settings.yml
ai:
  models:
    - name: "llama3.2:latest"
      provider: "ollama"
    - name: "gpt-4o"
      provider: "openai"
      api_key: "${OPENAI_API_KEY}"
    - name: "my-custom-model"          # ← Your addition
      provider: "custom"
      endpoint: "https://my-api.example.com/v1"
      api_key: "${MY_API_KEY}"
```

### Example: Custom POS Settings

```yaml
# projects/pos/pos-solo/configs/settings.yml
store:
  name: "My Store"
  currency: "SAR"
  timezone: "Asia/Riyadh"
  receipt_footer: "Thank you for shopping!"
  tax:
    default_rate: 0.15
    tax_number: "123456789"
```

---

## 3. Hook Extension (🟡 Medium Risk)

Extend business logic through delegation hooks without modifying core code.

### Available Hooks

| Hook | Location | Purpose |
|------|----------|---------|
| `CourseEnrollmentHook` | `lms/plugins/courses/hooks.py` | Before/after course enrollment |
| `RegistrationAdapter` | `plugins/accounts/adapters.py` | Custom registration logic |
| `PaymentProviderHook` | `plugins/payments/hooks.py` | Payment processing pipeline |
| `PDFExportHook` | `VResume/plugins/export/hooks.py` | Resume PDF generation |

### Example: Custom Enrollment Hook

```python
# projects/lms/plugins/courses/hooks.py
from lms.plugins.courses.hooks import CourseEnrollmentHook

class CustomEnrollmentHook(CourseEnrollmentHook):
    def before_enroll(self, student, course):
        """Validate prerequisites before allowing enrollment."""
        if not student.has_completed(course.prerequisites.all()):
            raise EnrollmentError("Missing prerequisites")

    def after_enroll(self, student, course):
        """Post-enrollment actions."""
        # Send welcome SMS
        send_welcome_sms(student.phone, course.title)
        # Create calendar event
        create_calendar_invite(student.email, course.schedule)
        # Notify instructor
        notify_instructor(course.instructor, student)
```

### Example: Custom Payment Provider

```python
# projects/pos/pos-full/plugins/payments/providers.py
from pos.plugins.payments.hooks import PaymentProviderHook

class MadaPaymentProvider(PaymentProviderHook):
    """Saudi Mada payment network integration."""
    provider_id = "mada"
    display_name = "Mada Card"

    def process_payment(self, order, payment_data):
        response = self.mada_api.charge(
            amount=order.total,
            currency=order.currency,
            card_token=payment_data["token"],
        )
        return PaymentResult(
            success=response.ok,
            transaction_id=response.txn_id,
            receipt_url=response.receipt_url,
        )
```

---

## 4. Model Extension (🟡 Medium Risk)

Add fields to existing models without forking.

### Example: Extend Course Model

```python
# projects/lms/plugins/courses/models.py
from lms.plugins.courses.models import Course

class ExtendedCourse(Course):
    """Course with additional LMS-specific fields."""
    class Meta:
        proxy = True

# Or use a profile pattern:
from django.db import models
from lms.plugins.courses.models import Course

class CourseMetadata(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    difficulty_level = models.CharField(max_length=20)
    estimated_hours = models.IntegerField()
    certificate_template = models.ForeignKey('certs.CertificateTemplate', null=True)
    is_featured = models.BooleanField(default=False)
```

---

## 5. Plugin Development (🟡 Medium Risk)

Create new plugins to add features without touching existing code.

### Plugin Structure

```
projects/<site>/plugins/myplugin/
├── __init__.py
├── apps.py               # Django AppConfig
├── models.py             # Your models
├── views.py              # Your views
├── urls.py               # URL routing
├── hooks.py              # Custom hooks
├── templates/
│   └── myplugin/
│       └── component.html
└── static/
    └── myplugin/
        └── styles.css
```

### Registering a Plugin

```python
# projects/lms/plugins/myplugin/apps.py
from django.apps import AppConfig

class MyPluginConfig(AppConfig):
    name = "plugins.myplugin"
    label = "myplugin"

    def ready(self):
        # Register template include paths
        from django_fusion.comp.registry import register_include_path
        register_include_path("myplugin/component.html")
```

---

## 6. Per-Project Patterns

### LMS Customization Hotspots

| Area | Method | Files |
|------|--------|-------|
| Course cards | Template Override | `templates/components/course_card.html` |
| Course details | Template Override | `templates/courses/details/` |
| Certification PDF | Hook Extension | `plugins/certs/hooks.py` |
| Enrollment workflow | Hook Extension | `plugins/courses/hooks.py` |
| Blog layout | Template Override | `templates/blog/components/` |
| Auth pages | Template Override | `templates/auth/` |

### Portfolio Customization Hotspots

| Area | Method | Files |
|------|--------|-------|
| Resume templates | Template Override | `templates/VResume/resume_*.html` |
| Section types | Model Extension | `VResume/www/resume/models.py` |
| PDF styling | Hook Extension | `VResume/plugins/export/hooks.py` |
| Theme colors | Config Override | `configs/settings.yml` |

### Cypercloud Customization Hotspots

| Area | Method | Files |
|------|--------|-------|
| Chat UI | Template Override | `templates/components/chat/` |
| AI models | Config Override | `configs/settings.yml` |
| Prompt templates | Config Override | `configs/settings.yml` |
| Streaming behavior | Config Override | `configs/settings.yml` |

### POS Customization Hotspots

| Area | Method | Files |
|------|--------|-------|
| Receipt template | Template Override | `pos-client/src/components/Receipt.vue` |
| Store settings | Config Override | `sidecar/settings.py` |
| Tax rules | Hook Extension | Rust `tax_calculator` trait |
| Payment methods | Hook Extension | Rust `PaymentProvider` trait |

---

## Related

| Topic | Path |
|-------|------|
| Customization tags | [`README.md`](README.md) |
| Best practices | [`../guides/08-best-practices.md`](../guides/08-best-practices.md) |
| Clone a site | [`../guides/06-clone-site.md`](../guides/06-clone-site.md) |
| Repo overview | [`../repo-overview.md`](../repo-overview.md) |
