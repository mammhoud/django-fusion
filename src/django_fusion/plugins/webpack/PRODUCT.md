---
id: plugin.webpack
title: Webpack Bundle-Tracker Compatibility
summary: Webpack bundle-tracker compatibility so django-webpack-loader manifests resolve through the fusion asset pipeline.
capabilities: [assets, bundle-tracker, webpack]
signals: []
requires: []
provides: [webpack]
surface: first-party
owner: Yahia
evidence:
  - path: libs/django-fusion/src/django_fusion/plugins/webpack/webpack_compat.py
    what: The monkey-patch itself — `_patch_webpack_loader()`, its idempotency guard, and the dict/string chunk handling.
  - path: libs/django-fusion/src/django_fusion/comp/apps.py
    what: The AppConfig `ready()` hook that invokes the patch, which is why a site never calls it directly.
  - path: libs/django-fusion/pyproject.toml
    what: The `webpack` extra (`django-webpack-loader>=3.2.3`) the patch is written against.
limits:
  - "Version-specific by construction: the patch exists to fix a defect between django-webpack-loader v3.2.3 and webpack-bundle-tracker v3+ dict-shaped chunks. If upstream fixes it, the patch is dead weight rather than a feature."
  - "It never bundles anything. Webpack and its config live in the frontend project; this plugin only makes the produced manifest readable."
  - "It does not patch anything if django-webpack-loader is not importable — `_patch_webpack_loader()` returns False and the site runs unpatched with whatever behaviour upstream has."
  - "A site may override STATS_FILE through its own WEBPACK_LOADER config block; the plugin reads that, it does not define the asset paths."
---

# Webpack Bundle-Tracker Compatibility

## What it does

- Patches `django-webpack-loader` at import time so the dict-shaped chunks that
  webpack-bundle-tracker v3+ emits are accepted instead of raising
  `TypeError: expected string or bytes-like object, got 'dict'`.
- Applies itself from the app config's `ready()`, so every site that loads
  django-fusion gets the fix without copying it.
- Reads `STATS_FILE` dynamically, so a site's own `WEBPACK_LOADER` block wins.
- Is idempotent — a re-import cannot half-apply it.

## What it does not do

- It does not build assets, watch files, or manage the webpack configuration.
- It does not replace django-webpack-loader; it is a compatibility shim over it,
  and shipping it is a bet on a specific upstream version pair.
- It does not degrade loudly: without `django-webpack-loader` installed it
  silently no-ops.
