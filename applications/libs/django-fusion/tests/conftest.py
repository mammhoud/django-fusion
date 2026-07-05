import django
from django.conf import settings


if not settings.configured:
    settings.configure(
        SECRET_KEY="django-fusion-tests",
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
