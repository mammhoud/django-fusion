# libs — Use Cases & Package Guide

## Package Structure

```
libs/
├── django-osoul/   django_osoul   Foundation layer — Django + stdlib only
├── django-rseal/   django_rseal   Automation layer — email, tasks, pipelines, AI
├── nawaai/         craftsai       Standalone AI/MCP toolkit — no Django required
└── django-grep/    django_grep    Centralized testing framework
```

### Dependency Graph

```
stdlib / Django
    └── django-osoul          (foundation — no app-layer deps)
            └── django-rseal  (automation — wagtail, celery, faker, …)
                    └── nawaai (optional AI backend for newsletter)

nawaai                        (standalone — no Django)

django-grep                   (testing — depends on osoul + rseal)
```

---

## django-osoul — Foundation Layer

**Rule:** `django_osoul` must never import from `wagtail`, `celery`,
`django_q`, `openai`, `anthropic`, `faker`, `mcp`, or `django_rseal`.

### Use cases

#### Abstract model bases

```python
from django_osoul.models.base import BaseModel, TimeStampedModel, UUIDModel

class Article(TimeStampedModel):
    title = models.CharField(max_length=255)
    # created_at, updated_at added automatically
```

#### Soft delete

```python
from django_osoul.models.mixins import SoftDeleteMixin, TimestampedModel

class Order(TimestampedModel, SoftDeleteMixin):
    ...

order.soft_delete()   # sets is_deleted=True, records deleted_at
order.restore()       # clears is_deleted
```

#### UUID primary key

```python
from django_osoul.models.mixins import UUIDPrimaryKeyModel

class Subscription(UUIDPrimaryKeyModel):
    ...
# subscription.pk → UUID4
```

#### Audit trail

```python
from django_osoul.models.mixins import AuditMixin, TimestampedModel

class Invoice(TimestampedModel, AuditMixin):
    ...
# invoice.created_by, invoice.updated_by → FK to auth.User
```

#### Validators

```python
from django_osoul.utils.validators import (
    validate_email_format,
    validate_phone_number,
    validate_url,
)

validate_email_format("user@example.com")  # True
validate_phone_number("+1-555-123-4567")   # True
```

#### Text utilities

```python
from django_osoul.utils.text import slugify_unique, truncate_words, strip_html_tags

slug = slugify_unique(Article, "My Article Title")
short = truncate_words("Long text here…", num_words=10)
plain = strip_html_tags("<p>Hello <b>World</b></p>")
```

#### JSON response helpers

```python
from django_osoul.utils.responses import success_response, error_response

def my_view(request):
    return success_response({"id": 1}, "Created", status=201)
```

#### View mixins

```python
from django_osoul.views.mixins import AjaxResponseMixin, MessageMixin

class ItemView(AjaxResponseMixin, View):
    def get(self, request):
        if self.is_ajax():
            return self.render_to_json_response({"items": []})
```

#### UI components (comp/)

```python
# In templates — components live in django_osoul.comp
{% load osoul_tags %}
{% component "card.html" title="Hello" %}
```

#### Context processors

```python
# settings.py
TEMPLATES[0]["OPTIONS"]["context_processors"] += [
    "django_osoul.contrib.context.auth.auth_context",
    "django_osoul.contrib.context.htmx.htmx_context",
    "django_osoul.contrib.context.languages.languages_context",
]
```

---

## django-rseal — Automation Layer

Depends on: `django_osoul`, `wagtail`, `celery`, `faker`, `toposort`.
Optional: `nawaai` (for AI features), `mcp`.

### Use cases

#### Email sending

```python
from django_rseal.services.email_service import EmailService

svc = EmailService()
svc.send(
    recipient="user@example.com",
    subject="Welcome",
    template_name="emails/welcome.html",
    context={"name": "Alice"},
)
```

#### Template renderer

```python
from django_rseal.renderer import TemplateRenderer

renderer = TemplateRenderer()
html  = renderer.render("emails/invitation.html", {"name": "Alice"})
email = renderer.render_email(
    "emails/invitation.html",
    context={"name": "Alice"},
    subject="You're invited",
)
# email["html"], email["text"], email["subject"]
return renderer.render_to_response("auth/login.html", {"form": form}, request)
```

#### Newsletter AI enhancement (optional nawaai)

```python
from django_rseal.newsletter import NewsletterEnhancer, EmailDesigner

enhancer = NewsletterEnhancer()
subject  = enhancer.enhance_subject("Monthly update")
body     = enhancer.enhance_body(html_body, tone="friendly")
variants = enhancer.generate_subject_variants("Black Friday", count=3)

designer = EmailDesigner()
branded  = designer.apply_brand_styles(html, {
    "primary_color": "#2563eb",
    "company_name":  "Acme Corp",
    "logo_url":      "https://example.com/logo.png",
})
```

#### Database seeding (Django models)

```python
from faker import Faker
from django_rseal.seeder import Seeder

seeder = Seeder(Faker())
seeder.add_entity(MyModel, 50)
inserted = seeder.execute()
```

#### Background tasks (Celery)

```python
from django_rseal.tasks.celery import send_email_task

send_email_task.delay(log_id=42, recipient="user@example.com")
```

---

## nawaai — Standalone AI/MCP Toolkit

