# Error Fixes — lms-demo & ctc-research (2026-06-09)

All fixes applied to the running Docker containers. Both `lms-demo-website`
and `ctc-research-website` are healthy after restart.

---

## 1. `ModuleNotFoundError: No module named 'www.core.handlers.models.forms'`

**Container:** lms-demo, ctc-research  
**Symptom:** Workers failed to boot (exit code 3), server crashed on startup.  
**Root cause:** `www/core/handlers/models/__init__.py` contained wildcard imports
for `forms` and `snippets` sub-modules that do not exist in either project.

**Fix:**  
`lms-demo/www/core/handlers/models/__init__.py`  
`ctc-research/www/core/handlers/models/__init__.py`

Removed `from .forms import *` and (for ctc-research) `from .snippets import *`.
Kept only the modules that actually exist: `manage`, `profiles`, `tags`,
`example_tagged_model`, and (lms-demo only) `snippets`.

---

## 2. `TemplateSyntaxError: Invalid block tag 'comp'`

**Container:** lms-demo, ctc-research  
**Symptom:** `Internal Server Error: /` — every front-end page failed.  
**Root cause:** Templates use `{% comp %}` from `django_fusion.comp.templatetags.components`
but that library was never discoverable — `django_fusion.comp` was not in
`INSTALLED_APPS` and not in `TEMPLATES.builtins`.

**Fix:**  
`configs/base/templates.py`

Added `"django_fusion.comp.templatetags.components"` to `_TEMPLATE_BUILTINS`,
guarded by `importlib.util.find_spec`. This matches the constant
`COMPONENTS_BUILTINS` already defined in `django_fusion`'s own `conf.py`.
The `{% comp %}` tag now works in all templates project-wide without any
`{% load %}` directive.

Also cleaned `ctc-research/templates/base_page.html` — removed stale
`{% load components %}` that was added as a workaround.

---

## 3. `TemplateDoesNotExist: landing/skeleton.html`

**Container:** lms-demo, ctc-research  
**Symptom:** Front-end pages (`/`, `/team-page/`, `/contact-page/`, `/all-courses/`, Arabic routes) returned 500.  
**Root cause:** `base_page.html` extends `landing/skeleton.html` but the file
lives at `assets/templates/layout/landing/skeleton.html`. The `layout/`
subdirectory was not in `TEMPLATES_DIRS`, so Django couldn't find it.

**Fix:**  
`configs/base/templates.py`

Added two extra template directories:
```python
BASE_DIR / "assets" / "templates" / "layout",
BASE_DIR.parent / "assets" / "templates" / "layout",
```
Both the per-site and workspace-level `layout/` directories are now
searchable, resolving `landing/skeleton.html`, `auth/skeleton.html`,
`learning/skeleton.html`, etc.

---

## 4. `ValueError / ImproperlyConfigured: Cannot use SnippetChooserBlock with non-snippet model Organization`

**Container:** lms-demo, ctc-research  
**Symptom:** `Internal Server Error: /admin/pages/9/edit/` and Wagtail block
serialization errors on any page that used the `clients` StreamField section.  
**Root cause:** `HomePage` and `AboutPage` both use
`SnippetChooserBlock("handlers.Organization")` but `Organization` was never
decorated with `@register_snippet`, so Wagtail refused to serialize it.

**Fix:**  
`lms-demo/www/core/handlers/models/manage/company.py`  
`ctc-research/www/core/handlers/models/manage/company.py`

Uncommented `@register_snippet` on the `Organization` class and added the
required import:
```python
from wagtail.snippets.models import register_snippet

@register_snippet
class Organization(DefaultBase, ClusterableModel):
    ...
```

---

## 5. `NoReverseMatch: Reverse for 'reorder' with arguments '(999999,)'`

**Container:** lms-demo  
**Symptom:** `Internal Server Error: /admin/snippets/lms/module/`  
**Root cause:** `Module` inherited from `wagtail.models.Orderable`, which adds
Wagtail's drag-to-reorder feature via an integer `sort_order` field and a
`reorder/<pk>/` URL. However `Module` uses a UUID primary key — Wagtail's
reorder view generates a test URL with the sentinel integer `999999`, which
fails the UUID regex pattern.

**Fix:**  
`lms-demo/plugins/lms/models/courses/detail.py`

Removed `Orderable` from `Module`'s base classes (it already has its own
`order = PositiveIntegerField` for manual ordering):
```python
# Before
class Module(DefaultBase, Orderable, ClusterableModel):

# After
class Module(DefaultBase, ClusterableModel):
```

Also added `ordering = ["order"]` to `ModuleSnippet` in `snippets/track.py`
so the list view still sorts by the `order` field.

---

## 6. Payment Snippets — `KeyError / AttributeError: Unable to lookup 'amount_display' / 'verified_badge' / 'enrollment_link'`

**Container:** lms-demo  
**Symptom:** `Internal Server Error` on `/admin/snippets/lms/paymenttransaction/`,
`/admin/snippets/lms/paymentrefund/`, `/admin/snippets/lms/paymentwebhooklog/`.  
**Root cause:** Old `list_display` entries (`amount_display`, `verified_badge`,
`enrollment_link`, `provider_display`, `transaction_link`, `created_at_display`,
`status_badge`) referenced methods defined on the ViewSet class — not on the
model. Wagtail's `label_for_field` only looks at the model, so it raised
`FieldDoesNotExist` for all of them.

