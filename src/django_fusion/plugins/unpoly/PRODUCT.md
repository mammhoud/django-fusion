---
id: plugin.unpoly
title: Unpoly Progressive Enhancement
summary: Unpoly request detection and adapter helpers for pages served with the Unpoly runtime, covering fragment targets, layer, and pushState requests.
capabilities: [progressive-enhancement, pushstate, unpoly]
signals: [unpoly-request]
requires: []
provides: [unpoly]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/unpoly/core.py
    what: The Unpoly request wrapper and the server-protocol properties (target, layer, mode).
  - path: libs/django-fusion/src/django_fusion/plugins/unpoly/adapter.py
    what: The base adapter a site subclasses to map Unpoly concepts onto its own render modes.
limits:
  - "Does not ship the Unpoly JavaScript library."
  - "Does not implement form validation or file uploads — Unpoly's client handles submission; this plugin only classifies the request."
  - "Ships one base adapter, not a full layer/navigation implementation: a site with non-trivial layer behaviour must subclass it."
---

# Unpoly Progressive Enhancement

## What it does

- Detects Unpoly requests (`X-Up-Target`) so a dual-mode view can answer with the
  fragment the client asked for.
- Wraps the request to expose the protocol details (`target`, layer, submit
  mode) without hand-parsing headers at every call site.
- Feeds the plugin registry's `unpoly-request` signal, which makes
  `plugins.detect(request)` report Unpoly correctly on the introspection
  dashboard.

## What it does not do

- It does not bundle Unpoly or configure its client options.
- It does not implement navigation, layers, or history — those are the client's.
- It does not replace the HTMX road. A site using both runs both plugins; they
  detect different headers and do not conflict.
