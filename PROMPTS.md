# django-fusion — AI Prompt Reference

## Adding a new ModelViewset

**Prompt:** Add a `BlogPost` ModelViewset to the site's www/urls.py with list, detail, create, update, delete views using django-fusion's ModelViewset.

**Expected Input:** Site `www/urls.py`, existing Application definitions, model class

**Expected Output:** Viewset class, template files, URL registration

**Doc References:**
- `applications/libs/django-fusion/AGENTS.md`
- `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md`

**Related Tags:** ModelViewset, Application, CRUD, forms, tables

---

## Adding a FragmentComponent

**Prompt:** Add a `FragmentComponent` for blog post detail that loads via HTMX. The fragment should replace `#post-content` on the list page when a post is clicked.

**Expected Input:** Existing list template, blog model, URL configuration

**Expected Output:** FragmentComponent class, detail template, HTMX trigger setup

**Doc References:**
- `applications/libs/django-fusion/docs/COMPONENT_SYSTEM.md`
- `applications/libs/django-fusion/docs/ROUTING_SYSTEM.md`

**Related Tags:** FragmentComponent, HTMX, hx-get, hx-target

---

## Creating a Component with Props and Slots

**Prompt:** Create a reusable card component that accepts `title`, `summary`, `image` as props and has a `footer` named slot for action buttons.

**Expected Input:** Component template directory under `assets/templates/components/`

**Expected Output:** Component template with `{% prop %}` declarations and `{% slot %}` blocks

**Doc References:**
- `applications/libs/django-fusion/docs/COMPONENT_TAG.md`

**Related Tags:** {% comp %}, props, slots, attrs, self-closing

---

## Adding a Wagtail StreamField Block

**Prompt:** Add a custom `CallToActionBlock` StreamField block with heading, description, button text, and button URL fields. Include it in the page's content_panels.

**Expected Input:** Existing page model, blocks module

**Expected Output:** StructBlock definition, FieldPanel addition, template rendering

**Doc References:**
- `applications/libs/django-fusion/AGENTS.md`
- `applications/libs/django-fusion/docs/WAGTAIL_INTEGRATION.md`

**Related Tags:** Wagtail, StreamField, StructBlock, content_panels

---

## Setting Up Health Check Endpoints

**Prompt:** Add django-fusion health check endpoints to the site's urls.py using `include(health_urls)` pattern.

**Expected Input:** Site `urls.py`

**Expected Output:** Health URL configuration at `/health/` returning JSON status responses

**Doc References:**
- `applications/libs/django-fusion/docs/HEALTH.md`

**Related Tags:** HealthCheckView, DatabaseHealthView, Docker HEALTHCHECK, Kubernetes probe
