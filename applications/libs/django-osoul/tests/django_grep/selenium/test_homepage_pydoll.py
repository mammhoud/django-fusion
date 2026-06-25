import pytest

pytestmark = pytest.mark.selenium

@pytest.mark.asyncio
async def test_homepage_loads_with_pydoll(pydoll_tab, selectors):
    # selectors is loaded YAML for the site
    hero_title_sel = selectors.get("homepage", {}).get("hero_title", "h1")
    # pydoll_tab.go_to expects full URL; tests should set SELENIUM_BASE_URL env var
    await pydoll_tab.go_to("/")
    # pydoll's find API varies; use selector kwarg if available
    try:
        el = await pydoll_tab.find(selector=hero_title_sel, timeout=5)
    except TypeError:
        # fallback to tag_name/css mix depending on API
        el = await pydoll_tab.find(tag_name=hero_title_sel)
    assert el is not None
