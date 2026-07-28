"""
Test asset health check endpoints for both projects.

This test verifies that the /health/assets/ endpoint returns proper
health status for static and media files.
"""
import pytest
import requests

SITES = {
    "website": {
        "name": "ctc-research.com",
        "base_url": "http://localhost:8270",
        "container": "website"
    },
    "core": {
        "name": "structa.cloud",
        "base_url": "http://localhost:8280",
        "container": "alliance-website"
    }
}


@pytest.mark.parametrize("site_key", ["website", "core"])
def test_asset_health_endpoint_exists(site_key):
    """Asset health check endpoint should return 200 or 503."""
    cfg = SITES[site_key]
    r = requests.get(f"{cfg['base_url']}/health/assets/", allow_redirects=True, timeout=10)

    # Should return either 200 (healthy/degraded) or 503 (unhealthy)
    assert r.status_code in [200, 503], f"Expected 200 or 503, got {r.status_code}"

    # Should return JSON
    assert r.headers.get("Content-Type", "").startswith("application/json")

    # Should have expected structure
    data = r.json()
    assert "status" in data
    assert "checks" in data
    assert "warnings" in data
    assert "errors" in data

    # Status should be one of the expected values
    assert data["status"] in ["ok", "degraded", "unhealthy"]


@pytest.mark.parametrize("site_key", ["website", "core"])
def test_asset_health_checks_structure(site_key):
    """Asset health check should validate expected components."""
    cfg = SITES[site_key]
    r = requests.get(f"{cfg['base_url']}/health/assets/", allow_redirects=True, timeout=10)

    data = r.json()
    checks = data.get("checks", {})

    # Should check static root
    assert "static_root" in checks
    assert "status" in checks["static_root"]

    # Should check media root
    assert "media_root" in checks
    assert "status" in checks["media_root"]

    # Should check webpack bundles
    assert "webpack_bundles" in checks
    assert "status" in checks["webpack_bundles"]


@pytest.mark.parametrize("site_key", ["website", "core"])
def test_asset_health_status_codes(site_key):
    """Asset health check should return appropriate HTTP status codes."""
    cfg = SITES[site_key]
    r = requests.get(f"{cfg['base_url']}/health/assets/", allow_redirects=True, timeout=10)

    data = r.json()
    status = data.get("status")

    # If status is ok or degraded, HTTP status should be 200
    if status in ["ok", "degraded"]:
        assert r.status_code == 200

    # If status is unhealthy, HTTP status should be 503
    elif status == "unhealthy":
        assert r.status_code == 503
