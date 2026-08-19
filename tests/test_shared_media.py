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
PRECIS = PROJECT_ROOT / "projects" / "precis"
PRECIS_ASSETS_CONFIG = PRECIS / "configs" / "base" / "assets.py"
PROXY = PROJECT_ROOT / "application" / "proxy"
CTC = PROJECT_ROOT / "projects" / "precis" / "precis-ctc"
SHARED_ASSETS = PROJECT_ROOT / "projects" / "assets"

TEST_DOCKER = os.environ.get("TEST_DOCKER", "false").lower() == "true"

# The former CTC shared-proxy topology is no longer part of this checkout.
# Keep those historical checks available for a restored CTC fixture, but do
# not report false failures when the retired project and its proxy layout are
# absent. The Precis-local asset checks below remain active.
LEGACY_CTC_AVAILABLE = CTC.exists()
CTC_BASE_URL = os.environ.get("CTC_BASE_URL", "http://localhost:5070")


# ── Helpers ─────────────────────────────────────────────────────────────────

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# ── Shared-Proxy Configuration Tests ────────────────────────────────────────

@pytest.mark.skipif(
    not LEGACY_CTC_AVAILABLE,
    reason="legacy CTC shared-proxy topology is not present in this checkout",
)
class TestSharedMediaConfiguration:
    """Static configuration checks that do not require a running server."""

    def test_nginx_compose_mounts_ctc_staticfiles(self) -> None:
        """shared-proxy must mount ctc staticfiles read-only under the ctc-research site path."""
        compose = PROXY / "docker-compose.nginx.yml"
        text = _read(compose)
        assert "../projects/precis/precis-ctc/assets/staticfiles:/var/www/sites/ctc-research/static:ro" in text

    def test_nginx_compose_mounts_ctc_media(self) -> None:
        """shared-proxy must mount the shared ctc-research media tree read-only."""
        compose = PROXY / "docker-compose.nginx.yml"
        text = _read(compose)
        assert "../projects/assets/media/ctc-research:/var/www/media/ctc-research:ro" in text

    def test_shared_media_dir_exists(self) -> None:
        """The shared ctc-research media tree must exist beside the other project media."""
        assert (SHARED_ASSETS / "media" / "ctc-research").is_dir()
        assert (SHARED_ASSETS / "media" / "ctc-research" / "images").is_dir()

    def test_nginx_compose_mounts_shared_static(self) -> None:
        """shared-proxy must mount the workspace shared static files."""
        compose = PROXY / "docker-compose.nginx.yml"
        text = _read(compose)
        assert "../projects/assets/static:/var/www/static:ro" in text

    def test_nginx_config_has_ctc_bundle_location(self) -> None:
        """Nginx must have a location for CTC webpack bundles."""
        conf = PROXY / "nginx" / "default.conf.template"
        text = _read(conf)
        assert "location /static/bundles/ctc-research/ {" in text
        assert "alias /var/www/sites/ctc-research/static/bundles/ctc-research/;" in text

    def test_nginx_config_has_ctc_static_location(self) -> None:
        """Nginx must have a location for CTC site-specific static files."""
        conf = PROXY / "nginx" / "default.conf.template"
        text = _read(conf)
        assert "location /sites/ctc-research/static/ {" in text
        assert "alias /var/www/sites/ctc-research/static/;" in text

    def test_nginx_config_has_ctc_media_location(self) -> None:
        """Nginx must have a location for CTC site-specific media files."""
        conf = PROXY / "nginx" / "default.conf.template"
        text = _read(conf)
        assert "location /media/ctc-research/ {" in text
        assert "alias /var/www/media/ctc-research/;" in text

    def test_nginx_config_has_shared_static_fallback(self) -> None:
        """Nginx must have a fallback /static/ location backed by $static_root."""
        conf = PROXY / "nginx" / "default.conf.template"
        text = _read(conf)
        assert "location /static/ {" in text
        assert "alias $static_root/;" in text

    def test_nginx_config_has_shared_media_fallback(self) -> None:
        """Nginx must have a fallback /media/ location backed by $media_root."""
        conf = PROXY / "nginx" / "default.conf.template"
        text = _read(conf)
        assert "location /media/ {" in text
        assert "alias $media_root/;" in text

    def test_traefik_ctc_routes_static_media_to_shared_media(self) -> None:
        """Traefik must route ctc-research.com /static /media /sites to shared-proxy."""
        traefik = PROXY / "traefik" / "dynamic" / "ctc-research.yml"
        text = _read(traefik)
        assert "PathPrefix(`/static/`)" in text
        assert "PathPrefix(`/media/`)" in text
        assert "PathPrefix(`/sites/`)" in text
        assert "shared-proxy:80" in text

    def test_traefik_media_subdomain_routes_to_shared_media(self) -> None:
        """media.ctc-research.com must route to shared-proxy."""
        traefik = PROXY / "traefik" / "dynamic" / "media-servers.yml"
        text = _read(traefik)
        assert 'Host(`media.ctc-research.com`)' in text
        assert "shared-proxy:80" in text

    def test_ctc_django_static_root_points_to_staticfiles(self) -> None:
        """Django STATIC_ROOT must end in precis-ctc/assets/staticfiles."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert 'STATIC_ROOT = str(settings.get("STATIC_ROOT", ASSETS_DIR / "staticfiles"))' in text

    def test_ctc_django_media_root_points_to_media(self) -> None:
        """Django MEDIA_ROOT must be derived from precis-ctc/assets/media."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert "MEDIA_ROOT = str(MEDIA_DIR)" in text
        assert "MEDIA_DIR = ASSETS_DIR / \"media\"" in text

    def test_ctc_django_static_url_is_relative(self) -> None:
        """STATIC_URL must be a relative /static/ path for shared-proxy compatibility."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert 'STATIC_URL  = settings.get("STATIC_URL", "/static/")' in text

    def test_ctc_django_media_url_is_relative(self) -> None:
        """MEDIA_URL must be a relative /media/ path for shared-proxy compatibility."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert 'MEDIA_URL  = settings.get("MEDIA_URL", "/media/")' in text

    def test_ctc_docker_compose_mounts_static_and_media_volumes(self) -> None:
        """precis-ctc-website container must mount static volume + shared media tree."""
        compose = CTC / "docker-compose.yml"
        text = _read(compose)
        assert "precis-ctc-static:/app/precis-ctc/assets/staticfiles:rw" in text
        assert "../../../assets/media/ctc-research:/app/media:rw" in text


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
        """STATIC_ROOT default in the Precis-local backend asset config must end with staticfiles."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert 'STATIC_ROOT = str(settings.get("STATIC_ROOT", ASSETS_DIR / "staticfiles"))' in text

    def test_media_root_in_assets_config(self) -> None:
        """MEDIA_ROOT in the Precis-local backend asset config must be derived from MEDIA_DIR."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert "MEDIA_ROOT = str(MEDIA_DIR)" in text

    def test_staticfiles_dirs_include_bundles_in_assets_config(self) -> None:
        """STATICFILES_DIRS in the Precis-local backend asset config must include the webpack bundles directory."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert '(f"bundles/{SITE_NAME}", SITE_BUNDLES_DIR)' in text

    def test_webpack_loader_bundle_dir_name_in_assets_config(self) -> None:
        """WEBPACK_LOADER BUNDLE_DIR_NAME in assets config must match the site bundle folder."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert 'BUNDLE_DIR_NAME: f"bundles/{SITE_NAME}/"' in text or 'BUNDLE_DIR_NAME": f"bundles/{SITE_NAME}/"' in text

    def test_webpack_loader_stats_file_in_assets_config(self) -> None:
        """WEBPACK_LOADER STATS_FILE in assets config must point to the site bundles.json."""
        assets_py = PRECIS_ASSETS_CONFIG
        text = _read(assets_py)
        assert 'STATS_FILE:      str(_bundles_json)' in text or 'STATS_FILE":      str(_bundles_json)' in text


# ── Running-Server Media Tests ─────────────────────────────────────────────

class TestRunningServerMedia:
    """Tests that require a running server or Docker container."""

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_shared_media_container_is_running(self) -> None:
        """shared-proxy container must be running."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=shared-proxy", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "shared-proxy" in result.stdout

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_shared_media_container_exposes_static_volume(self) -> None:
        """shared-proxy container must have CTC staticfiles mounted."""
        result = subprocess.run(
            ["docker", "exec", "shared-proxy", "ls", f"/var/www/sites/ctc-research/static/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"shared-proxy cannot list CTC static: {result.stderr}"

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_shared_media_container_exposes_media_volume(self) -> None:
        """shared-proxy container must have CTC media mounted."""
        result = subprocess.run(
            ["docker", "exec", "shared-proxy", "ls", f"/var/www/media/ctc-research/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"shared-proxy cannot list CTC media: {result.stderr}"

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_nginx_config_is_valid_inside_container(self) -> None:
        """nginx -t must pass inside shared-proxy."""
        result = subprocess.run(
            ["docker", "exec", "shared-proxy", "nginx", "-t"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"nginx config test failed: {result.stderr}"


# ── Main CLI ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
