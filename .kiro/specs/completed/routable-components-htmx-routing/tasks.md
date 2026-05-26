# Implementation Tasks: Routable Components & Nested HTMX Fragment Views

**Feature Name:** routable-components-htmx-routing
**Status:** In Progress
**Updated:** 2026-04-19

---

## Status Legend
- [x] Completed
- [~] In Progress
- [ ] Not Started

---

## Phase 1: Core Classes (DONE)

### 1.1 RoutableComponent Base Class
**Status:** [x] Completed
**File:** `libs/django-osoul/src/django_osoul/contrib/routes/components.py`
- [x] Inherits from `ComponentViews` + `BaseViewset`
- [x] `route_name`, `route_path`, `icon`, `title`, `permission_required`
- [x] `has_permission()` — single and multi-perm support
- [x] `get_route_url()` — namespace-aware reverse
- [x] `get_breadcrumbs()` — traverses parent hierarchy
- [x] `get_context_data()` — adds breadcrumbs, title, icon, component

### 1.2 FragmentComponent Class
**Status:** [x] Completed
**File:** `libs/django-osoul/src/django_osoul/contrib/routes/fragments.py`
- [x] Inherits from `RoutableComponent`
- [x] `fragment_template`, `htmx_only`, `oob_fragments`
- [x] `is_htmx_request()` — checks HX-Request header
- [x] `get_fragment_context()` — delegates to `get_context_data()`
- [x] `get_oob_fragments()` — renders all OOB fragments
- [x] `render_oob_fragment()` — wraps HTML with hx-swap-oob
- [x] `render_to_response()` — appends OOB fragments for HTMX
- [x] `get_template_names()` — returns fragment_template for HTMX

### 1.3 Fragment Detection System
**Status:** [x] Completed
**File:** `libs/django-osoul/src/django_osoul/contrib/routes/detection.py`
- [x] `FragmentDetector.detect()` → "full" | "fragment" | "oob"
- [x] `is_htmx_request()`, `has_oob_swap()`, `get_target_id()`
- [x] `add_fragment_detection_to_request()` — augments request
- [x] `FragmentDetectionMixin` — adds detection to any view

### 1.4 BaseViewset + Viewset
**Status:** [x] Completed
**File:** `libs/django-osoul/src/django_osoul/contrib/routes/base.py`
- [x] `BaseViewset` — parent/namespace management, `reverse()`
- [x] `Viewset` — declarative `_path` attributes, `_get_urls()`
- [x] `Route` / `route()` — prefix + viewset mapping
- [x] `menu_path()` — URL pattern with icon/title metadata
- [x] `IndexViewMixin` — auto-redirect to first view

### 1.5 ModelViewset + CRUD Mixins
**Status:** [x] Completed
**Files:** `model.py`, `other.py`
- [x] `BaseModelViewset` — model, queryset, list_view_class
- [x] `ModelViewset` — List + Create + Update + AppMenuMixin
- [x] `DeleteViewMixin` — single + bulk delete
- [x] `DetailViewMixin` — detail view + page actions
- [x] `ReadonlyModelViewset` — List + Detail only
- [x] `ListBulkActionsMixin` — bulk action support

### 1.6 Application + Site
**Status:** [x] Completed
**File:** `libs/django-osoul/src/django_osoul/contrib/routes/sites.py`
- [x] `AppMenuMixin` — title/icon with auto-title from class name
- [x] `Application` — groups viewsets, `menu_items()`, `has_view_permission()`
- [x] `Site` — top-level container, `register()`, `get_absolute_url()`
- [x] `Site._viewset_models` — cached model→viewset map

---

## Phase 2: Integration Layer (THIS SPRINT)

### 2.1 Fix RoutableComponent Import Path
**Status:** [~] In Progress
**Priority:** High

The `RoutableComponent` imports from `django_osoul.comp.site.page_handler` but
`ComponentViews` lives in `django_osoul.contrib.page_handler`. Verify and fix.

**Files:**
- `libs/django-osoul/src/django_osoul/contrib/routes/components.py`

**Acceptance Criteria:**
- [x] Import resolves without error
- [x] `RoutableComponent` can be instantiated
- [x] `has_permission()` works correctly
- [x] `get_route_url()` works correctly

---

### 2.2 Wire FragmentComponent into ComponentViews Strategy
**Status:** [x] Completed
**Priority:** High

