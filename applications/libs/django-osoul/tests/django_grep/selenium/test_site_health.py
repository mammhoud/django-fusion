import pytest

requests = pytest.importorskip("requests")

@pytest.mark.selenium
def test_homepage_loads_http(base_url):
    """Homepage must return HTTP 200 at the base URL (requests-based smoke)."""
    r = requests.get(base_url + "/", timeout=10, allow_redirects=True)
    assert r.status_code == 200, f"Homepage returned {r.status_code}"


@pytest.mark.selenium
def test_health_endpoint_http(base_url):
    r = requests.get(base_url + "/health/", timeout=10)
    assert r.status_code == 200, f"/health/ returned {r.status_code}"


@pytest.mark.selenium
def test_admin_accessible_http(base_url):
    r = requests.get(base_url + "/admin/", timeout=10, allow_redirects=False)
    assert r.status_code in (200, 301, 302), f"/admin/ returned {r.status_code}"
