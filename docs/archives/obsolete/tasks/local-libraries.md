# Local library consolidation tasks

Priority: 3 — after runtime and template/auth path stability.

## Affected paths
- `core/libs/django-fusion/`
- `core/libs/django-fusion/`
- `core/libs/ceptor-ai/`
- `core/libs/ceptor-ai/`
- `core/ctc-research/`
- `core/lms-demo/`
- `core/VResume/`
- `tests/`

## Intended behavior
- Component/configuration functionality duplicated between `ceptor-ai` and `django-fusion` is consolidated into `django-fusion`.
- `django-fusion` functionality is merged into `core/libs/django-fusion` with imports migrated or compatibility shims retained.
- `ceptor-ai` functionality is merged into `core/libs/ceptor-ai` with imports migrated or compatibility shims retained.
- Directory namespaces are organized around clear Django/use-case conventions such as `contrib`, `models`, `managers`, `management`, and `services`.

## Validation commands
- `rg -n "django_fusion|django-fusion|ceptor_ai|ceptor-ai|rseal|grep" applications tests`
- `python -m compileall core/libs/django-fusion core/libs/ceptor-ai core/libs/django-fusion core/libs/ceptor-ai`
- `make -C applications check WEBSITE=ctc`
- `make -C applications check WEBSITE=lms-demo`
- `make -C applications check WEBSITE=VResume`
- `pytest tests/unit tests/apps`
