"""Tests for the django-fusion project config loader (django_fusion.config.project).

The module is Django-free and pure-stdlib (with optional dynaconf vendored
YAML), so these tests build fake project trees with tmp_path and verify layer
precedence and base-URL priority resolution without booting Django.
"""

import os

import pytest

from django_fusion.config.project import (
    ProjectConfig,
    load_config,
    staticfiles_plan,
)


def _make_project(tmp_path, *, with_shared=True, with_env_site=True):
    """Build a minimal project tree with configs/, Env/, and backend/ dirs."""
    project = tmp_path / "projects" / "precis" / "precis-main"
    (project / "configs").mkdir(parents=True)
    (project / "Env").mkdir(parents=True)
    (project / "backend" / "assets" / "static").mkdir(parents=True)
    (project / "assets" / "static" / "css").mkdir(parents=True)
    (project / "frontend" / "public").mkdir(parents=True)

    shared_env = tmp_path / "projects" / "precis" / "configs" / "Env"
    if with_shared:
        (shared_env / "default").mkdir(parents=True)
        (shared_env / "database.yml").write_text(
            "default:\n  DATABASE:\n    engine: django.db.backends.sqlite3\n"
            "production:\n  DATABASE:\n    engine: django.db.backends.postgresql\n"
        )
        (shared_env / "security.yml").write_text("default: {}\n")

    if with_env_site:
        (project / "Env" / "_site.yml").write_text(
            "default:\n  SITE:\n    name: precis-main\n    domain: structa.cloud\n"
            "development:\n  DEBUG: true\n"
        )

    return project


def _make_project_configs(project, content: str, name: str = "site.yml"):
    path = project / "configs" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def test_merges_shared_then_project_then_site(tmp_path):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  SITE:\n    name: precis-main\n    domain: example.org\n  DEBUG: false\n",
        name="defaults.yml",
    )

    config = load_config(project, env="development")

    # Shared database default survives.
    assert config.get("DATABASE.engine") == "django.db.backends.sqlite3"
    # Project configs layer overrides the shared site registry name.
    assert config.get("SITE.name") == "precis-main"
    # The site-level Env/_site.yml layer is the most specific YAML layer and
    # wins over project configs for identity defaults.
    assert config.get("SITE.domain") == "structa.cloud"
    # Env/_site.yml development section supplies DEBUG.
    assert config.get("DEBUG") is True


def test_project_layer_overrides_shared_site_registry(tmp_path):
    project = _make_project(tmp_path)
    config = load_config(project, env="development")
    # With no project configs, the shared Env YAML still provides defaults.
    assert config.get("DATABASE.engine") == "django.db.backends.sqlite3"
    assert config.get("SITE.domain") == "structa.cloud"


def test_environment_section_selection(tmp_path):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  DEBUG: true\n  FEATURE_X: false\n"
        "production:\n  DEBUG: false\n  FEATURE_X: true\n",
        name="defaults.yml",
    )

    dev = load_config(project, env="development")
    prod = load_config(project, env="production")

    assert dev.get("DEBUG") is True
    assert dev.get("FEATURE_X") is False
    assert prod.get("DEBUG") is False
    assert prod.get("FEATURE_X") is True
    # default-section values carry into environments that do not override them.
    assert prod.get("SITE.domain") == "structa.cloud"


def test_dotenv_and_env_vars_win(tmp_path, monkeypatch):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  SITE:\n    domain: structa.cloud\n  DEBUG: true\n",
        name="defaults.yml",
    )
    # Project .env overrides the YAML domain.
    (project / ".env").write_text("SITE_DOMAIN=custom.local\nDJANGO_DEBUG=false\n")

    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", "prod.structa.cloud")

    config = load_config(project, env="development")

    # dotenv scalar keys merge at top level.
    assert config.get("SITE_DOMAIN") == "custom.local"
    # env vars override merged YAML/dotenv values.
    assert config.get("ALLOWED_HOSTS") == "prod.structa.cloud"
    # DJANGO_DEBUG from dotenv maps to the DEBUG key (top-level env overlay).
    assert config.get("DEBUG") == "false"


def test_env_section_keys_use_django_prefix(tmp_path, monkeypatch):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  DEBUG: true\n  SITE:\n    domain: structa.cloud\n",
        name="defaults.yml",
    )
    monkeypatch.setenv("DJANGO_DEBUG", "1")

    config = load_config(project, env="development")
    assert config.get("DEBUG") == "1"


def test_missing_configs_dir_degrades_to_empty(tmp_path):
    project = tmp_path / "some" / "project"
    (project / "frontend").mkdir(parents=True)
    config = load_config(project, env="development")
    assert config.get("anything", "fallback") == "fallback"
    # No config-derived sections exist (only ambient DJANGO_* env vars).
    assert "DATABASE" not in config.as_dict()
    assert "SITE" not in config.as_dict()


