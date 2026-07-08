import os
import sys

import django
from django.conf import settings

# Ensure the tests directory is on the Python path so that
# ROOT_URLCONF='tests.urls' can be imported at configure-time.
_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

if not settings.configured:
    settings.configure(
        SECRET_KEY="django-fusion-tests",
        ROOT_URLCONF="urls",  # resolves to tests/urls.py
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "taggit",
            "modelcluster",
            "wagtail",
            "wagtail.admin",
            "wagtail.snippets",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.AutoField",
        STATIC_URL="/static/",
    )
    django.setup()
