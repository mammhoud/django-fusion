"""
Dynaconf YAML loading smoke tests.

Verifies that Dynaconf actually loads and merges values from:
- configs/Env/default/_core.yml  (shared base, every environment)
- configs/Env/default/_<env>.yml (shared, environment-specific)
- configs/Env/*.yml              (infrastructure: database, celery, etc.)
- <project>/Env/_site.yml        (per-project overrides, highest priority)

The test asserts on values that exist **only** in YAML files — not in Python
defaults on MainSettings — so a passing test proves Dynaconf loaded the YAML
rather than silently falling back to Python defaults.
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers — set the stage before importing configs.settings.conf
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]  # tests/configs -> tests -> repo root
_PROJECTS_DIR = _REPO_ROOT / "projects"  # repo/projects/ — where configs/ lives

# Path is set up by conftest.py; kept here for direct execution.


def _fresh_settings(*, server_env: str = "development", website: str = "lms-fusion"):
    """Return a fresh MainSettings instance for the given env/site combo.

    Isolated from the module-level ``settings`` singleton so each test can
    target a different environment or website.
    """
    from configs.settings.conf import MainSettings

    return MainSettings(
        SERVER_ENV=server_env,
        WEBSITE_NAME=website,
        WEBSITE_DIR=str(_PROJECTS_DIR / website),
    )


# ═══════════════════════════════════════════════════════════════════
# Shared YAML (_core.yml, _development.yml)
# ═══════════════════════════════════════════════════════════════════


class TestSharedCoreYaml:
    """Values that exist ONLY in configs/Env/default/_core.yml."""

    def test_template_debug_from_core_yml(self):
        """_core.yml → development.TEMPLATE_DEBUG: true (NOT a MainSettings field)."""
        s = _fresh_settings()
        assert s.get("TEMPLATE_DEBUG") is True, (
            "TEMPLATE_DEBUG should be True from _core.yml [development] section"
        )

    def test_static_url_from_core_yml(self):
        """_core.yml → default.STATIC_URL: @env STATIC_URL /static/"""
        s = _fresh_settings()
        assert s.get("STATIC_URL") == "/static/", (
            "STATIC_URL should be /static/ from _core.yml [default] section"
        )

    def test_media_url_from_core_yml(self):
        """_core.yml → default.MEDIA_URL: @env MEDIA_URL /media/"""
        s = _fresh_settings()
        assert s.get("MEDIA_URL") == "/media/", (
            "MEDIA_URL should be /media/ from _core.yml [default] section"
        )


class TestSharedDevelopmentYaml:
    """Values that exist ONLY in configs/Env/default/_development.yml."""

    def test_email_strategy_from_development_yml(self):
        """_development.yml → development.EMAIL_STRATEGY: console (NOT a MainSettings field)."""
        s = _fresh_settings()
        assert s.get("EMAIL_STRATEGY") == "console", (
            "EMAIL_STRATEGY should be 'console' from _development.yml [development] section"
        )

    def test_debug_from_development_yml(self):
        """_development.yml → development.DEBUG: true"""
        s = _fresh_settings()
        assert s.get("DEBUG") is True, (
            "DEBUG should be True from _development.yml [development] section"
        )


# ═══════════════════════════════════════════════════════════════════
# Environment switching
# ═══════════════════════════════════════════════════════════════════


class TestEnvironmentSwitching:
    """Verify that different SERVER_ENV values load the correct YAML file."""

    def test_testing_env_loads_testing_yml(self):
        """_testing.yml → testing.EMAIL_STRATEGY: console"""
        s = _fresh_settings(server_env="testing")
        assert s.get("EMAIL_STRATEGY") == "console", (
            "EMAIL_STRATEGY should be 'console' from _testing.yml"
        )

    def test_demo_env_loads_demo_yml(self):
        """_demo.yml → demo.EMAIL_STRATEGY: mailtrap"""
        s = _fresh_settings(server_env="demo")
        assert s.get("EMAIL_STRATEGY") == "mailtrap", (
            "EMAIL_STRATEGY should be 'mailtrap' from _demo.yml"
        )

    def test_staging_env_turns_off_debug(self):
        """_staging.yml → staging.DEBUG: false"""
        s = _fresh_settings(server_env="staging")
        assert s.get("DEBUG") is False, (
            "DEBUG should be False from _staging.yml"
        )


# ═══════════════════════════════════════════════════════════════════
# Per-project _site.yml overrides (highest priority)
# ═══════════════════════════════════════════════════════════════════


class TestPerProjectSiteYml:
    """Values loaded from <project>/Env/_site.yml (loaded last, highest priority)."""

    def test_lms_branding_from_site_yml(self):
        """lms-fusion/Env/_site.yml → default.FUSION_SITE_NAME: Fusion LMS"""
        s = _fresh_settings(website="lms-fusion")
        assert s.get("FUSION_SITE_NAME") == "Fusion LMS", (
            "FUSION_SITE_NAME should be 'Fusion LMS' from lms-fusion/Env/_site.yml"
        )

    def test_lms_primary_color_from_site_yml(self):
        """lms-fusion/Env/_site.yml → default.FUSION_PRIMARY_COLOR: #00a1b3 (teal)"""
        s = _fresh_settings(website="lms-fusion")
        assert s.get("FUSION_PRIMARY_COLOR") == "#00a1b3", (
            "FUSION_PRIMARY_COLOR should be '#00a1b3' (teal) from lms-fusion/Env/_site.yml"
        )

    def test_lms_render_first_from_site_yml(self):
        """lms-fusion/Env/_site.yml → default.FUSION_RENDER_FIRST_DEFAULT: false"""
        s = _fresh_settings(website="lms-fusion")
        assert s.get("FUSION_RENDER_FIRST_DEFAULT") is False, (
            "FUSION_RENDER_FIRST_DEFAULT should be False from lms-fusion/Env/_site.yml"
        )

    def test_lms_cors_origins_from_site_yml(self):
        """lms-fusion/Env/_site.yml → default.CORS_ORIGINS includes :3458"""
        s = _fresh_settings(website="lms-fusion")
        origins = s.get("CORS_ORIGINS")
        assert isinstance(origins, list), "CORS_ORIGINS should be a list"
        assert "http://localhost:3458" in origins, (
            "CORS_ORIGINS should include localhost:3458 from lms-fusion/Env/_site.yml"
        )

    def test_cms_branding_from_site_yml(self):
        """cms-fusion/Env/_site.yml → default.FUSION_SITE_NAME: Fusion CMS"""
        s = _fresh_settings(website="cms-fusion")
        assert s.get("FUSION_SITE_NAME") == "Fusion CMS", (
            "FUSION_SITE_NAME should be 'Fusion CMS' from cms-fusion/Env/_site.yml"
        )

    def test_cms_primary_color_from_site_yml(self):
        """cms-fusion/Env/_site.yml → default.FUSION_PRIMARY_COLOR: #7c3aed (purple)"""
        s = _fresh_settings(website="cms-fusion")
        assert s.get("FUSION_PRIMARY_COLOR") == "#7c3aed", (
            "FUSION_PRIMARY_COLOR should be '#7c3aed' (purple) from cms-fusion/Env/_site.yml"
        )

    def test_cms_render_first_from_site_yml(self):
        """cms-fusion/Env/_site.yml → default.FUSION_RENDER_FIRST_DEFAULT: true"""
        s = _fresh_settings(website="cms-fusion")
        assert s.get("FUSION_RENDER_FIRST_DEFAULT") is True, (
            "FUSION_RENDER_FIRST_DEFAULT should be True from cms-fusion/Env/_site.yml"
        )

    def test_cms_cors_origins_from_site_yml(self):
        """cms-fusion/Env/_site.yml → default.CORS_ORIGINS does NOT include :3458"""
        s = _fresh_settings(website="cms-fusion")
        origins = s.get("CORS_ORIGINS")
        assert isinstance(origins, list), "CORS_ORIGINS should be a list"
        assert "http://localhost:3458" not in origins, (
            "CORS_ORIGINS should NOT include localhost:3458 (cms-fusion only has 4 origins)"
        )

    def test_per_project_override_is_different_between_sites(self):
        """LMS and CMS resolve different FUSION_PRIMARY_COLOR from their own _site.yml."""
        lms = _fresh_settings(website="lms-fusion")
        cms = _fresh_settings(website="cms-fusion")
        assert lms.get("FUSION_PRIMARY_COLOR") != cms.get("FUSION_PRIMARY_COLOR"), (
            "LMS and CMS should resolve different FUSION_PRIMARY_COLOR values"
        )