def test_get_resolves_at_env_placeholder(tmp_path, monkeypatch):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  ADMIN:\n    wagtailadmin_base_url: '@env WAGTAILADMIN_BASE_URL https://structa.cloud/admin/'\n",
        name="admin.yml",
    )
    monkeypatch.setenv("WAGTAILADMIN_BASE_URL", "https://admin.example.com/")

    config = load_config(project, env="development")
    assert config.get("ADMIN.wagtailadmin_base_url") == "https://admin.example.com/"


# ── base-URL priority resolution ─────────────────────────────────────────────


def test_resolve_matches_domain_and_overlays_site_identity(tmp_path):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  SITE:\n    name: precis-main\n    primary_domain: structa.cloud\n"
        "    domains: [structa.cloud, www.structa.cloud, lms.structa.cloud]\n",
        name="site.yml",
    )

    config = load_config(project, env="development")
    resolved = config.resolve("https://lms.structa.cloud", side="back")

    assert resolved["SITE"]["name"] == "precis-main"
    assert resolved["SITE"]["base_url"] == "https://lms.structa.cloud"
    assert resolved["SITE"]["side"] == "back"


def test_resolve_picks_registry_site_by_domain(tmp_path):
    project = _make_project(tmp_path, with_env_site=False)
    _make_project_configs(
        project,
        "default:\n  SITE:\n    name: precis-main\n    websites:\n"
        "      main:\n        primary_domain: structa.cloud\n"
        "      research:\n        primary_domain: ctc-research.com\n"
        "        admin_url: https://ctc-research.com/admin/\n",
        name="site.yml",
    )

    config = load_config(project, env="development")
    resolved = config.resolve("https://ctc-research.com", side="back")

    assert resolved["SITE"]["primary_domain"] == "ctc-research.com"
    assert resolved["SITE"]["admin_url"] == "https://ctc-research.com/admin/"


def test_resolve_localhost_port_matches_side(tmp_path):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  SITE:\n    name: precis-main\n    primary_domain: structa.cloud\n"
        "    domains: [structa.cloud, localhost]\n"
        "    ports: {front: 3000, back: 8074}\n",
        name="site.yml",
    )

    config = load_config(project, env="development")

    front = config.resolve("http://localhost:3000", side="front")
    back = config.resolve("http://localhost:8074", side="back")

    assert front["SITE"]["side"] == "front"
    assert back["SITE"]["side"] == "back"
    # Both resolve to the same site (default when only one site is present).
    assert front["SITE"]["name"] == "precis-main"
    assert back["SITE"]["name"] == "precis-main"


def test_resolve_no_match_falls_back_to_self_site(tmp_path):
    project = _make_project(tmp_path)
    config = load_config(project, env="development")
    resolved = config.resolve("https://unknown.example.com", side="back")

    # Unknown host: no registry match; base SITE identity stays.
    assert resolved["SITE"]["name"] == "precis-main"
    assert resolved["SITE"]["base_url"] == "https://unknown.example.com"


def test_staticfiles_plan_conventional_layout(tmp_path):
    project = _make_project(tmp_path)
    plan = staticfiles_plan(project)

    assert plan.project_dir == project
    assert plan.output_dir == project / "backend" / "assets" / "staticfiles"
    assert plan.media_dir == project / "backend" / "assets" / "media"
    assert plan.css_path == project / "assets" / "static" / "css" / "fusion.css"
    # Existing conventional read dirs are included.
    assert plan.read_dirs == (
        project / "backend" / "assets" / "static",
        project / "assets" / "static",
        project / "frontend" / "public",
    )
    assert plan.deploy["static_volume"] == "precis-main-static"
    assert "/static/" in plan.render()
    assert "STATIC_ROOT" in plan.render()


def test_staticfiles_plan_overrides_from_section(tmp_path):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  STATIC:\n    output_dir: custom/collected\n"
        "    css_path: custom/css/site.css\n"
        "    deploy:\n      static_volume: my-site-static\n"
        "      custom_key: custom-value\n",
        name="defaults.yml",
    )
    config = load_config(project, env="development")
    plan = staticfiles_plan(project, overrides=config.section("STATIC"))

    assert plan.output_dir == project / "custom" / "collected"
    assert plan.css_path == project / "custom" / "css" / "site.css"
    assert plan.deploy["static_volume"] == "my-site-static"
    assert plan.deploy["custom_key"] == "custom-value"


def test_section_case_tolerance(tmp_path):
    project = _make_project(tmp_path)
    _make_project_configs(
        project,
        "default:\n  ADMIN:\n    panel_path: /django-admin/\n",
        name="admin.yml",
    )
    config = load_config(project, env="development")
    assert config.section("admin") == {"panel_path": "/django-admin/"}
    assert config.section("ADMIN") == {"panel_path": "/django-admin/"}
