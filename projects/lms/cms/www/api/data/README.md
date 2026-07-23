# Data API Module (`www.api.data`)

High-performance domain API handlers backed by django-bolt and Django ORM.

This package provides modular bolt-style handler functions organised by domain.
It extends the core endpoints defined in [`apis.py`](../../apis.py) with additional
CRUD and business-logic endpoints that previously lived in DRF viewsets.

---

## Architecture

```
                     ┌──────────────┐
                     │  apis.py     │  ← Core endpoints (health, auth, courses,
                     │  (BoltAPI)   │     blog, events, site settings, LMS)
                     └──────┬───────┘
                            │ register_all_handlers()
                     ┌──────▼───────┐
                     │  data/       │  ← Domain extras (this package)
                     │  (router.py) │
                     └──┬───┬───┬──┘
          ┌─────────────┘   │   └─────────────┐
     ┌────▼────┐      ┌────▼────┐      ┌──────▼──┐
     │ auth.py │      │ shop.py │      │ blog.py │  …
     └─────────┘      └─────────┘      └─────────┘
```

**Key principle:** The core `apis.py` registers essential endpoints directly.
This `data/` package registers **additional** endpoints that extend the API
surface without duplicating what already exists.

---

## Module overview

| Module | File | Prefix | Auth? | Description |
|--------|------|--------|-------|-------------|
| Auth | `auth.py` | `/auth/profile` | ✅ | Profile CRUD, password change/reset |
| Courses | `courses.py` | `/courses/featured`, `/courses/<pk>/detail` | ❌ | Featured courses, full detail with curriculum |
| Students | `students.py` | `/students/<pk>/dashboard`, `/students/<pk>/enrollments`, `/enrollments` | ✅ | Dashboard stats, enrollment management, progress |
| Instructors | `instructors.py` | `/instructors` | Mixed | List, detail, dashboard stats, courses, reviews |
| Blog | `blog.py` | `/blog/<pk>`, `/blog/featured`, `/blog/<pk>/related`, `/blog/categories` | ❌ | Post detail, featured, related, categories |
| Shop | `shop.py` | `/shop/products`, `/shop/cart`, `/shop/orders` | Mixed | Products list/detail, cart management, checkout |
| Events | `events.py` | `/events/<pk>`, `/events/upcoming`, `/events/register` | ❌ | Event detail, upcoming filter, registration |
| Contact | `contact.py` | `/contact/inquiries` | ✅ | Admin inquiry listing, mark-as-read |
| Helpers | `helpers.py` | — | — | Shared utilities (pagination, auth helpers, etc.) |
| Router | `router.py` | — | — | Aggregates all modules via `register_all_handlers()` |

---

## Adding a new endpoint

### 1. Add the handler function

Each module exposes a `register_handlers(bolt)` function. Add your endpoint
inside it using the `@bolt.get()`, `@bolt.post()`, etc. decorators:

```python
# www/api/data/my_domain.py

import logging
from www.auth import TokenAuthBackend, auth_required
from www.api.data.helpers import paginate_queryset, parse_body, get_current_user

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    @bolt.get("/my-domain", auth=[TokenAuthBackend()])
    def list_items(request):
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401
        return {"status": "success", "data": [...]}
```

### 2. Register in the router

Add your import and call to `www/api/data/router.py`:

```python
from www.api.data.my_domain import register_handlers as register_my_domain
# ...
register_my_domain(bolt)
```

That's it — the endpoint is live at `/apis/my-domain`.

---

## Handler conventions

### Return values

Handlers must return **dict** (→ 200 JSON) or **tuple of (dict, int)** (→ custom status):

```python
return {"status": "success", "data": item}           # 200
return {"status": "error", "message": "..."}, 404     # 404
return {"status": "success", "data": item}, 201       # 201
```

### Authentication

Use `**auth_required()` as decorator kwargs for endpoints that need a valid token:

```python
@bolt.get("/protected", **auth_required())
def protected_endpoint(request):
    user = get_current_user(request)
    ...
```

For endpoints that should accept both authenticated and anonymous users, pass
`auth=[TokenAuthBackend()]` to populate `request.user` when a valid token is present,
but still allow unauthenticated access.

### Shared helpers (`helpers.py`)

| Function | Purpose |
|----------|---------|
| `get_image_url(field)` | Extract absolute URL from a Wagtail/Django Image FileField |
| `get_user_display_name(user)` | Best-effort display name from User instance |
| `paginate_queryset(qs, request, default_per_page=20)` | Paginate a QuerySet/list using `page`/`per_page` query params |
| `parse_body(request)` | Parse JSON request body to dict (returns `{}` on failure) |
| `get_current_user(request)` | Safely resolve the current user from request |

---

## Relationship with `apis.py`

The file [`apis.py`](../../apis.py) creates the main `BoltAPI` instance and registers
**core endpoints** directly on it. The `data/` package hooks into the same instance
via `register_all_handlers(bolt)`:

```python
# apis.py (core)
bolt = BoltAPI(prefix="/apis")
# ... core endpoints registered directly ...

from www.api.data.router import register_all_handlers
register_all_handlers(bolt)   # ← data/ extras are added here
```

**Core endpoints** (in `apis.py`):
`/health`, `/auth/login`, `/auth/register`, `/auth/me`, `/auth/logout`,
`/auth/refresh`, `/contact/submit`, `/courses`, `/courses/<pk>`,
`/courses/categories`, `/blog`, `/events`, `/research/publications`,
`/research/team`, `/testimonials`, `/site/settings`, `/lms/features`,
`/lms/instructors`, `/lms/faq`, `/lms/dashboard`, `/lms/products`, `/lms/menu`

**Extras** (in this `data/` package):
`/auth/profile`, `/auth/change-password`, `/auth/password-reset`,
`/courses/featured`, `/courses/<pk>/detail`,
`/students/<pk>/dashboard`, `/students/<pk>/enrollments`,
`/enrollments`, `/enrollments/<pk>/progress`,
`/instructors`, `/instructors/<pk>`, `/instructors/<pk>/dashboard`,
`/instructors/<pk>/courses`, `/instructors/<pk>/reviews`, `/instructors/courses/<pk>` (DELETE),
`/blog/<pk>`, `/blog/featured`, `/blog/<pk>/related`, `/blog/categories`,
`/shop/products`, `/shop/products/<pk>`, `/shop/cart`, `/shop/cart/add`,
`/shop/orders`, `/shop/cart/checkout`,
`/events/<pk>`, `/events/upcoming`, `/events/register`,
`/contact/inquiries`, `/contact/inquiries/<pk>/mark-read`

---

## Legacy adapter (`www.api.data_adapter`)

The module `www.api.data_adapter` provides a `@bolt_view` decorator that bridges
bolt-style function views with traditional Django URL routing. This is used by
legacy view modules in `www/api/*.py` (e.g. `www/api/auth.py`, `www/api/shop.py`)
that were initially written as DRF views and converted via the decorator pattern.
New endpoints should be added directly as bolt handlers — not through the adapter.

---

## Testing

Test files live in [`tests/`](../../../tests/) with the naming convention
`test_data_*.py`. They use `TestClient` from `django_bolt.testing` with a
real `BoltAPI` instance:

```python
from django_bolt.testing import TestClient

def test_endpoint(test_api, auth_token):
    with TestClient(test_api) as client:
        resp = client.get("/apis/instructors")
        assert resp.status_code == 200
```

Run the full verification script:

```bash
cd projects/lms/cms
python tests/verify_endpoints.py
```
