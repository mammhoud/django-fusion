# django-fusion Enhancement Plan & Shared-Code Consolidation

Status: ✅ Applied (rename + consolidation) · 🔮 Proposed (enhancements)

Companion audit: [`dead-code-audit-cms-lms.md`](./dead-code-audit-cms-lms.md)

---

## 1. What was consolidated into django-fusion

### 1.1 `django_fusion/contrib/api.py` (NEW)

The three tiny REST views that were copy-pasted into **both** `cms-fusion` and
`precis-lms` now live in django-fusion:

| Project copy (deleted) | django-fusion replacement |
|---|---|
| `core/api/fusion_health.py` → `fusion_health()` | `django_fusion.contrib.api.health` |
| `core/api/fusion_branding.py` → `fusion_branding()` | `django_fusion.contrib.api.branding` |
| `core/api/fusion_layouts.py` → `fusion_layouts()` (cms only) | `django_fusion.contrib.api.layouts` |

Per-site branding is configured through env vars (`FUSION_SITE_NAME`,
`FUSION_PRIMARY_COLOR`, ...) or the `FusionBranding` Wagtail snippet — the lib
view reads them directly, so project wiring is one line per view:

```python
# projects/<site>/backend/apps/core/api/urls.py
from django_fusion.contrib.api import branding, health, layouts

urlpatterns = [
    path("health/", health, name="health"),
    path("branding/", branding, name="branding"),
    path("layouts/", layouts, name="layouts"),  # cms only
]
```

### 1.2 Fusion-prefix rename (methods/variables — settings untouched)

Removed the redundant `fusion_` prefix from project-level **methods and
variables** (settings/config keys and the `fusion_render_first` wire contract
were deliberately left alone):

| Old | New | Files |
|---|---|---|
| `fusion_health` / `fusion_health_checker` | `health` / `health_checker` | moved to lib |
| `fusion_branding` | `branding` | moved to lib |
| `fusion_layouts` | `layouts` | moved to lib |
| `fusion_admin_css` | `admin_css` | `apps/pages/pages/wagtail_hooks.py` (both sites) |
| `fusion_before_serve` | `before_serve` | `apps/pages/pages/wagtail_hooks.py` (both sites) |
| `Page._fusion_search_patched` | `Page._search_patched` | `apps/domain/apps.py` (both sites) |
| `Token.from_django_fusion_pattern()` | `Token.create_token()` | `apps/content/models/others.py` (both sites) |
| URL `/api/fusion/health` `/api/fusion/branding` | `/api/health` `/api/branding` | lms `core/api/urls.py` + frontend `api-client.ts` |

**Kept as-is (settings / wire contracts / CLI):** `fusion_render_first` (model
field, JSON key, sessionStorage key, query param), `FUSION_*` env/settings keys,
`FUSION_SITE_NAME`, `FUSION_LAYOUTS`, all django-fusion library API names
(`fusion_json_response`, `fusion_response`, `FusionSessionChecker`, …), the
`fusion_pages` app label (migration/FK integrity), and the documented management
commands `load_fusion_fixtures` / `validate_fusion_fixtures` (see
`docs/guides/fixture-loading.md`).

### 1.3 Deleted dead/duplicated code

- **lms `core/api/` bolt-era leftovers** (all unreferenced — only `urls.py` is
  wired; `www/urls.py` includes `apps.core.api.urls`):
  `bolt_apis.py`, `data_adapter.py`, `pages.py`, `blog.py`, `courses.py`,
  `products.py`.  The canonical endpoints live in the app-specific
  `apps/pages/*/api.py` modules; `fusion_response` is imported from
  `django_fusion.routes` (same as cms).  cms had already deleted these files.
- Project-local `fusion_health.py` / `fusion_branding.py` / `fusion_layouts.py`
  (now provided by the lib).
- lms `tests/test_api_smoke.py` updated to the renamed `/api/health/` and
  `/api/branding/` paths.

---

## 2. Enhancement recommendations

### 2.1 Base models for People / Organization 🔮

**Already in the lib:** `models.base` (`BaseModel`, `TimeStampedModel`,
`UUIDModel`, `AuditableBaseModel`), `models.default` (`DefaultBase`,
`EnhancedBase`, `ContentBase`, `TaggableBase`, `TemplateRenderMixin`),
`models.model_cache.ModelCacheMixin`, `models.tags` (`BaseTagCategory`,
`BaseTag`, `TagRelationship`), `models.datatoken`, `models.email`, `models.auth`
(`UserRole`, `Role`).

**Gap — no Person / Organization domain models.** Both sites carry near-identical
`apps/domain/models/*` (banner, certification, contacts, coupon, enums,
locations, newsletter, settings, users, workspace) and an `apps/pages/accounts`
people module (`PersonTag`, `TaggedPerson`, profiles, manage views). This is the
biggest duplication left.

**Recommended lib additions (abstract + concrete, all swappable):**

1. **`django_fusion.models.people`** — `AbstractPerson` (name, avatar, bio,
   contact email/phone, roles M2M, `display_name`), `AbstractOrganization`
   (name, slug, logo, website, members M2M), `AbstractTeamMembership`
   (person FK, organization FK, role, joined/left dates), plus `Person`,
   `Organization`, `TeamMembership` concrete versions under a single
   `people` app label. Include Wagtail `index.Indexed` + `ClusterableModel`
   mixins so sites get search & inline panels for free.
2. **`django_fusion.models.workspace`** — promote the current
   `Workspace(DefaultBase)` used by both sites into the lib.
