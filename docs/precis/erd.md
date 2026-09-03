# Precis — Database ERD

Entity-relationship diagrams for the Precis Django products. Each product
generates its own ERD from `django-extensions` `graph_models`.

## Precis Main (unified LMS + landing)

**Generate:** `cd projects/precis/precis-main/backend && make erd`

Output: `projects/precis/precis-main/docs/erd/precis_main_erd.png`

Apps covered: `apps.content`, `apps.pages`, `apps.handlers`, `apps.auth`,
`apps.learning`, `apps.tasks`, `apps.components`, `apps.domain`

Per-app diagrams: `make erd-all` → one PNG per app in `docs/erd/`.

## CTC Research

**Generate:** `cd projects/precis/precis-ctc/backend && make erd`

Output: `projects/precis/precis-ctc/docs/erd/precis_ctc_erd.png`

Apps covered: `apps.content`, `apps.learning`, `apps.pages`, `apps.handlers`,
`apps.auth`, `apps.core`, `apps.domain`

Per-app diagrams: `make erd-all` → one PNG per app in `docs/erd/`.

## Requirements

Both products share the same stack:

- `graphviz` — system package, pre-installed in all backend Docker images
- `django-extensions` — Python package in `projects/pyproject.toml`
- `pydot` — Python package in `projects/pyproject.toml`
- `django_extensions` in `INSTALLED_APPS` via `projects/precis/configs/base/apps.py`

## Notes

PNG output files are git-ignored (`*.png` in root `.gitignore`).
The `docs/erd/` directories are tracked via `.gitkeep`.
Regenerate diagrams after any model migration.
