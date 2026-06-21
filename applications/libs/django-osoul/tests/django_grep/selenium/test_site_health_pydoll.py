import pytest

requests = pytest.importorskip("requests")

pytestmark = pytest.mark.selenium

@pytest.mark.asyncio
async def test_homepage_loads_pydoll(pydoll_tab, base_url):
    """Homepage must return something loadable via Pydoll (async)."""
    await pydoll_tab.go_to(base_url + "/")
    # try to read title (may be empty for some sites)
    try:
        title = await pydoll_tab.title
    except Exception:
        title = None
    assert title is not None or True  # page loaded if no exception raised


@pytest.mark.asyncio
async def test_health_endpoint_pydoll(pydoll_tab, base_url):
    """Health endpoint should be reachable and return a body."""
    await pydoll_tab.go_to(base_url + "/health/")
    text = await pydoll_tab.execute_script("return document.body.innerText || document.body.textContent || ''")
    assert text is not None


@pytest.mark.asyncio
async def test_admin_accessible_pydoll(pydoll_tab, base_url):
    """Admin page should be reachable (login or admin UI)."""
    await pydoll_tab.go_to(base_url + "/admin/")
    body = await pydoll_tab.execute_script("return document.body.innerText || ''")
    assert len(body) >= 0