3. **`django_fusion.models.settings` / `newsletter` / `coupon` / `certification`** —
   these four `domain` sub-models are byte-identical across sites → promote the
   *pure* ones (no site FK) to the lib; keep site-scoped variants as thin
   subclasses.
4. **`django_fusion.models.tags.TaggedPerson` + `PersonTagCategory`** already exist;
   finish wiring them so sites no longer define their own `tags.py` wrappers.

**How to use:** sites subclass the abstract bases and add site-only fields:

```python
from django_fusion.models.people import AbstractPerson

class Instructor(AbstractPerson):
    bio = RichTextField(blank=True)
    panels = AbstractPerson.panels + [FieldPanel("bio")]
```

### 2.2 Base views 🔮

**Already in the lib:** `core/views/mixins.py`, `comp.generic` (CRUD CBVs),
`site.interface` (`PageHandler`, `ComponentViews`), `fragments/generic`.

**Recommendations:**

1. **`django_fusion.core.views.api`** — a small `fusion_json`/`json_view`
   decorator + `ApiView` base that standardizes the
   `fusion_json_response({...}, status=...)` envelope (the pattern now used in
   `contrib/api.py` and every `apps/pages/*/api.py`). This kills the last reason
   sites hand-roll `@bolt_view`-style adapters.
2. **`LayoutViewMixin`** — page views already resolve
   `effective_layout` / `effective_fragment_name`; extract that into a mixin so
   `FusionContentPageView`/`FusionHomePageView` (duplicated in both sites'
   `apps/pages/pages/components.py`) shrink to a single class.
3. **`health`/`branding`/`layouts` as `ApiView` subclasses** so sites can add
   authentication/permission hooks without forking the lib views.

### 2.3 Fusion adapter 🔮

`data_adapter.py` (lms) — the `bolt_view` decorator + local `fusion_response`
copy — was deleted this session. `fusion_response`/`fusion_json_response` from
`django_fusion.routes` are now the single source of truth.

**Recommendations:**

1. Add a **`django_fusion.contrib.api.adapters`** module with a modern
   `json_view` decorator (returns `(data, status)` tuples → `JsonResponse`,
   passes `HttpResponse` through) as a maintained replacement for the deleted
   `bolt_view` — documented for sites that still like the tuple style.
2. **Deprecate the `django-bolt` plugin** (`plugins/bolt`) or split it into an
   optional extra; it is dead weight in every site (not installed, no mount).

### 2.4 URLs 🔮

1. **`django_fusion.urls`** — an `api_patterns()` helper returning the standard
   `health/`, `branding/`, `layouts/` trio so site urls.py becomes one line:

   ```python
   urlpatterns += django_fusion_urls()
   ```

   (No per-site kwargs — branding is driven by env vars / the Wagtail
   `FusionBranding` snippet.)
2. **`apps.py` label cleanup** — sites still set `label = "fusion_pages"` /
   `"shared"` to keep old FK names; once migrations are squashed this can go.
3. **UnicodeSlugConverter** is already re-registered in every site's urls.py —
   move the `register_converter` call into the lib so it happens once.

---

## 3. Move-into-django-fusion candidates (priority order)

| Priority | Candidate | Effort | Impact |
|---|---|---|---|
| 1 ✅ | `health`/`branding`/`layouts` views | done | removes 5 files, both sites |
| 2 🔮 | `domain` pure models (workspace, coupon, certification, newsletter, settings, enums, locations, contacts) | M | removes the largest cross-site duplication (~44 diff'd files) |
| 3 🔮 | `apps/pages/pages/components.py` page views + `layouts` resolution mixin | M | single source for the dual-mode (HTML/JSON) page contract |
| 4 🔮 | management commands (send_bulk_emails, verify_content, populate_* are triplicated in core/handlers/pages-accounts) | L | canonical command set in lib `site.management` |
| 5 🔮 | `setup_wagtail_home` command (bug-fixed last session; identical in both sites) | S | one command to maintain |

> **Note on risky deletion:** `apps/domain/migrations/0001_initial.py` applies
> `AddIndex`/`AddConstraint` for 6 models that are never created
> (`department`, `person`, `team`, `teammembership`, `techbridges`,
> `workspace`), so `migrate` fails with `KeyError`. Before moving the `domain`
> models into the lib, regenerate/repair this migration (safe — it can never be
> recorded as applied). See the dead-code audit for details.

---

## 4. Validation performed

- ✅ Live smoke test: `GET /api/health/` → 200 (`fusion_render_first`), `GET /api/branding/` → 200 (site branding), `GET /api/layouts/` → 404 on lms (cms-only route, as designed).
- ✅ lms backend: **138 passed** (includes `test_api_smoke.py` + renamed fixture tests on the new paths).
- ✅ lms frontend: `tsc --noEmit` clean + **213 vitest passed**.
- ✅ cms backend: 110 passed; 3 pre-existing failures in `test_domain_models.py` (verified identical on the stashed baseline — unrelated to this refactor).
- ✅ django-fusion lib: 324 passed; 4 pre-existing `test_form_components` template-loader failures (untouched code).
- ✅ No dangling imports remain (`grep` for old module/function names is empty).

> **Operational note:** the projects import `django_fusion.contrib.api`, which is
> a new file in the `libs/django-fusion` submodule. Before deploying/cloning
> elsewhere, push the submodule (`make push-lib LIB=django-fusion`) and bump the
> parent pointer, or the site `urls.py` imports will fail.