`FragmentComponent.get()` now calls `get_fragment_context()` for HTMX requests
and delegates to parent `ComponentViews.get()` for full-page requests.

---

### 2.3 Add `page_title` Attribute to RoutableComponent
**Status:** [x] Completed
**Priority:** Medium

`page_title` added as alias for `title`. `get_context_data()` includes both.

---

### 2.4 Add `menu_label` and `menu_order` to RoutableComponent
**Status:** [x] Completed
**Priority:** Medium

`menu_label`, `menu_order` (default 100), `show_in_menu` (default True) added.
`Application.menu_items()` now sorts by `menu_order` and respects `show_in_menu`.

---

### 2.5 Fix `htmx_only` to Return 400 Not 403
**Status:** [x] Completed
**Priority:** Medium

`FragmentComponent.dispatch()` patched to return HTTP 400 when `htmx_only=True`
and request is not HTMX. Uses `_BadRequest` exception internally.

---

### 2.6 Add `paginate_by` Support to FragmentComponent
**Status:** [x] Completed
**Priority:** Medium

`paginate_by`, `page_kwarg`, `get_queryset()` added. `get_fragment_context()`
auto-paginates when `paginate_by` is set, adding `page_obj`, `paginator`,
`object_list`, `is_paginated`, `has_next`, `has_previous` to context.

---

## Phase 3: Template Tags & Templates

### 3.1 Create `routable_components` Template Tag Library
**Status:** [x] Completed
**Priority:** High
**File:** `libs/django-osoul/src/django_osoul/site/routes/templatetags/routable_components.py`

Tags implemented:
- [x] `{% site_menu site user %}` — renders full site navigation
- [x] `{% app_menu app user %}` — renders application menu
- [x] `{% breadcrumbs component %}` — renders breadcrumb trail
- [x] `{% component_url component %}` — returns URL for component
- [x] `{% active_menu component %}` — returns "active" if current
- [x] `{% fragment_pagination page_obj url %}` — HTMX pagination controls

---

### 3.2 Create Default Fragment Templates
**Status:** [x] Completed
**Priority:** Medium
**Directory:** `libs/django-osoul/src/django_osoul/site/routes/templates/`

Templates created:
- [x] `routable_components/menu/site_menu.html`
- [x] `routable_components/menu/app_menu.html`
- [x] `routable_components/breadcrumbs.html`
- [x] `routable_components/pagination.html`

---

### 3.3 Create HTMX Fragment Base Template
**Status:** [ ] Deferred
**Priority:** Low — existing templates sufficient.

---

## Phase 4: ctc-research.com Integration

### 4.1 Create `apps/core/routes.py` in ctc-research
**Status:** [x] Completed
**File:** `ctc-research.com/apps/core/routes.py`

- [x] `LMSApp` with `DashboardComponent`, `CourseViewset`, `EnrollmentViewset`, `CourseListFragment`
- [x] `BlogApp` with `BlogPostViewset`, `BlogCategoryViewset`, `BlogPostListFragment`
- [x] `site = Site(title="CTC Research", viewsets=[LMSApp(), BlogApp()])`
- [x] Lazy imports to avoid circular dependencies

---

### 4.2 Create LMS Viewsets for ctc-research
**Status:** [x] Completed
**File:** `ctc-research.com/apps/lms/viewsets.py`

- [x] `CourseViewset(ModelViewset)` — list, create, update, delete with permissions
- [x] `EnrollmentViewset(ReadonlyModelViewset)` — staff-only read-only view

---

### 4.3 Create Blog Viewsets for ctc-research
**Status:** [x] Completed
**File:** `ctc-research.com/apps/blog/viewsets.py`

- [x] `BlogPostViewset(ModelViewset)` — public read, staff write
- [x] `BlogCategoryViewset(ModelViewset)` — staff only

---

### 4.4 Create Fragment Components for ctc-research
**Status:** [x] Completed
**Files:** `ctc-research.com/apps/lms/components.py`, `ctc-research.com/apps/blog/components.py`

- [x] `DashboardComponent(RoutableComponent)` — LMS dashboard with stats
- [x] `CourseListFragment(FragmentComponent)` — paginated, search, category filter
- [x] `BlogPostListFragment(FragmentComponent)` — paginated, search, category filter

