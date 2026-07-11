# django-fusion — AI Prompt Reference

Prompt entries below are tagged with the stable doc IDs (from
`docs/INDEX.md`) they touch. Paths in `**Doc IDs**` lines are repo-relative
and apply equally to the standalone repo or the Structa Cloud submodule at
`core/libs/django-fusion/`.

## PR-01 — Add a ModelViewset

**Prompt:** Add a `BlogPost` ModelViewset to the site's `www/urls.py` with
list, detail, create, update, delete views using django-fusion's
`ModelViewset`.

**Expected Input:** Site `www/urls.py`, existing Application definitions, model class
**Expected Output:** Viewset class, template files, URL registration

**Doc IDs:** `DF-000`, `DF-005`
**Related Tags:** ModelViewset, Application, CRUD, forms, tables

---

## PR-02 — Add a FragmentComponent

**Prompt:** Add a `FragmentComponent` for blog post detail that loads via
HTMX. The fragment should replace `#post-content` on the list page when
a post is clicked.

**Expected Input:** Existing list template, blog model, URL configuration
**Expected Output:** FragmentComponent class, detail template, HTMX trigger setup

**Doc IDs:** `DF-003`, `DF-005`
**Related Tags:** FragmentComponent, HTMX, hx-get, hx-target

---

## PR-03 — Create a Component with Props and Slots

**Prompt:** Create a reusable card component that accepts `title`,
`summary`, `image` as props and has a `footer` named slot for action
buttons.

**Expected Input:** Component template directory under
`assets/templates/components/`

**Expected Output:** Component template with `{% prop %}` declarations and
`{% slot %}` blocks

**Doc IDs:** `DF-004`
**Related Tags:** `{% comp %}`, props, slots, attrs, self-closing

---

## PR-04 — Add a Wagtail StreamField Block

**Prompt:** Add a custom `CallToActionBlock` StreamField block with
heading, description, button text, and button URL fields. Include it in
the page's `content_panels`.

**Expected Input:** Existing page model, blocks module
**Expected Output:** `StructBlock` definition, `FieldPanel` addition,
template rendering

**Doc IDs:** `DF-010`
**Related Tags:** Wagtail, StreamField, StructBlock, content_panels

---

## PR-05 — Wire Health-Check Endpoints

**Prompt:** Add django-fusion health-check endpoints to the site's
`urls.py` using the `include(health_urls)` pattern.

**Expected Input:** Site `urls.py`
**Expected Output:** Health URL configuration at `/health/` returning JSON
status responses

**Doc IDs:** `DF-009`
**Related Tags:** HealthCheckView, DatabaseHealthView, AssetsHealthView,
Docker HEALTHCHECK, Kubernetes probe