**No Django required.**  Install extras as needed:

```bash
pip install nawaai[openai]     # OpenAI support
pip install nawaai[anthropic]  # Claude support
pip install nawaai[mcp]        # MCP server support
```

### Use cases

#### AI text generation

```python
from craftsai.ai.integrations import AIIntegrationRegistry

ai = AIIntegrationRegistry.get("openai")
response = ai.generate("Summarise this article: …")

for chunk in ai.stream("Write a poem about Python"):
    print(chunk, end="", flush=True)
```

#### MCP server

```python
from craftsai.mcp.server import MCPServer

server = MCPServer(name="my-tools", version="1.0.0")

@server.tool("search")
def search(query: str) -> list:
    return []

server.run(host="localhost", port=8765)
```

#### Fake data generation (no ORM)

```python
from faker import Faker
from craftsai.seeder import SimpleSeeder

seeder = SimpleSeeder(Faker())
records = seeder.generate(count=10, schema={
    "name":  "name",
    "email": "email",
    "score": lambda f: f.random_int(0, 100),
})
```

#### Spec task orchestration (CLI)

```bash
craftsai --help
craftsai run --spec .kiro/specs/my-feature/tasks.md
```

---

## django-grep — Testing Framework

### Base test cases

```python
from django_grep.tests import BaseTestCase, BaseAPITestCase

class MyTest(BaseAPITestCase):
    def test_endpoint(self):
        self.login()
        response = self.get_json("/api/items/")
        self.assertJSONSuccess(response)
```

### pytest fixtures (auto-registered via pytest11 entry point)

```python
def test_profile(test_user, authenticated_client):
    response = authenticated_client.get("/api/profile/")
    assert response.status_code == 200
```

### Email assertions

```python
from django_grep.tests import AssertEmailMixin

class InviteTest(AssertEmailMixin, BaseTestCase):
    def test_sends_invite(self):
        send_invitation("user@example.com")
        self.assertEmailSent("user@example.com", subject="You're invited")
```

### Model factories

```python
from django_grep.tests.factories import ModelFactory

article = ModelFactory.create(Article, title="Custom Title")
articles = ModelFactory.create_batch(Article, 5)
```

---

## Integration Example

All four packages working together in a typical Django project:

```python
# models.py — use osoul base classes
from django_osoul.models.base import TimeStampedModel
from django_osoul.models.mixins import SoftDeleteMixin

class Newsletter(TimeStampedModel, SoftDeleteMixin):
    subject = models.CharField(max_length=255)
    body = models.TextField()


# views.py — use rseal email service
from django_rseal.services.email_service import EmailService
from django_rseal.newsletter import NewsletterEnhancer

def send_newsletter(newsletter):
    enhancer = NewsletterEnhancer()
    subject = enhancer.enhance_subject(newsletter.subject)
    svc = EmailService()
    svc.send(
        recipient="subscribers@example.com",
        subject=subject,
        template_name="emails/newsletter.html",
        context={"body": newsletter.body},
    )


# tests/test_newsletter.py — use django-grep testing framework
from django_grep.tests import BaseTestCase, AssertEmailMixin
from django_grep.tests.factories import ModelFactory

class NewsletterTest(AssertEmailMixin, BaseTestCase):
    def test_send_newsletter(self):
        newsletter = ModelFactory.create(Newsletter, subject="Hello")
        send_newsletter(newsletter)
        self.assertEmailSent("subscribers@example.com")


# standalone_script.py — use nawaai without Django
from craftsai.ai.integrations import AIIntegrationRegistry

ai = AIIntegrationRegistry.get("openai")
improved = ai.generate(f"Improve this subject line: {subject}")
```

---

## Migration Guide

If you were using the old `django_grep.*` imports, migrate to the canonical locations:

| Old import | New import |
|-----------|-----------|
| `django_grep.utils.text` | `django_osoul.utils.text` |
| `django_grep.utils.validators` | `django_osoul.utils.validators` |
| `django_grep.models.base` | `django_osoul.models.base` |
| `django_grep.models.mixins` | `django_osoul.models.mixins` |
| `django_grep.views.mixins` | `django_osoul.views.mixins` |
| `django_grep.comp` | `django_osoul.comp` |
| `django_grep.pipelines` | `django_rseal.pipelines` |
| `django_grep.email_tools` | `django_rseal.email_tools` |
| `django_grep.mcp_designer` | `django_rseal.mcp_designer` |
| `django_grep.contrib.debug_tools` | `django_rseal.contrib.debug_tools` |
| `django_seed.*` | `craftsai.*` (standalone) or `django_rseal.seeder` (Django) |
| `craftsai.*` | `craftsai.*` (unchanged — nawaai package, same module name) |

The old `django_grep.*` shim imports still work but emit a `DeprecationWarning`.
Update your imports at your own pace.

---

## Settings Reference

| Setting | Package | Default | Description |
|---------|---------|---------|-------------|
| `RSEAL_AI_BACKEND` | django-rseal | `"rseal"` | AI backend for newsletter: `"rseal"` or `"nawaai"` |
| `RSEAL_TEMPLATE_RENDERER` | django-rseal | `None` | Dotted path to custom `TemplateRenderer` subclass |
| `PROFILE_MODEL` | django-rseal | — | Dotted path to the site's profile model |
