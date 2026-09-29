---
id: plugin.staticfiles
title: Staticfiles & Asset Pipeline
summary: Serves component static assets and registers the CSS/JS asset pipeline (AssetType collection) that {% comp %} rendering depends on.
capabilities: [asset-pipeline, assets, component-assets, css, js, staticfiles]
signals: []
requires: []
provides: [staticfiles, component-assets]
surface: first-party
owner: Yahia
core: true
evidence:
  - path: libs/django-fusion/src/django_fusion/config/staticfiles.py
    what: The AssetType/AssetElement collection, the component static finder, and the AssetTag rendering used by {% comp %}.
limits:
  - "Does not compile or bundle anything — webpack is a separate tool; this plugin only serves what already exists on disk."
  - "Does not provide remote/CDN storage. `StaticFilesStorage` comes from Django or the site's own settings."
  - "Requires `django.contrib.staticfiles`; without it the finder has nothing to hook into."
---

# Staticfiles & Asset Pipeline

## What it does

- Registers the CSS/JS **asset types** that component templates declare, so a
  component's stylesheet and script are collected and emitted in the right order.
- Finds component-owned static files next to their templates (the convention
  `component.html` → `component.css` / `component.js`).
- Is auto-registered with the pluggy manager at import, because component
  rendering does not work without it (`CORE_PLUGINS`).

## What it does not do

- It does not build assets. Compilation belongs to the site's bundler
  (`npm run build`, webpack); this plugin is the serving half.
- It does not host assets on a CDN or object store.
- It does not decide `STATIC_ROOT` / `STATIC_URL` — the site does, per
  [`docs/publish/`](../../../../docs/publish/README.md) guidance.
