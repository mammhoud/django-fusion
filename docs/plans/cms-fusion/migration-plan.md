# Fusion CMS - Migration & Integration Plan

> **Status:** Superseded by Precis and Landing-Fusion
> **Canonical runtime:** [`projects/precis/main/`](../../../projects/precis/main/)
> **Canonical landing slice:** [`projects/precis/landi/`](../../../projects/precis/landi/)
> **Historical boundary:** `projects/cms-fusion/`
> **Last reviewed:** 2026-08-11

This document is retained as migration evidence. The former CMS-Fusion
boundary was split into the active Precis learning/content runtime and the
Landing-Fusion Astro + Django/Wagtail landing slice. New work must use those
canonical project paths and their current Makefiles, tests, assets, and Docker
configuration.

## Disposition

- Core django-fusion integration: complete in the historical migration.
- Landing content and AHA rendering: maintained by Landing-Fusion.
- Learning/catalog/API runtime: maintained by Precis.
- The former Next.js/FlyonUI proposal is historical and is not an active
  implementation target.
- Project APIs remain project-owned; django-fusion does not regain the removed
  Bolt integration.

## Current verification commands

```bash
cd projects/precis/main
uv run python backend/manage.py check
uv run pytest backend/tests/test_api_smoke.py \
  backend/tests/test_fixture_content.py \
  backend/tests/test_fixture_data.py -q --tb=short
cd frontend && npm run check && npm run build

cd ../precis/landi/backend && make check && make test
cd ../frontend && npm run check && npm run build
```

## Related

- [`../../README.md`](../README.md)
- [`../../../projects/precis/main/README.md`](../../../projects/precis/main/README.md)
- [`../../../projects/precis/landi/README.md`](../../../projects/precis/landi/README.md)
- [`../../repository/active-project-closeout-2026-08-11.md`](../repository/active-project-closeout-2026-08-11.md)
