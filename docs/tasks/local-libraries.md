# Local library consolidation tasks

Priority: 3 — after runtime and template/auth path stability.

## Affected paths
- `applications/libs/django-osoul/`
- `applications/libs/django-osoul/`
- `applications/libs/crafts-ai/`
- `applications/libs/crafts-ai/`
- `applications/ctc-research/`
- `applications/lms-demo/`
- `applications/VResume/`
- `tests/`

## Intended behavior
- Component/configuration functionality duplicated between `crafts-ai` and `django-osoul` is consolidated into `django-osoul`.
- `django-osoul` functionality is merged into `applications/libs/django-osoul` with imports migrated or compatibility shims retained.
- `crafts-ai` functionality is merged into `applications/libs/crafts-ai` with imports migrated or compatibility shims retained.
- Directory namespaces are organized around clear Django/use-case conventions such as `contrib`, `models`, `managers`, `management`, and `services`.

## Validation commands
- `rg -n "django_osoul|django-osoul|crafts_ai|crafts-ai|rseal|grep" applications tests`
- `python -m compileall applications/libs/django-osoul applications/libs/crafts-ai applications/libs/django-osoul applications/libs/crafts-ai`
- `make -C applications check WEBSITE=ctc`
- `make -C applications check WEBSITE=lms-demo`
- `make -C applications check WEBSITE=VResume`
- `pytest tests/unit tests/apps`
