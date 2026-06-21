
## Deprecated compatibility namespace

The legacy `django_grep` top-level import path now exists only as a temporary
compatibility shim in `applications/libs/django-osoul/src/django_grep/__init__.py`.
Do not add new code under that namespace; migrate imports to `django_osoul`.
