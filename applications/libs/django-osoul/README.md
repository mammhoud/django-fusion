# django-osoul

`django-osoul` is the reusable Django/Wagtail helper package for Structa Cloud.
The legacy reference checkout has been retired: the former
`django-osoul` package content and the former `django-grep` support utilities now
live directly in this package.

## Merged namespaces

- New and refactored code should import from `django_osoul`.
- The legacy `django_grep` top-level import path is still packaged from
  `applications/libs/django-osoul/src/django_grep/` so older site code can keep
  running during the migration window.
- Do not restore the legacy reference checkout; add shared Django helpers, component
  tooling, cache helpers, and debug/test utilities here instead.

## Local checks

```bash
python -m compileall -q applications/libs/django-osoul/src
python -m pytest applications/libs/django-osoul/tests
```
