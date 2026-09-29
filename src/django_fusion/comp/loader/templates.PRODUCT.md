---
id: plugin.templates
title: Component Template Discovery
summary: Discovers component templates, tracks template-to-component usage, and feeds the component registry and render-history tracker.
capabilities: [component-discovery, loader, template-usage, templates]
signals: []
requires: []
provides: [component-discovery, template-usage]
surface: first-party
owner: Yahia
core: true
evidence:
  - path: libs/django-fusion/src/django_fusion/comp/loader/templates.py
    what: Template directory resolution, component discovery in templates, and the block-tag usage scanner.
  - path: libs/django-fusion/src/django_fusion/comp/loader/discovery.py
    what: Section discovery used by the component loader.
limits:
  - "Does not render templates — it scans and registers them; rendering belongs to Django's template engine and the {% comp %} tag."
  - "Does not cache template output; the component map cache is a separate module (django_fusion.comp.cache)."
  - "Discovers only the conventions it knows: component templates under the configured app template directories."
---

# Component Template Discovery

## What it does

- Resolves the template directories a site's components live in, so
  `{% comp "name" %}` can find them without app-by-app `TEMPLATES['DIRS']` edits.
- Scans templates for component usage and feeds the component registry, which is
  what makes `{% comp %}` name resolution work.
- Is auto-registered at import (a member of `CORE_PLUGINS`) because the registry
  is empty without it.

## What it does not do

- It does not render, cache, or mutate templates.
- It does not validate your HTML or CSS — see the designer plugin's audit tools.
- It does not discover components outside the template directories the site
  configures.
