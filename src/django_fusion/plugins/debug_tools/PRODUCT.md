---
id: plugin.debug_tools
title: Debug & Introspection Tools
summary: Development tooling — debug toolbar, Silk, livereload, Prometheus metrics, error views and the fusion introspection dashboard.
capabilities: [debugging, dev-tools, introspection, monitoring, profiling]
signals: []
requires: []
provides: [debugging, introspection, dev-tools, monitoring, profiling]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/debug_tools/core.py
    what: The registration entry point that decides which tools are active and mounts their URL configuration.
  - path: libs/django-fusion/src/django_fusion/plugins/debug_tools/detection.py
    what: Environment/setting detection that turns each tool on or off.
  - path: libs/django-fusion/src/django_fusion/plugins/debug_tools/introspection.py
    what: The fusion introspection dashboard — plugin, component and route truth read from the live registries.
  - path: libs/django-fusion/src/django_fusion/plugins/debug_tools/prometheus.py
    what: Prometheus metrics exposure.
  - path: libs/django-fusion/src/django_fusion/plugins/debug_tools/error_views.py
    what: The debug error views (traceback presentation in development).
  - path: libs/django-fusion/src/django_fusion/plugins/debug_tools/autoreload.py
    what: Livereload/autoreload wiring.
limits:
  - "It does not bundle the third-party tools it switches on: debug toolbar and Silk are Django apps the site installs and lists in INSTALLED_APPS; this plugin only gates and mounts them (`prometheus_client` is the same story)."
  - "It ships no security boundary of its own. Its whole purpose is to expose internals, so enabling it in production is a configuration error — the detection layer assumes a development setting."
  - "It does not collect, store, or query profiling samples. Silk owns its own storage; this plugin does not read the database."
  - "It has no request-side signals — these are operator tools reached by URL, not per-request render modes, which is why `signals` is deliberately empty."
---

# Debug & Introspection Tools

## What it does

- Turns development tooling on or off from one place, by inspecting the
  environment and settings rather than each site re-deciding.
- Mounts the **fusion introspection dashboard**, which reports what is really
  registered — plugins and their specs, components, routes — by reading the live
  registries instead of a hand-kept list.
- Exposes Prometheus metrics and the development error views, and wires
  autoreload so template/asset edits show up without a reload.

## What it does not do

- It does not package the debuggers. Debug toolbar, Silk and
  `prometheus_client` are installed by the site; the plugin is the switch, not
  the tool.
- It does not provide production monitoring, alerting, or retention.
- It does not do profiling analysis: it exposes samples, it does not store them.
