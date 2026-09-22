"""
Shared Media, Local Media, and Running-Server Media Tests
=========================================================

Validates that the ctc-research.com / lms static/media pipeline is wired
correctly from source files through to the shared assets-proxy Nginx server
(``application/tools/docker-compose.assets.yml`` + ``nginx/assets.conf.template``).

Both Precis sites (precis-ctc, structa.cloud (precis-main)/lms) mount their per-site staticfiles
and media trees into assets-proxy **and** fall back to the monorepo shared
``projects/assets/static`` + ``projects/assets/media`` roots, so every site loads
its shared assets dir at the backend (Django STATICFILES_DIRS/collectstatic) and
the frontend (Nginx/Traefik) with a cross-tree fallback when the per-site file
is missing.

Run with pytest:
    pytest tests/test_shared_media.py -v

Environment variables:
    TEST_CTC_RESEARCH=true|false   (default: true)
    TEST_DOCKER=true|false         (default: false — enables live container checks)
    CTC_BASE_URL=http://localhost:5070
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRECIS = PROJECT_ROOT / "projects" / "precis"
PRECIS_ASSETS_CONFIG = PRECIS / "configs" / "base" / "assets.py"
ASSETS_PROXY_DIR = PROJECT_ROOT / "application" / "tools"
ASSETS_COMPOSE = ASSETS_PROXY_DIR / "docker-compose.assets.yml"
ASSETS_NGINX = ASSETS_PROXY_DIR / "nginx" / "assets.conf.template"
TRAEFIK_DYNAMIC = PROJECT_ROOT / "application" / "proxy" / "configs" / "traefik" / "dynamic"
CTC = PROJECT_ROOT / "projects" / "precis" / "precis-ctc"
CTC_BACKEND_COMPOSE = CTC / "backend" / "docker-compose.yml"
CTC_ASSETS_SETTINGS = CTC / "backend" / "settings" / "assets.py"
SHARED_ASSETS = PROJECT_ROOT / "projects" / "assets"

TEST_DOCKER = os.environ.get("TEST_DOCKER", "false").lower() == "true"
CTC_BASE_URL = os.environ.get("CTC_BASE_URL", "http://localhost:5070")


# ── Helpers ─────────────────────────────────────────────────────────────────

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


# ── Assets-Proxy Configuration Tests ────────────────────────────────────────

class TestSharedMediaConfiguration:
    """Static configuration checks that do not require a running server."""

    def test_assets_compose_mounts_ctc_staticfiles(self) -> None:
        """assets-proxy must mount ctc staticfiles read-only under the ctc-research site path."""
        text = _read(ASSETS_COMPOSE)
        assert "../../projects/precis/precis-ctc/assets/staticfiles:/var/www/sites/ctc-research/static:ro" in text

    def test_assets_compose_mounts_ctc_media(self) -> None:
        """assets-proxy must mount the shared ctc-research media tree read-only."""
        text = _read(ASSETS_COMPOSE)
        assert "../../projects/assets/media/ctc-research:/var/www/media/ctc-research:ro" in text

    def test_assets_compose_mounts_lms_static_and_media(self) -> None:
        """assets-proxy must mount precis-main/lms staticfiles + media for lms.structa.cloud."""
        text = _read(ASSETS_COMPOSE)
        assert "../../projects/structa.cloud/assets/staticfiles:/var/www/sites/lms/static:ro" in text
        assert "../../projects/structa.cloud/assets/media:/var/www/media/lms:ro" in text

    def test_shared_media_dir_exists(self) -> None:
        """The monorepo-shared ctc-research media tree must exist beside the other project media."""
        assert (SHARED_ASSETS / "media" / "ctc-research").is_dir()
        assert (SHARED_ASSETS / "media" / "ctc-research" / "images").is_dir()

    def test_assets_compose_mounts_shared_static(self) -> None:
        """assets-proxy must mount the workspace shared static files."""
        text = _read(ASSETS_COMPOSE)
        assert "../../projects/assets/static:/var/www/static:ro" in text

    def test_assets_compose_runs_assets_proxy_container(self) -> None:
        """The compose file must define the assets-proxy service/container."""
        text = _read(ASSETS_COMPOSE)
        assert "container_name: assets-proxy" in text
        assert "dockerfile: application/tools/nginx/Dockerfile.assets" in text

    def test_nginx_config_has_ctc_path_locations(self) -> None:
        """Nginx must expose path-based /ctc-research/static|media on media.structa.cloud."""
        text = _read(ASSETS_NGINX)
        assert "location /ctc-research/static/ {" in text
        assert "alias /var/www/sites/ctc-research/static/;" in text
        assert "location /ctc-research/media/ {" in text
        assert "alias /var/www/media/ctc-research/;" in text

    def test_nginx_config_has_ctc_bundle_location(self) -> None:
        """Nginx must have a location for CTC webpack bundles."""
        text = _read(ASSETS_NGINX)
        assert "location /bundles/ctc-research/ {" in text
        assert "alias /var/www/sites/ctc-research/static/bundles/ctc-research/;" in text

    def test_nginx_config_has_ctc_media_subdomain(self) -> None:
        """Nginx must serve media.ctc-research.com with static + media aliases."""
        text = _read(ASSETS_NGINX)
        assert "server_name media.ctc-research.com;" in text
        assert "location /static/ {" in text
        assert "alias /var/www/sites/ctc-research/static/;" in text
        assert "location /media/ {" in text
        assert "alias /var/www/media/ctc-research/;" in text

    def test_nginx_config_has_shared_static_fallback(self) -> None:
        """Nginx must have a fallback /static/ root backed by the shared /var/www/static tree."""
        text = _read(ASSETS_NGINX)
        assert "map $host $static_root {" in text
        assert "default /var/www/static;" in text
        assert "alias /var/www/static/;" in text

    def test_nginx_config_has_shared_media_fallback(self) -> None:
        """Nginx must have a fallback /media/ root backed by the shared /var/www/media tree."""
        text = _read(ASSETS_NGINX)
        assert "map $host $media_root {" in text
        assert "default /var/www/media;" in text

    def test_traefik_ctc_routes_static_media_to_assets_proxy(self) -> None:
        """Traefik must route ctc-research.com /static /media /sites to assets-proxy."""
        text = _read(TRAEFIK_DYNAMIC / "ctc-research.yml")
        assert "PathPrefix(`/static/`) || PathPrefix(`/media/`) || PathPrefix(`/sites/`)" in text
        assert "ctc-media:" in text
        assert "http://assets-proxy:80" in text

    def test_traefik_media_subdomain_routes_to_assets_proxy(self) -> None:
        """media.ctc-research.com must route to assets-proxy."""
        text = _read(TRAEFIK_DYNAMIC / "media-servers.yml")
        assert "Host(`media.ctc-research.com`)" in text
        assert "http://assets-proxy:80" in text

    def test_ctc_backend_compose_mounts_shared_media_tree(self) -> None:
        """precis-ctc backend container must mount host staticfiles + the monorepo shared media tree."""
        text = _read(CTC_BACKEND_COMPOSE)
        assert "../assets/staticfiles:/app/precis-ctc/assets/staticfiles:rw" in text
        assert "../../../assets/media/ctc-research:/app/media:rw" in text

    def test_ctc_media_root_defaults_to_shared_tree(self) -> None:
        """CTC settings must default MEDIA_ROOT to the monorepo shared tree (projects/assets/media/ctc-research)."""
        text = _read(CTC_ASSETS_SETTINGS)
        assert 'str(_PROJECTS_ROOT / "assets" / "media" / "ctc-research")' in text
        # Guard against regression to the precis-local rendition-only tree.
        assert 'str(_PROJECTS_DIR / "assets" / "media" / "ctc-research")' not in text

    def test_precis_config_static_root_points_to_staticfiles(self) -> None:
        """Shared Precis config STATIC_ROOT must end in assets/staticfiles."""
        text = _read(PRECIS_ASSETS_CONFIG)
        assert 'STATIC_ROOT = str(settings.get("STATIC_ROOT", ASSETS_DIR / "staticfiles"))' in text

    def test_precis_config_media_root_derived_from_media_dir(self) -> None:
        """Shared Precis config MEDIA_ROOT must default to the site ASSETS_DIR/media tree."""
        text = _read(PRECIS_ASSETS_CONFIG)
        assert "MEDIA_ROOT = str(settings.get(\"MEDIA_ROOT\", str(MEDIA_DIR)))" in text
        assert 'MEDIA_DIR = ASSETS_DIR / "media"' in text

    def test_precis_config_static_and_media_urls_are_relative(self) -> None:
        """STATIC_URL/MEDIA_URL must be relative paths for assets-proxy compatibility."""
        text = _read(PRECIS_ASSETS_CONFIG)
        assert 'settings.get("STATIC_URL", "/static/")' in text
        assert 'settings.get("MEDIA_URL", "/media/")' in text

    def test_precis_config_staticfiles_dirs_include_bundles(self) -> None:
        """STATICFILES_DIRS must include the site + shared webpack bundle directories."""
        text = _read(PRECIS_ASSETS_CONFIG)
        assert '(f"bundles/{SITE_NAME}", SITE_BUNDLES_DIR)' in text
        assert '("bundles/shared", SHARED_BUNDLES_DIR)' in text
        assert 'SHARED_BUNDLES_DIR = BASE_ASSETS_DIR / "bundles" / "shared"' in text

    def test_precis_config_webpack_loader_matches_site_bundles(self) -> None:
        """WEBPACK_LOADER must point at the site bundle folder and bundles.json."""
        text = _read(PRECIS_ASSETS_CONFIG)
        assert 'BUNDLE_DIR_NAME": f"bundles/{SITE_NAME}/"' in text
        assert "STATS_FILE\":      str(_bundles_json)" in text


# ── Local Media Serving Tests ────────────────────────────────────────────────

class TestLocalMediaServing:
    """Tests that run against the workspace test Django settings."""

    def test_static_url_setting(self) -> None:
        """STATIC_URL must be set to /static/."""
        from django.conf import settings
        assert settings.STATIC_URL == "/static/"

    def test_media_url_setting(self) -> None:
        """MEDIA_URL must be set to /media/."""
        from django.conf import settings
        assert settings.MEDIA_URL == "/media/"


# ── Running-Server Media Tests ─────────────────────────────────────────────

class TestRunningServerMedia:
    """Tests that require a running server or Docker container."""

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_assets_proxy_container_is_running(self) -> None:
        """assets-proxy container must be running."""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=assets-proxy", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "assets-proxy" in result.stdout

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_assets_proxy_exposes_ctc_static_volume(self) -> None:
        """assets-proxy container must have CTC staticfiles mounted."""
        result = subprocess.run(
            ["docker", "exec", "assets-proxy", "ls", "/var/www/sites/ctc-research/static/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"assets-proxy cannot list CTC static: {result.stderr}"

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_assets_proxy_exposes_ctc_media_volume(self) -> None:
        """assets-proxy container must have the shared CTC media tree mounted."""
        result = subprocess.run(
            ["docker", "exec", "assets-proxy", "ls", "/var/www/media/ctc-research/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"assets-proxy cannot list CTC media: {result.stderr}"

    @pytest.mark.skipif(not TEST_DOCKER, reason="Set TEST_DOCKER=true to run live container checks")
    def test_nginx_config_is_valid_inside_container(self) -> None:
        """nginx -t must pass inside assets-proxy."""
        result = subprocess.run(
            ["docker", "exec", "assets-proxy", "nginx", "-t"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"nginx config test failed: {result.stderr}"


# ── Main CLI ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
