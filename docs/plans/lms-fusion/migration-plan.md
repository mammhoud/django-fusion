# LMS Fusion - Migration & django-fusion Integration Plan

> **Status:** Superseded by the canonical Precis project
> **Canonical runtime:** [`projects/precis/`](../../../projects/precis/)
> **Historical boundary:** `projects/lms-fusion/`
> **Last reviewed:** 2026-08-11

This document is retained as migration evidence. It is no longer an active
implementation checklist. New LMS work belongs in Precis and must use the
current `projects/precis/` paths, settings, tests, Docker Compose, and Astro
frontend. The original sections below are preserved so historical decisions
and verification claims remain traceable.

## Disposition

- Core django-fusion integration: complete in the historical migration.
- Runtime ownership: moved to `projects/precis/`.
- API ownership: remains project-owned; django-fusion provides rendering,
  routing, components, fragments, and data-response primitives.
- Remaining historical checkboxes: not reinterpreted as current work. Verify
  the current state with Precis commands instead.

## Current verification commands

```bash
cd projects/precis
uv run python backend/manage.py check
uv run pytest backend/tests/test_api_smoke.py \
  backend/tests/test_fixture_content.py \
  backend/tests/test_fixture_data.py -q --tb=short
cd frontend && npm run check && npm run build
```

## Historical migration record

The original plan content is preserved in git history and in the repository's
migration evidence. The current plan registry records this file as superseded;
no new code should be added under the retired LMS Fusion boundary.

## Related

- [`../../README.md`](../README.md)
- [`../../../projects/precis/README.md`](../../../projects/precis/README.md)
- [`../../repository/active-project-closeout-2026-08-11.md`](../repository/active-project-closeout-2026-08-11.md)
- [`../../../libs/django-fusion/CHANGELOG.md`](../../../libs/django-fusion/CHANGELOG.md)
