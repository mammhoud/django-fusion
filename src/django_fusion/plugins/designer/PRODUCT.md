---
id: plugin.designer
title: Designer Tools
summary: Interactive designer: component catalog, Wagtail field suggestions, form/table scaffolds, website audits, and safe component previews.
capabilities: [component-catalog, designer, form-scaffold, table-scaffold, wagtail-field]
signals: [designer_tools_call]
requires: []
provides: [designer, component-catalog, form-scaffold, table-scaffold, wagtail-field]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/designer/handlers.py
    what: The six generation/inspection handlers — component catalog, form scaffold, table scaffold, wagtail field, validate, preview.
  - path: libs/django-fusion/src/django_fusion/plugins/designer/website.py
    what: Website audit and the webapp enhancement plan.
  - path: libs/django-fusion/src/django_fusion/plugins/designer/mcp_router.py
    what: The MCP tool router that exposes the handlers as agent-callable tools.
  - path: libs/django-fusion/src/django_fusion/plugins/designer/views.py
    what: The HTTP views for the same surface.
  - path: libs/django-fusion/src/django_fusion/plugins/designer/__init__.py
    what: The public `__all__` — the eight names above and nothing else.
limits:
  - "Read-only or pure-generation by design: it never writes project files, so its scaffolds are text for a human or agent to apply, not applied edits."
  - "It never evaluates client-supplied template source — `designer_preview` renders registered templates only, which is the safety property the package docstring states."
  - "Its output is not verified against a running site: an audit reports what the registries and the code expose, it does not crawl a deployed site."
  - "It is opt-in. The spec is deliberately not `core=True` and not in CORE_PLUGINS, so nothing is exposed unless a site registers it."
---

# Designer Tools

## What it does

- Lists the components that are actually registered, with their props and slots,
  so a caller sees the real catalog rather than a maintained inventory.
- Generates **form and table scaffolds** and suggests **Wagtail field**
  definitions from a declarative description.
- Validates a draft and previews a registered component.
- Audits a website and produces a webapp enhancement plan.
- Serves all of it over both MCP (for agents) and HTTP views, from the same
  handlers.

## What it does not do

- It does not modify your project. Every handler is read-only or returns text;
  applying a scaffold is the caller's action.
- It does not compile or evaluate arbitrary template source, so previewing
  unregistered/attacker-supplied templates is not possible.
- It is not enabled automatically, and it is not a page builder or CMS editing
  surface — Wagtail remains the editor-facing UI.
