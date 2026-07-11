# Integration Examples — DF-012

> Source of truth: distilled from `docs/COMPONENT_CASE_STUDIES.md`
> (22 components) and the COMPONENT_CASE_STUDIES *Form Sample* /
> *Component Sample* sections.

This doc walks through **one end-to-end feature** per example. Each is
*model → viewset/component → template → test*.

## Example 1 — Pricing table with search

A user clicks `/pricing/?tier=pro`. The page lists 25 plans with a
search box and a tier filter; HTMX swaps the list fragment.

### 1. The model

```python
# myapp/models.py
from django_fusion.core.models import TimeStampedModel
from django.db import models

class Plan(TimeStampedModel):
    name = models.CharField(max_length=80)
    tier = models.CharField(max_length=20, choices=[
        ("free", "Free"), ("pro", "Pro"), ("enterprise", "Enterprise"),
    ])
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self):
        return f"{self.name} ({self.tier})"
```

### 2. The viewset

```python
# myapp/views.py
from django_fusion.comp.routes import ModelViewset
from .models import Plan

class PlanViewset(ModelViewset):
    model = Plan
    template_name = "pricing/plan"   # resolves _list, _detail, _form
    paginate_by = 25
    fragment_name = "components.pricing.plan_list"
```

### 3. The list template

```django
{# myapp/templates/pricing/plan_list.html #}
{% load components %}
<div id="plan-list" class="plan-list">
  {{ block.super }}
</div>

{% comp "components/search.html"
    search_query=search_query
    hx_target="#plan-list"
    hx_get=request.path
    extra_filters={"tier": request.GET.tier|default:""} / %}

{% comp "components/table.html"
    headers=table_headers
    rows=table_data
    hx_target="#plan-list" / %}
```

### 4. The search component kwargs

From the view, populate `search_query` and `extra_filters` in
`get_context_data`:

```python
class PlanViewset(ModelViewset):
    model = Plan
    fragment_name = "components.pricing.plan_list"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_query"] = self.request.GET.get("q", "")
        ctx["extra_filters"] = {"tier": self.request.GET.get("tier", "")}
        return ctx
```

### 5. The test

```python
# myapp/tests/test_pricing_list.py
import pytest
from django.test import Client

@pytest.mark.django_db
def test_plan_list_renders(client):
    Plan.objects.create(name="Solo", tier="free", price_monthly="0")
    Plan.objects.create(name="Team", tier="pro", price_monthly="19.99")
    response = client.get("/pricing/")
    assert response.status_code == 200
    assert b"Solo" in response.content
    assert b"Team" in response.content

@pytest.mark.django_db
def test_plan_list_filters_by_tier(client):
    Plan.objects.create(name="Free Plan", tier="free", price_monthly="0")
    Plan.objects.create(name="Pro Plan", tier="pro", price_monthly="19.99")
    response = client.get("/pricing/?tier=pro")
    assert b"Pro Plan" in response.content
    assert b"Free Plan" not in response.content
```

## Example 2 — Inline edit modal (HTMX fragment-to-fragment)

A row in a user list has an *Edit* button that, when clicked, swaps
the row's `<td>` with a form. Save → swap back to read-only mode.

### Models

```python
class User(TimeStampedModel):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
```

### Viewset

```python
from django_fusion.comp.routes import ModelViewset, ViewsetMeta
from django.contrib.auth import get_user_model

class UserViewset(ModelViewset):
    model = get_user_model()
    template_name = "users/user"
    fragment_name = "components.users.user_row"
```

### Row template

```django
{# components/users/user_row.html #}
{% load components %}
<tr id="user-{{ user.id }}" class="user-row {{ attrs }}">
  {% if editing %}
    <td colspan="4">
      {% comp "components/form/form.html"
          form=form
          hx_put="/users/{{ user.id }}/"
          hx_target="#user-{{ user.id }}"
          hx_swap="outerHTML"
          submit_label="Save" / %}
    </td>
  {% else %}
    <td>{{ user.email }}</td>
    <td>{{ user.full_name }}</td>
    <td>{% if user.is_active %}active{% else %}inactive{% endif %}</td>
    <td>
      <button hx-get="/users/{{ user.id }}/?edit=1"
              hx-target="#user-{{ user.id }}"
              hx-swap="outerHTML"
              class="btn btn--sm btn--outline-primary">Edit</button>
    </td>
  {% endif %}
</tr>
```

### Test

```python
@pytest.mark.django_db
def test_user_row_renders_in_read_mode(client):
    user = User.objects.create(email="a@b.com", full_name="Alice")
    response = client.get(f"/users/{user.id}/?edit=0")
    assert b"Alice" in response.content
    assert b"name=\"email\"" not in response.content

@pytest.mark.django_db
def test_user_row_renders_in_edit_mode(client):
    user = User.objects.create(email="a@b.com", full_name="Alice")
    response = client.get(f"/users/{user.id}/?edit=1")
    assert b"name=\"email\"" in response.content
```

## Example 3 — Wagtail snippet viewset with `export_to_csv`

```python
# myapp/wagtail_hooks.py
from django_fusion.wagtail.viewsets import BaseSnippetViewSet
from .models import Subscriber

class SubscriberViewSet(BaseSnippetViewSet):
    model = Subscriber
    list_display = ["email", "subscribed_at", "is_confirmed"]
    duplicate_enabled = False
    export_csv_fields = ["email", "subscribed_at", "is_confirmed"]
```

Then visit `/admin/snippets/myapp/subscriber/` and a `Download CSV`
button appears for any selected rows.

## Example 4 — Cached manager on a hot query

```python
# myapp/models.py
from django_fusion.core.managers import CachedManager

class Article(TimeStampedModel):
    title = models.CharField(max_length=160)
    body = models.TextField()
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    objects = CachedManager(cache_attr="published_articles", timeout=60)

    class Meta:
        ordering = ["-published_at"]
```

The manager caches `Article.objects.published()` results for 60 s
across all requests, with invalidation on signal when an Article is
saved.

> Remark: `CachedManager.cache_attr` is the registry key — use a
> stable namespace, not a hash of the query, so cache hits across
> requests stay cheap.

## Pattern: success acknowledgement without a redirect

```django
{% comp "components/form/form.html"
    form=form
    hx_post=request.path
    hx_target="#contact-form"
    hx_swap="outerHTML"
    submit_label="Send message"
    field_success="email"
    success_message="Thanks — we'll be in touch!" / %}
```

After save, the same form re-renders with a `success_message` next
to the email field. No redirect, no flicker, no second page load.

## Where to read more

- [DF-005 Routing](./05-routing.md) — `ModelViewset` in detail
- [DF-006 Forms & tables](./06-forms-and-tables.md) — same page reference, deeper
- [DF-010 Wagtail](./10-wagtail-integration.md) — snippet viewsets
- [DF-011 Best practices](./11-best-practices.md) — when to reach for each tool
