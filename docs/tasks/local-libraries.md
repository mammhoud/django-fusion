# Local library consolidation tasks

Priority: 3 — after runtime and template/auth path stability.

## Affected paths
- `applications/libs/django-grep/`
- `applications/libs/django-osoul/`
- `applications/libs/django-rseal/`
- `applications/libs/crafts-ai/`
- `applications/ctc-research/`
- `applications/lms-demo/`
- `applications/VResume/`
- `tests/`

## Intended behavior
- Component/configuration functionality duplicated between `django-rseal` and `django-osoul` is consolidated into `django-osoul`.
- `django-grep` functionality is merged into `applications/libs/django-osoul` with imports migrated or compatibility shims retained.
- `django-rseal` functionality is merged into `applications/libs/crafts-ai` with imports migrated or compatibility shims retained.
- Directory namespaces are organized around clear Django/use-case conventions such as `contrib`, `models`, `managers`, `management`, and `services`.

## Validation commands
- `rg -n "django_grep|django-grep|django_rseal|django-rseal|rseal|grep" applications tests`
- `python -m compileall applications/libs/django-osoul applications/libs/crafts-ai applications/libs/django-grep applications/libs/django-rseal`
- `make -C applications check WEBSITE=ctc`
- `make -C applications check WEBSITE=lms-demo`
- `make -C applications check WEBSITE=VResume`
- `pytest tests/unit tests/apps`
