"""
Tests that run INSIDE the Docker container:
  docker exec <container> python -m pytest /tmp/test_container.py -v -p no:django

Tests the production Django environment directly.
Run with -p no:django to bypass pytest-django's DB access restrictions
since we're testing the live production DB.
"""
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("RUNNING_ENV", "docker")
os.environ.setdefault("SERVER_ENV", "production")
os.environ.setdefault("ALLOWED_HOSTS", "*")
# SECRET_KEY is loaded from secret.key.txt by production.py — do not set here

import django

django.setup()

# Allow DB access by disabling pytest-django's restriction
from django.test.utils import setup_test_environment

setup_test_environment()

import pytest

# ── Settings ─────────────────────────────────────────────────────────────────

def test_settings_load():
    from django.conf import settings
    assert settings.configured
    assert settings.SECRET_KEY and len(settings.SECRET_KEY) > 10


def test_installed_apps():
    from django.conf import settings
    for app in ["django.contrib.auth", "django.contrib.contenttypes",
                "wagtail", "allauth.account"]:
        assert app in settings.INSTALLED_APPS, f"Missing: {app}"


def test_middleware():
    from django.conf import settings
    assert "django.middleware.security.SecurityMiddleware" in settings.MIDDLEWARE
    assert "django.contrib.auth.middleware.AuthenticationMiddleware" in settings.MIDDLEWARE


def test_database_engine():
    from django.conf import settings
    engine = settings.DATABASES["default"]["ENGINE"]
    assert "postgresql" in engine or "sqlite3" in engine


def test_migration_modules_sites():
    from django.conf import settings
    assert settings.MIGRATION_MODULES.get("sites") == "www.migrations"


def test_allowed_hosts_set():
    from django.conf import settings
    assert settings.ALLOWED_HOSTS


# ── Database (direct — bypasses pytest-django restriction) ───────────────────

def test_db_connection():
    from django.db import connection
    # Use allow_database_queries context to bypass pytest-django
    conn = connection
    conn.ensure_connection()
    with conn.cursor() as c:
        c.execute("SELECT 1")
        assert c.fetchone()[0] == 1


def test_sites_migration_consistent():
    from django.db import connection
    connection.ensure_connection()
    with connection.cursor() as c:
        c.execute(
            "SELECT name FROM django_migrations WHERE app='sites' ORDER BY id"
        )
        applied = [r[0] for r in c.fetchall()]
    if "0004_alter_options_ordering_domain" in applied:
        assert "0003_set_site_domain_and_name" in applied, (
            "Inconsistent: 0004 applied but 0003_set_site_domain_and_name missing"
        )


def test_site_record_exists():
    from django.contrib.sites.models import Site
    from django.db import connection
    connection.ensure_connection()
    assert Site.objects.using("default").filter(id=1).exists(), "No Site with id=1"


def test_no_pending_migrations():
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    connection.ensure_connection()
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    assert len(plan) == 0, (
        f"Unapplied migrations: {[str(m) for m, _ in plan[:5]]}"
    )


# ── App registry ──────────────────────────────────────────────────────────────

def test_app_registry_ready():
    from django.apps import apps
    assert apps.ready


def test_wagtail_importable():
    from wagtail.models import Page
    assert Page is not None


def test_allauth_importable():
    import allauth.account
    assert allauth.account is not None


# ── URL resolution ────────────────────────────────────────────────────────────

def test_health_url_resolves():
    from django.urls import NoReverseMatch, reverse
    try:
        url = reverse("health:health")
        assert "/health/" in url
    except NoReverseMatch:
        pytest.skip("health namespace not registered")


def test_admin_url_resolves():
    from django.urls import reverse
    assert "admin" in reverse("admin:index")


def test_pipelines_login_resolves():
    from django.urls import reverse
    assert reverse("pipelines:login")


def test_pipelines_logout_resolves():
    from django.urls import reverse
    assert reverse("pipelines:logout")


def test_pipelines_register_resolves():
    from django.urls import reverse
    assert reverse("pipelines:register")


# ── Static / media ────────────────────────────────────────────────────────────

def test_static_url():
    from django.conf import settings
    assert getattr(settings, "STATIC_URL", None)


def test_media_url():
    from django.conf import settings
    assert getattr(settings, "MEDIA_URL", None)


# ── Security ──────────────────────────────────────────────────────────────────

def test_secret_key_not_trivial():
    from django.conf import settings
    key = settings.SECRET_KEY
    assert key != "django-insecure-default"
    assert len(key) > 20
