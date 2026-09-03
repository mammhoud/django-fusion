# Syntara — Database ERD

Entity-relationship diagrams for the Syntara (Cypercloud AI chat) Django models.

## Generate

```bash
cd projects/syntara
make erd        # combined diagram → docs/erd/syntara_erd.png
make erd-all    # one PNG per app  → docs/erd/
```

Output: `projects/syntara/docs/erd/syntara_erd.png`

Apps covered: `chat`

## Requirements

- `graphviz` — system package, pre-installed in the Syntara Docker image
- `django-extensions` — in `requirements.txt`
- `pydot` — in `requirements.txt`
- `django_extensions` in `INSTALLED_APPS` in `settings.py`

## Notes

PNG output files are git-ignored (`*.png` in root `.gitignore`).
The `docs/erd/` directory is tracked via `.gitkeep`.
Regenerate after any model migration in `chat/`.
