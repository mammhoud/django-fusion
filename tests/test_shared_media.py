"""
Shared Media, Local Media, and Running-Server Media Tests
=========================================================

Validates that the ctc-research.com static/media pipeline is wired correctly
from source files through to the shared Nginx media server.

Run with pytest:
    pytest tests/test_shared_media.py -v

Environment variables:
    TEST_CTC_RESEARCH=true|false   (default: true)
    TEST_DOCKER=true|false         (default: false — enables live container checks)
    CTC_BASE_URL=http://localhost:5070
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CORE = PROJECT_ROOT / "core"
PROXY = PROJECT_ROOT / "proxy"
CTC = CORE / "ctc-research"

TEST_DOCKER = os.environ.get("TEST_DOCKER", "false").lower() == "true"
CTC_BASE_URL = os.environ.get("CTC_BASE_URL", "http://localhost:5070")


# ── Helpers ─────────────────────────────────────────────────────────────────

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# ── Shared-Media Configuration Tests ────────────────────────────────────────

class TestSharedMediaConfiguration:
    """Static configuration checks that do not require a running server."""

    def test_nginx_compose_mounts_ctc_staticfiles(self) -> None:
        """shared-media must mount ctc-research staticfiles read-only."""
        compose = PROXY / "docker-compose.nginx.yml"
        text = _read(compose)
        assert "../core/ctc-research/assets/staticfiles:/var/www/sites/ctc-research/static:ro" in text

    def test_nginx_compose_mounts_ctc_media(self) -> None:
        """shared-media must mount ctc-research media read-only."""
        compose = PROXY / "docker-compose.nginx.yml"
        text = _read(compose)
        assert "../core/ctc-research/assets/media:/var/www/media/ctc-research:ro" in text

    def test_nginx_compose_mounts_shared_static(self) -> None:
        """shared-media must mount the workspace shared static files."""
        compose = PROXY / "docker-compose.nginx.yml"
        text = _read(compose)
        assert "../core/assets/static:/var/www/static:ro" in text

    def test_nginx_config_has_ctc_bundle_location(self) -> None:
        """Nginx must have a location for CTC webpack bundles."""
        conf = PROXY / "nginx" / "default.conf"
        text = _read(conf)
        assert "location /static/bundles/ctc-research/ {" in text
        assert "alias /var/www/sites/ctc-research/static/bundles/ctc-research/;" in text

    def test_nginx_config_has_ctc_static_location(self) -> None:
        """Nginx must have a location for CTC site-specific static files."""
        conf = PROXY / "nginx" / "default.conf"
        text = _read(conf)
        assert "location /sites/ctc-research/static/ {" in text
        assert "alias /var/www/sites/ctc-research/static/;" in text

    def test_nginx_config_has_ctc_media_location(self) -> None:
        """Nginx must have a location for CTC site-specific media files."""
        conf = PROXY / "nginx" / "default.conf"
        text = _read(conf)
        assert "location /media/ctc-research/ {" in text
        assert "alias /var/www/media/ctc-research/;" in text

    def test_nginx_config_has_shared_static_fallback(self) -> None:
        """Nginx must have a fallback /static/ location."""
        conf = PROXY / "nginx" / "default.conf"
        text = _read(conf)
        assert "location /static/ {" in text
        assert "alias /var/www/static/;" in text

    def test_nginx_config_has_shared_media_fallback(self) -> None:
        """Nginx must have a fallback /media/ location."""
        conf = PROXY / "nginx" / "default.conf"
        text = _read(conf)
        assert "location /media/ {" in text
        assert "alias /var/www/media/;" in text

    def test_traefik_ctc_routes_static_media_to_shared_media(self) -> None:
        """Traefik must route ctc-research.com /static /media /sites to shared-media."""
        traefik = PROXY / "traefik" / "dynamic" / "ctc-research.yml"
        text = _read(traefik)
        assert "PathPrefix(`/static/`)" in text
        assert "PathPrefix(`/media/`)" in text
        assert "PathPrefix(`/sites/`)" in text
        assert "shared-media:80" in text

    def test_traefik_media_subdomain_routes_to_shared_media(self) -> None:
        """media.ctc-research.com must route to shared-media."""
        traefik = PROXY / "traefik" / "dynamic" / "media-servers.yml"
        text = _read(traefik)
        assert 'Host(`media.ctc-research.com`)' in text
        assert "shared-media:80" in text

    def test_ctc_django_static_root_points_to_staticfiles(self) -> None:
        """Django STATIC_ROOT must end in ctc-research/assets/staticfiles."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert 'STATIC_ROOT = str(settings.get("STATIC_ROOT", ASSETS_DIR / "staticfiles"))' in text

    def test_ctc_django_media_root_points_to_media(self) -> None:
        """Django MEDIA_ROOT must be derived from ctc-research/assets/media."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert "MEDIA_ROOT = str(MEDIA_DIR)" in text
        assert "MEDIA_DIR = ASSETS_DIR / \"media\"" in text

    def test_ctc_django_static_url_is_relative(self) -> None:
        """STATIC_URL must be a relative /static/ path for shared-media compatibility."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert 'STATIC_URL  = settings.get("STATIC_URL", "/static/")' in text

    def test_ctc_django_media_url_is_relative(self) -> None:
        """MEDIA_URL must be a relative /media/ path for shared-media compatibility."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert 'MEDIA_URL  = settings.get("MEDIA_URL", "/media/")' in text

    def test_ctc_docker_compose_mounts_static_and_media_volumes(self) -> None:
        """ctc-research-website container must mount static and media volumes."""
        compose = CTC / "docker-compose.yml"
        text = _read(compose)
        assert "ctc-research-static:/app/ctc-research/static:rw" in text
        assert "ctc-research-media:/app/ctc-research/media:rw" in text


# ── Local Media Serving Tests ────────────────────────────────────────────────

class TestLocalMediaServing:
    """Tests that run against a local Django test client / settings."""

    @pytest.mark.django_db
    def test_static_url_setting(self) -> None:
        """STATIC_URL must be set to /static/."""
        from django.conf import settings
        assert settings.STATIC_URL == "/static/"

    @pytest.mark.django_db
    def test_media_url_setting(self) -> None:
        """MEDIA_URL must be set to /media/."""
        from django.conf import settings
        assert settings.MEDIA_URL == "/media/"

    def test_static_root_default_in_assets_config(self) -> None:
        """STATIC_ROOT default in core/configs/base/assets.py must end with staticfiles."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert 'STATIC_ROOT = str(settings.get("STATIC_ROOT", ASSETS_DIR / "staticfiles"))' in text

    def test_media_root_in_assets_config(self) -> None:
        """MEDIA_ROOT in core/configs/base/assets.py must be derived from MEDIA_DIR."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert "MEDIA_ROOT = str(MEDIA_DIR)" in text

    def test_staticfiles_dirs_include_bundles_in_assets_config(self) -> None:
        """STATICFILES_DIRS in core/configs/base/assets.py must include the webpack bundles directory."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert '(f"bundles/{SITE_NAME}", SITE_BUNDLES_DIR)' in text

    def test_webpack_loader_bundle_dir_name_in_assets_config(self) -> None:
        """WEBPACK_LOADER BUNDLE_DIR_NAME in assets config must match the site bundle folder."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert 'BUNDLE_DIR_NAME: f"bundles/{SITE_NAME}/"' in text or 'BUNDLE_DIR_NAME": f"bundles/{SITE_NAME}/"' in text

    def test_webpack_loader_stats_file_in_assets_config(self) -> None:
        """WEBPACK_LOADER STATS_FILE in assets config must point to the site bundles.json."""
        assets_py = CORE / "configs" / "base" / "assets.py"
        text = _read(assets_py)
        assert 'STATS_FILE:      str(_bundles_json)' in text or 'STATS_FILE":      str(_bundles_json)' in text


# ── Running-Server Media Tests ─────────────────────────────────────────────

class TestRunningServerMedia:
    """Tests that require a running server or Docker container."""

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_shared_media_container_is_running(self) -> None:
        """shared-media container must be running."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=shared-media", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "shared-media" in result.stdout

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_shared_media_container_exposes_static_volume(self) -> None:
        """shared-media container must have CTC staticfiles mounted."""
        result = subprocess.run(
            ["docker", "exec", "shared-media", "ls", f"/var/www/sites/ctc-research/static/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"shared-media cannot list CTC static: {result.stderr}"

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_shared_media_container_exposes_media_volume(self) -> None:
        """shared-media container must have CTC media mounted."""
        result = subprocess.run(
            ["docker", "exec", "shared-media", "ls", f"/var/www/media/ctc-research/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"shared-media cannot list CTC media: {result.stderr}"

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_nginx_config_is_valid_inside_container(self) -> None:
        """nginx -t must pass inside shared-media."""
        result = subprocess.run(
            ["docker", "exec", "shared-media", "nginx", "-t"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"nginx config test failed: {result.stderr}"


# ── Main CLI ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
