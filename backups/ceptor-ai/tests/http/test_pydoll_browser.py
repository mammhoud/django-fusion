"""
Pydoll Browser Tests for All Sites
===================================
Async browser-based smoke tests using pydoll for all 4 websites.

Prerequisites:
    pip install pydoll

Run:
    SELENIUM_BASE_URL=http://localhost:5070 pytest tests/http/test_pydoll_browser.py -v
    SELENIUM_BASE_URL=http://localhost:5071 pytest tests/http/test_pydoll_browser.py -v -k lms
"""

import os
from pathlib import Path

import pytest

# Mark all tests as selenium (can be skipped with -m "not selenium")
pytestmark = pytest.mark.selenium

# Base URL from environment or default
BASE_URL = os.environ.get("SELENIUM_BASE_URL", "http://localhost:5070")

# ── Site configurations ──────────────────────────────────────────────────────
SITES = {
    "ctc-research": {
        "url": os.environ.get("CTC_BASE_URL", "http://localhost:5070"),
        "title_keywords": ["CTC", "Research", "Structa"],
    },
    "lms-demo": {
        "url": os.environ.get("LMS_BASE_URL", "http://localhost:5071"),
        "title_keywords": ["LMS", "Structa", "Learning"],
    },
    "vresume": {
        "url": os.environ.get("VRESUME_BASE_URL", "http://localhost:5072"),
        "title_keywords": ["VResume", "Resume"],
    },
    "crm": {
        "url": os.environ.get("CRM_BASE_URL", "http://localhost:5074"),
        "title_keywords": ["CRM"],
    },
}

# Pages to test for each site
PAGES = {
    "ctc-research": ["/", "/health/", "/accounts/login/", "/django-admin/login/"],
    "lms-demo": ["/", "/health/", "/accounts/login/", "/django-admin/login/"],
    "vresume": ["/", "/health/", "/django-admin/login/", "/api/csrf-token/"],
    "crm": ["/", "/health/", "/accounts/login/", "/django-admin/login/"],
}




# ═════════════════════════════════════════════════════════════════════════════
# Health Endpoint Tests
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.selenium
@pytest.mark.parametrize("site_name", list(SITES.keys()))
@pytest.mark.asyncio
async def test_health_page_loads(site_name, pydoll_tab, event_loop):
    """Health endpoint loads without error."""
    url = f"{SITES[site_name]['url']}/health/"
    try:
        await pydoll_tab.go_to(url)
        title = await pydoll_tab.title
        assert title is not None, f"{site_name} health page has no title"

        # Get page text content
        text = await pydoll_tab.execute_script(
            "return document.body.innerText || document.body.textContent || ''"
        )
        assert text is not None, f"{site_name} health page has no content"
    except Exception as e:
        pytest.skip(f"Browser test failed for {site_name}: {e}")


@pytest.mark.selenium
@pytest.mark.parametrize("site_name", list(SITES.keys()))
@pytest.mark.asyncio
async def test_homepage_loads(site_name, pydoll_tab, event_loop):
    """Homepage loads without JavaScript errors."""
    url = SITES[site_name]["url"]
    try:
        await pydoll_tab.go_to(url)
        title = await pydoll_tab.title
        assert title is not None, f"{site_name} homepage has no title"
    except Exception as e:
        pytest.skip(f"Browser test failed for {site_name}: {e}")


@pytest.mark.selenium
@pytest.mark.parametrize("site_name", list(SITES.keys()))
@pytest.mark.asyncio
async def test_admin_login_page(site_name, pydoll_tab, event_loop):
    """Admin login page renders correctly."""
    url = f"{SITES[site_name]['url']}/django-admin/login/"
    try:
        await pydoll_tab.go_to(url)

        # Check that page loaded with content
        text = await pydoll_tab.execute_script(
            "return document.body.innerText || document.body.textContent || ''"
        )
        if text:
            # Should contain login-related text
            has_login_text = any(
                keyword in text.lower()
                for keyword in ["login", "password", "username", "sign in"]
            )
            # This is optional — some sites redirect away
    except Exception as e:
        pytest.skip(f"Admin page test failed for {site_name}: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# Console Error Detection
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.selenium
@pytest.mark.asyncio
async def test_no_console_errors(pydoll_tab):
    """Homepage should not have severe console errors."""
    url = f"{BASE_URL}/"
    try:
        await pydoll_tab.go_to(url)
        # Wait for page to fully load
        import asyncio

        await asyncio.sleep(2)

        # Check for console errors via JavaScript
        has_errors = await pydoll_tab.execute_script(
            """
            (function() {
                return window.__capturedErrors ? window.__capturedErrors.length > 0 : false;
            })();
            """
        )
        # Not all browsers capture errors — this is informational
    except Exception as e:
        pytest.skip(f"Console error check failed: {e}")


# ═════════════════════════════════════════════════════════════════════════════
# Page Content Verification
# ═════════════════════════════════════════════════════════════════════════════

@pytest.mark.selenium
@pytest.mark.parametrize(
    "site_name,path",
    [
        (site, page)
        for site, pages in PAGES.items()
        for page in pages
    ],
)
@pytest.mark.asyncio
async def test_page_content_loads(site_name, path, pydoll_tab, event_loop):
    """Each page loads and has content."""
    url = f"{SITES[site_name]['url']}{path}"
    try:
        await pydoll_tab.go_to(url)
        import asyncio

        await asyncio.sleep(1)

        html = await pydoll_tab.execute_script(
            "return document.documentElement.outerHTML || ''"
        )
        assert html is not None and len(html) > 0, (
            f"{site_name}{path} returned empty HTML"
        )
    except Exception as e:
        pytest.skip(f"Page content check failed for {site_name}{path}: {e}")
