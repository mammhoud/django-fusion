---
id: plugin.robyn
title: Robyn Async-Server Adapter
summary: Robyn async-server adapter that mounts fusion viewsets as Robyn routes with a /fusion/health endpoint.
capabilities: [async-server, health, robyn]
signals: []
requires: []
provides: [robyn, async-server, health]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/robyn/adapter.py
    what: The adapter that mounts fusion viewsets onto Robyn routes.
  - path: libs/django-fusion/src/django_fusion/plugins/robyn/checker.py
    what: RobynFusionChecker — capability detection and the /fusion/health route registration.
  - path: libs/django-fusion/src/django_fusion/plugins/robyn/request.py
    what: The request bridging between Robyn's Request and the fusion view contract.
  - path: libs/django-fusion/src/django_fusion/plugins/robyn/__init__.py
    what: The setup entry point that registers the health route against an app.
limits:
  - "Robyn is not declared as a dependency — not even as an extra (`pyproject.toml` has no `robyn` group). A site using this road installs robyn itself, and the adapter is inert without it."
  - "It does not make Robyn the only server. Django's own server and the WSGI/ASGI stack keep serving; this is an additional, parallel route surface for the viewsets that opt in."
  - "Health is per-request: the checker runs capability detection and answers `/fusion/health`; it does not run a background prober or persist uptime history."
  - "It does not translate Django middleware. Session/auth expectations are whatever the adapters explicitly bridge in `request.py`."
---

# Robyn Async-Server Adapter

## What it does

- Mounts fusion viewsets as Robyn routes, so a site can serve selected endpoints
  from Robyn's async server using the same viewset definitions.
- Bridges Robyn `Request` objects onto the fusion view contract.
- Registers a `/fusion/health` endpoint that reports whether the fusion surface
  is wired correctly on that app.

## What it does not do

- It does not install Robyn. There is no `robyn` extra in the library, so the
  site brings the dependency and this adapter stays unused if it is absent.
- It does not replace Django. It is a second road beside the existing one, not a
  migration of the framework onto Robyn.
- It does not proxy every Django feature through — middleware and the full
  request lifecycle are not re-implemented.
