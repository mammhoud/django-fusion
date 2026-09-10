---
Object type: Decision
Status: Accepted
Category: Technology
Date: 2024-08-15
Decision Maker: mammhoud
Tags: adr, django, fusion, component

# ADR-002: django-fusion Custom Component System

## Context

As the Structa Cloud monorepo grew from one site (CTC Research) to multiple sites (LMS Demo, VResume, Tinker, POS editions), we needed a consistent way to build and share UI components across Django applications. Each site was duplicating similar patterns: navigation menus, data tables, forms, cards, and authentication flows.

The key requirements were:
- Reusable components that could be shared across all sites
- Server-side rendering (no mandatory JavaScript framework)
- URL routing at the component level (not just the view level)
- Partial page updates (fragment rendering) for HTMX-like interactions
- Wagtail StreamField block integration

## Options Considered

1. **Django generic class-based views (CBVs)**
   - Pros: Built-in, well-documented, no new dependency
   - Cons: No component reuse across views, no fragment rendering, no StreamField integration

2. **Django REST Framework + React frontend**
   - Pros: Rich component ecosystem, modern frontend patterns
   - Cons: Full rewrite required, dual backend complexity, overkill for content-focused sites

3. **Third-party Django component libraries (django-crispy-forms, django-components)**
   - Pros: Existing community solutions, documented patterns
   - Cons: Limited routing support, no fragment system, Wagtail integration gaps

4. **Custom django-fusion framework** — **Chosen**
   - Pros: Full control over component model, routable components, fragment rendering, Wagtail integration
   - Cons: Development time, maintenance burden, documentation required

## Decision

We built **django-fusion**, a custom component and routing framework for Django, hosted at `libs/django-fusion/`.

The framework provides:

- **Routable components** (`Component` class with `route()` method) — components can define their own URL routes, not just views
- **Fragment rendering** (`FragmentComponent`) — components can render partial page content for HTMX-style updates
- **Viewset pattern** (`ModelViewset`) — CRUD operations with list/detail/create/update/delete views built in
- **Template tag system** (`{% comp "name" /%}`) — renders components declaratively in templates
- **Wagtail StreamField blocks** — components can be used within Wagtail page content
- **Include path tracking** (`{% comp_include "path" %}`) — registers template includes for dependency tracking
- **Authentication mixins** — reusable auth flows across all sites

All import paths use canonical module references (e.g., `from django_fusion.comp.routes import Viewset`) without re-export shims — a deliberate choice to keep the dependency graph explicit and avoid import confusion.

## Consequences

**Positive:**
- All sites share the same component library — visual consistency by default
- Fragment rendering enables smooth HTMX interactions without a JS framework
- Wagtail StreamField blocks can render Fusion components, blending CMS and component patterns
- New sites can reuse existing components with zero duplication
- Template syntax (`{% comp %}`) is declarative and familiar to Django developers

**Negative:**
- Custom framework means custom bugs — no community support
- New developers must learn Fusion patterns on top of Django
- Framework development diverts time from feature work
- Versioning and migration across sites must be coordinated

**Risks:**
- **Framework drift** — mitigated by keeping Fusion focused on its core patterns, not adding speculative features
- **Wagtail version incompatibility** — mitigated by pinning Wagtail versions in `pyproject.toml`
- **Developer adoption friction** — mitigated by comprehensive `AGENTS.md` and `CLAUDE.md` files in the library

## Related Docs

- → `../objects/decision.md` — Decision object type
- → `../architecture/overview.md` — Architecture overview
- → `../../libs/django-fusion/AGENTS.md` — django-fusion agent instructions
- → `../guides/development-workflow.md` — Setup guide
- → `../references/` — API references
