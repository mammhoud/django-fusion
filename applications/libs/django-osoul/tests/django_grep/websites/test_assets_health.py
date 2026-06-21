"""
Simple asset/health checks adapted from structa.cloud expectations.
These are generic and meant to be customized per-site via selectors or by
placing site-specific selectors in tests/selectors/<site>.yml.
"""
import pytest

requests = pytest.importorskip("requests")


@pytest.mark.selenium
def test_static_root_not_500(base_url):
    """Accessing the /static/ root should not return a server error."""
    r = requests.get(base_url + "/static/", timeout=10, allow_redirects=True)
    assert r.status_code < 500, f"/static/ returned server error {r.status_code}"


@pytest.mark.selenium
def test_verify_health_and_assets(base_url):
    """Verify health endpoint and a common asset CSS file (best-effort).
    This test is tolerant to missing files; it primarily guards against server errors.
    """
    r = requests.get(base_url + "/health/", timeout=10)
    assert r.status_code == 200, "/health/ failed"

    # common compiled stylesheet path; may be absent in some sites — just ensure no 500
    css_paths = [
        "/static/styles/main.css",
        "/static/css/main.css",
        "/static/styles/main.min.css",
    ]
    ok = False
    for p in css_paths:
        rr = requests.get(base_url + p, timeout=10, allow_redirects=True)
        if rr.status_code == 200:
            ok = True
            break
    # do not fail if missing — just warn via assertion that no 200 found
    assert rr.status_code < 500, "Trying assets returned server error"
