---
id: plugin.htmx
title: HTMX & Fragments
summary: HTMX request detection, fragment swap helpers, and SSE push utilities for dual-mode views that answer with either a fragment or a full page.
capabilities: [ajax, fragments, htmx, partial-render, sse]
signals: [fragment-request, htmx-request, sse]
requires: []
provides: [htmx, fragments, sse]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/htmx/core.py
    what: HtmxDetails request wrapper, request detection, and response helpers.
  - path: libs/django-fusion/src/django_fusion/plugins/htmx/sse.py
    what: The Server-Sent Events streamer that renders a template as a single `fragment` event.
  - path: libs/django-fusion/src/django_fusion/plugins/htmx/README.md
    what: The usage reference for the plugin's public surface.
limits:
  - "Does not ship the HTMX JavaScript library — the site loads it (or uses the Astro client), and this plugin only speaks the server protocol."
  - "SSE here is one-way server-to-client; there is no WebSocket transport."
  - "Detection reads headers and path prefixes only. It cannot know whether a client is really an HTMX client if the headers are stripped by a proxy."
  - "No client-side state management: swapping, history, and focus behaviour are HTMX's, not this plugin's."
---

# HTMX & Fragments

## What it does

- Detects HTMX requests (`HX-Request`, `HX-Target`) and exposes them as a typed
  request wrapper, so a view can branch without re-parsing headers.
- Provides fragment swap helpers and the small response conveniences dual-mode
  views need.
- Streams a rendered template to the client as a single SSE `fragment` event,
  for the HTMX SSE extension.

## What it does not do

- It does not bundle HTMX. A site that never loads the library can still have
  this plugin installed — it simply never sees a matching request.
- It does not implement WebSockets or bidirectional streaming.
- It does not decide render mode. The render-first contract
  (`docs/plans/repository/precis-main-render-flow.md`) owns that decision; this
  plugin supplies the signals it reads.