**Fix:**  
`lms-demo/plugins/lms/snippets/payments.py` *(new file)*  
`lms-demo/plugins/lms/migrations/0002_payment_proxy_models.py` *(new migration)*  
`lms-demo/plugins/lms/snippets/__init__.py`  
`lms-demo/plugins/lms/wagtail_hooks.py`

Created three Django **proxy models** over `Enrollment` — one per admin view —
so each can be registered as its own Wagtail snippet without conflicting:

| Proxy model          | Filter                        | FA icon                              |
|----------------------|-------------------------------|--------------------------------------|
| `PaymentTransaction` | all enrollments               | `solid/credit-card.svg`              |
| `PaymentRefund`      | `payment_status` in refunded/failed | `solid/rotate-left.svg`       |
| `PaymentWebhookLog`  | `payment_status = pending`    | `solid/bell.svg`                     |

All `list_display` entries are now actual model fields — no ViewSet methods.

Added a `PaymentSnippetGroup` to `wagtail_hooks.py` with:
```python
menu_icon = "wagtailfontawesomesvg/solid/wallet.svg"
```

---

## 7. SECRET_KEY — Auto-generation & removal from `.env` files

**Container:** lms-demo, ctc-research  
**Symptom:** `CRITICAL startup: SECRET_KEY is only 47 characters long` on every
worker boot.  
**Root cause:** `DJANGO_SECRET_KEY` was hard-coded in `.env` files with values
shorter than the 50-character minimum enforced by `startup.py`.

**Fix:**  
`configs/settings/conf.py`

Added a `_generate_secret_key()` helper using `secrets.choice` over Django's
own character set, and set it as the `default_factory` for `DJANGO_SECRET_KEY`:
```python
def _generate_secret_key(length: int = 64) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return "".join(secrets.choice(alphabet) for _ in range(length))

DJANGO_SECRET_KEY: str = Field(
    default_factory=_generate_secret_key,
    description="Django secret key — set via DJANGO_SECRET_KEY env var or auto-generated",
)
```

Removed `DJANGO_SECRET_KEY` from:
- `ctc-research/.env`
- `lms-demo/.env`
- `.env` (workspace root)

If `DJANGO_SECRET_KEY` is not set in the environment, a cryptographically
secure 64-character key is generated at startup. To persist it across
container restarts, set it explicitly in the site `.env` file using:
```bash
python -c "
import secrets, string
a = string.ascii_letters + string.digits + '!@#\$%^&*(-_=+)'
print('DJANGO_SECRET_KEY=' + ''.join(secrets.choice(a) for _ in range(64)))
"
```

---

## 8. `Makefile webpack-validate` — Wrong `bundles.json` path

**Container:** lms-demo  
**Symptom:** Server failed to start with `make: Error 1` before gunicorn
even launched.  
**Root cause:** The `webpack-validate` Makefile target checked for
`$(pwd)/assets/bundles/bundles.json` but Webpack writes stats to
`assets/bundles/$(SITE_NAME)/bundles.json`.

**Fix:**  
`lms-demo/Makefile`  
`ctc-research/Makefile`

```makefile
# Before
@BUNDLES_JSON=$$(pwd)/assets/bundles/bundles.json; \

# After
@BUNDLES_JSON=$$(pwd)/assets/bundles/$(SITE_NAME)/bundles.json; \
```

---

## Files changed

| File | Change |
|------|--------|
| `configs/base/templates.py` | Added `layout/` to `TEMPLATES_DIRS`; added `django_fusion.comp` builtin |
| `configs/settings/conf.py` | `_generate_secret_key()` helper; auto-generate `DJANGO_SECRET_KEY` |
| `configs/base/apps.py` | Added `www.core.handlers.apps.AccountsConfig` to `LOCAL_APPS` |
| `ctc-research/.env` | Removed `DJANGO_SECRET_KEY` |
| `lms-demo/.env` | Removed `DJANGO_SECRET_KEY` |
| `.env` | Removed `DJANGO_SECRET_KEY` |
| `ctc-research/templates/base_page.html` | Cleaned stale `{% load components %}` |
| `ctc-research/www/core/handlers/models/__init__.py` | Removed missing imports |
| `ctc-research/www/core/handlers/models/manage/company.py` | `@register_snippet` on `Organization` |
| `ctc-research/Makefile` | Fixed `webpack-validate` path |
| `lms-demo/www/core/handlers/models/__init__.py` | Removed missing `forms` import |
| `lms-demo/www/core/handlers/models/manage/company.py` | `@register_snippet` on `Organization` |
| `lms-demo/plugins/lms/models/courses/detail.py` | Removed `Orderable` from `Module` |
| `lms-demo/plugins/lms/snippets/payments.py` | New — proxy models + ViewSets with FA icons |
| `lms-demo/plugins/lms/migrations/0002_payment_proxy_models.py` | New — proxy model migration |
| `lms-demo/plugins/lms/snippets/__init__.py` | Added `from .payments import *` |
| `lms-demo/plugins/lms/snippets/track.py` | Added `ordering` to `ModuleSnippet` |
| `lms-demo/plugins/lms/wagtail_hooks.py` | Added `PaymentSnippetGroup` with FA wallet icon; enabled `EnrollmentSnippetGroup` |
| `lms-demo/Makefile` | Fixed `webpack-validate` path |