---

### 4.5 Wire site.urls into ctc-research core/urls.py
**Status:** [x] Completed
**File:** `ctc-research.com/core/urls.py`

- [x] `path("app/", include(site.urls))` added with graceful fallback
- [x] Existing URL patterns unchanged
- [x] Try/except prevents startup failure if routes fail to load

---

### 4.6 Create Fragment Templates for ctc-research
**Status:** [x] Completed

Templates created:
- [x] `ctc-research.com/assets/templates/lms/fragments/course_list.html`
- [x] `ctc-research.com/assets/templates/blog/fragments/post_list.html`
- [x] `ctc-research.com/assets/templates/lms/dashboard.html`

---

## Phase 5: HTMX Enhancement & Integration

### 5.1 Create BlogPostCreateFragment Component
**Status:** [x] Completed
**Priority:** High
**File:** `ctc-research.com/apps/blog/components.py`

New component for HTMX-based post creation:
- [x] `BlogPostCreateFragment(FragmentComponent)` class
- [x] `route_name = "post-create-fragment"`, `route_path = "posts/create-fragment/"`
- [x] `fragment_template = "blog/fragments/post_create_form.html"`
- [x] `htmx_only = True` — only responds to HTMX requests
- [x] `has_permission()` — staff only
- [x] `get_fragment_context()` — returns form instance
- [x] `post()` override — handles form submission, returns success or form errors
- [x] `oob_fragments` — list with post-list refresh fragment on success

**Acceptance Criteria:**
- [x] Component instantiates without error
- [x] GET request returns form HTML
- [x] POST with valid data creates post and returns OOB refresh
- [x] POST with invalid data returns form with errors
- [x] Non-HTMX requests return 400

---

### 5.2 Create BlogPostCreateFragment Template
**Status:** [x] Completed
**Priority:** High
**File:** `ctc-research.com/assets/templates/blog/fragments/post_create_form.html`

HTMX form template for post creation:
- [x] Form with `hx-post` to fragment endpoint
- [x] Fields: title, slug, excerpt, body, category, status
- [x] CSRF token included
- [x] Error display for each field
- [x] Submit button with loading state (`hx-indicator`)
- [x] Success message placeholder (for OOB swap)

**Acceptance Criteria:**
- [x] Form renders without errors
- [x] All required fields present
- [x] CSRF token included
- [x] Error messages display correctly

---

### 5.3 Enhance BlogPostListFragment with OOB Fragments
**Status:** [x] Completed
**Priority:** High
**File:** `ctc-research.com/apps/blog/components.py`

Update `BlogPostListFragment` to support OOB updates:
- [x] Add `oob_fragments` property
- [x] Include success message fragment (hidden by default)
- [x] Include post count fragment for stats
- [x] Update `get_oob_fragments()` to render on demand
- [x] Add context for OOB fragment visibility

**Acceptance Criteria:**
- [x] OOB fragments render correctly
- [x] Success message appears after post creation
- [x] Post count updates without page reload
- [x] Multiple OOB fragments in single response

---

### 5.4 Create OOB Fragment Templates
**Status:** [x] Completed
**Priority:** High
**Directory:** `ctc-research.com/assets/templates/blog/fragments/`

New templates for out-of-band updates:
- [x] `post_create_success.html` — success toast/alert
- [x] `post_count.html` — updated post count for stats
- [x] Both wrapped with `hx-swap-oob="true"` and unique IDs

**Acceptance Criteria:**
- [x] Templates render without errors
- [x] Correct IDs for HTMX targeting
- [x] Proper styling and messaging

---

### 5.5 Wire BlogPostCreateFragment into BlogApp
**Status:** [x] Completed
**Priority:** High
**File:** `ctc-research.com/apps/core/routes.py`

Register new component in site routing:
- [x] Add `BlogPostCreateFragment()` to `BlogApp.viewsets`
- [x] Verify URL generation: `/osoul/blog/posts/create-fragment/`
- [x] Test namespace resolution

**Acceptance Criteria:**
- [x] Component appears in site.urls
- [x] URL reverses correctly
- [x] No namespace conflicts

---

### 5.6 Write Integration Tests for HTMX Workflow
**Status:** [x] Completed
**Priority:** High
**File:** `tests/integration/test_blog_htmx_workflow.py`