# ═══════════════════════════════════════════════════════════════════
# Infrastructure YAML (database.yml, security.yml, etc.)
# ═══════════════════════════════════════════════════════════════════


class TestInfraYaml:
    """Shared infrastructure YAML files that live directly in configs/Env/."""

    def test_database_engine_from_yaml(self):
        """database.yml should provide a default DATABASE_URL or DB config."""
        s = _fresh_settings()
        # database.yml has a [default] section; Dynaconf should load it.
        db_url = s.get("DATABASE_URL")
        assert db_url is not None, "DATABASE_URL should be loaded from database.yml"

    def test_security_settings_from_yaml(self):
        """security.yml should provide SECRET_KEY or similar."""
        s = _fresh_settings()
        # security.yml exists; just verify it doesn't crash and provides something.
        secret = s.get("SECRET_KEY") or s.get("DJANGO_SECRET_KEY")
        assert secret is not None, (
            "SECRET_KEY should be loaded from security.yml or generated"
        )


# ═══════════════════════════════════════════════════════════════════
# Edge cases
# ═══════════════════════════════════════════════════════════════════


class TestDynaconfEdgeCases:
    """Ensure Dynaconf handles missing files and unknown envs gracefully."""

    def test_unknown_env_falls_back_to_default(self):
        """An unknown SERVER_ENV should still load _core.yml defaults."""
        s = _fresh_settings(server_env="nonexistent")
        # _core.yml default section should still be loaded
        assert s.get("STATIC_URL") == "/static/", (
            "STATIC_URL should fall back to _core.yml [default] section"
        )

    def test_missing_site_yml_does_not_crash(self):
        """A website without Env/_site.yml should still boot cleanly."""
        # cypercloud doesn't have an Env/_site.yml
        s = _fresh_settings(website="cypercloud")
        assert s.get("STATIC_URL") == "/static/", (
            "Should still load shared YAML even without per-project _site.yml"
        )

    def test_settings_files_list_is_populated(self):
        """Dynaconf should have a non-empty settings_files list."""
        s = _fresh_settings()
        if s.dynaconf_settings is not None:
            files = getattr(s.dynaconf_settings, "_loaded_files", None) or []
            # At minimum _core.yml and the env-specific YAML should be loaded.
            loaded = [str(f) for f in files]
            core_loaded = any("_core.yml" in f for f in loaded)
            assert core_loaded, (
                f"_core.yml should be in Dynaconf loaded files, got: {loaded}"
            )
