# Formint Cloud — Database ERD

Entity-relationship diagrams for the Formint Cloud (POS SaaS) Django models.

## Generate

```bash
cd projects/formints/formint-cloud
make erd        # combined diagram → docs/erd/formint_cloud_erd.png
make erd-all    # one PNG per app  → docs/erd/
```

Output: `projects/formints/formint-cloud/docs/erd/formint_cloud_erd.png`

Apps covered: `apps.core`, `apps.domain`, `apps.handlers`

## Requirements

- `graphviz` — install with `apt-get install graphviz` in the dev environment
- `django-extensions` — in `backend/pyproject.toml`
- `pydot` — in `backend/pyproject.toml`
- `django_extensions` in `INSTALLED_APPS` in `backend/configs/__init__.py`

## Notes

PNG output files are git-ignored (`*.png` in root `.gitignore`).
The `docs/erd/` directory is tracked via `.gitkeep`.
Regenerate after any model migration under `backend/apps/`.