Full end-to-end tests:
- [x] Test GET `/osoul/blog/posts/create-fragment/` returns form
- [x] Test POST with valid data creates post + OOB refresh
- [x] Test POST with invalid data returns form errors
- [x] Test non-HTMX GET returns 400
- [x] Test permission denied for non-staff
- [x] Test OOB fragments in response
- [x] Test post list updates after creation

**Acceptance Criteria:**
- [x] All tests pass
- [x] Coverage > 80% for blog components
- [x] No flaky tests

---

### 5.7 Verify Namespace Conflicts
**Status:** [x] Completed
**Priority:** Medium
**Files:** `ctc-research.com/apps/blog/urls.py`, `ctc-research.com/apps/core/routes.py`

Audit for namespace collisions:
- [x] Check traditional `blog:` routes vs `/osoul/blog/` routes
- [x] Verify no duplicate route names
- [x] Test URL reversals don't collide
- [x] Document namespace strategy

**Acceptance Criteria:**
- [x] No URL conflicts found
- [x] Both routing systems coexist
- [x] Clear documentation of namespace strategy

---

### 5.8 Create Migration Guide
**Status:** [x] Completed
**Priority:** Medium
**File:** `docs/routable-components/MIGRATION_GUIDE_BLOG.md`

Documentation for using new routable components:
- [x] Overview of routable vs traditional routing
- [x] How to create a `RoutableComponent`
- [x] How to create a `FragmentComponent`
- [x] HTMX integration patterns
- [x] OOB fragment examples
- [x] Permission system
- [x] URL reversal examples
- [x] Common pitfalls and solutions

**Acceptance Criteria:**
- [x] Guide is clear and complete
- [x] Code examples are runnable
- [x] Covers all major use cases

---

### 5.9 Create API Reference Documentation
**Status:** [x] Completed
**Priority:** Medium
**File:** `docs/routable-components/API_REFERENCE.md`

Class and method reference:
- [x] `RoutableComponent` — all attributes and methods
- [x] `FragmentComponent` — all attributes and methods
- [x] `Application` — configuration and methods
- [x] `Site` — configuration and methods
- [x] Template tags — `{% site_menu %}`, `{% fragment_pagination %}`, etc.

**Acceptance Criteria:**
- [x] All public APIs documented
- [x] Type hints included
- [x] Examples for each major method

---

### 5.10 Create Usage Examples
**Status:** [x] Completed
**Priority:** Low
**File:** `docs/routable-components/EXAMPLES.md`

Real-world usage examples:
- [x] Simple list fragment with pagination
- [x] Create form with OOB refresh
- [x] Nested applications and viewsets
- [x] Permission-based menu items
- [x] Custom template tags

**Acceptance Criteria:**
- [x] Examples are clear and runnable
- [x] Cover common patterns
- [x] Include HTMX integration

---

## Task Dependencies

```
Phase 1-4 (DONE)
    │
    └── Phase 5: HTMX Enhancement & Integration
        │
        ├── 5.1 BlogPostCreateFragment component
        │   ├── 5.2 Create form template
        │   └── 5.5 Wire into BlogApp
        │
        ├── 5.3 Enhance BlogPostListFragment with OOB
        │   └── 5.4 Create OOB templates
        │
        ├── 5.6 Integration tests (depends on 5.1-5.5)
        │
        ├── 5.7 Verify namespace conflicts
        │
        └── 5.8-5.10 Documentation (can run in parallel)
            ├── 5.8 Migration guide
            ├── 5.9 API reference
            └── 5.10 Usage examples
```

---

## Success Criteria

### Code Quality
- [ ] All public APIs have type hints
- [ ] All public APIs have docstrings
- [ ] No linting errors (ruff)
- [ ] Code coverage > 80%

### Functionality
- [ ] All Phase 2 fixes applied
- [ ] Template tags render menus and breadcrumbs
- [ ] ctc-research site.urls generates valid patterns
- [ ] Fragment requests return fragments, not full pages
- [ ] OOB fragments appended correctly

### Performance
- [ ] URL resolution < 10ms
- [ ] Fragment detection < 1ms overhead

### Compatibility
- [ ] Django 4.2+ compatible
- [ ] Python 3.11+ compatible
- [ ] HTMX 1.9+ compatible
- [ ] Existing ctc-research URLs unchanged
