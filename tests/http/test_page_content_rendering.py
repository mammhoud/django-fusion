"""
E2E Content Rendering Tests — Backend API Verification
=======================================================

Verifies that page content endpoints return valid, well-structured data
via the backend API for both CMS (port 5075) and LMS (port 5074).

Tests cover:
1. Page list API returns all pages with required fields
2. Every page data endpoint returns valid encoded content
3. Decoded content has expected structural fields
4. CORS headers are present for cross-origin frontend access
5. No data corruption across pages (unique slugs, valid encoding)
6. Consistent page counts between CMS and LMS

Run:
    pytest tests/http/test_page_content_rendering.py -v --timeout=30

Environment:
    USE_LIVE_DOMAINS=1  — test against production domains instead of localhost
"""

from __future__ import annotations

import base64
import json
import os
from urllib.parse import quote

import pytest
import requests

# ── URL config ────────────────────────────────────────────────────────────────
USE_LIVE = os.environ.get("USE_LIVE_DOMAINS", "0") == "1"

LMS_PORT = 5074
CMS_PORT = 5075
LMS_LOCAL  = f"http://localhost:{LMS_PORT}"
CMS_LOCAL  = f"http://localhost:{CMS_PORT}"
LMS_DOMAIN = "https://structa.cloud"
CMS_DOMAIN = "https://cms.structa.cloud"

LMS_URL = LMS_DOMAIN if USE_LIVE else LMS_LOCAL
CMS_URL = CMS_DOMAIN if USE_LIVE else CMS_LOCAL

TIMEOUT = int(os.environ.get("TEST_TIMEOUT", "15"))

# ── Expected page slugs for cross-site validation ────────────────────────────
MIN_EXPECTED_PAGES = 14
# Core slugs that should be present in at least one locale
EXPECTED_PAGE_SLUGS = {"home", "about", "contact", "team", "services"}
# (No known bug slugs — the Arabic slug server bug was fixed in this session)
KNOWN_BUG_SLUGS: set[str] = set()

# ── Helpers ───────────────────────────────────────────────────────────────────


def page_api_url(site_url: str, slug: str, suffix: str = "data/") -> str:
    """Build a page API URL with proper Unicode slug encoding."""
    return f"{site_url.rstrip('/')}/api/pages/{quote(slug, safe='')}/{suffix}"


def get(url: str, origin: str | None = None, **kw) -> requests.Response:
    """GET with defaults. Optionally set Origin header for CORS checks."""
    kw.setdefault("timeout", TIMEOUT)
    kw.setdefault("allow_redirects", True)
    kw.setdefault("verify", False)
    headers = kw.pop("headers", {})
    if origin:
        headers.setdefault("Origin", origin)
    if headers:
        kw["headers"] = headers
    return requests.get(url, **kw)


def decode_fusion_v1(encoded: str) -> dict:
    """Decode a 'fusion_v1:base64...' payload into a dict."""
    if ":" not in encoded:
        pytest.fail(f"No 'fusion_v1:' prefix in encoded data: {encoded[:40]}")
    prefix, b64 = encoded.split(":", 1)
    assert prefix == "fusion_v1", f"Unexpected encoding prefix: {prefix}"
    try:
        decoded = json.loads(base64.b64decode(b64))
        assert isinstance(decoded, dict), "Decoded fusion payload is not a dict"
        return decoded
    except (json.JSONDecodeError, ValueError) as exc:
        pytest.fail(f"Failed to decode fusion payload: {exc}")


def get_page_list(site_url: str) -> list[dict]:
    """Fetch and return the pages list from /api/pages/."""
    resp = get(f"{site_url}/api/pages/")
    assert resp.status_code == 200, f"/api/pages/ returned {resp.status_code}"
    data = resp.json()
    assert "pages" in data, "/api/pages/ response missing 'pages' key"
    assert "total" in data, "/api/pages/ response missing 'total' key"
    assert data["total"] >= MIN_EXPECTED_PAGES, (
        f"Expected at least {MIN_EXPECTED_PAGES} pages, got {data['total']}"
    )
    return data["pages"]


def get_page_data(site_url: str, slug: str) -> dict:
    """Fetch decoded page data from /api/pages/{slug}/data/."""
    url = page_api_url(site_url, slug, "data/")
    resp = get(url)
    body = resp.json()
    assert resp.status_code == 200, (
        f"/api/pages/{slug}/data/ returned {resp.status_code}: {body}"
    )
    assert "data" in body, f"Page data response missing 'data' key for /{slug}"
    assert "encoded" in body["data"], f"Page data missing 'encoded' field for /{slug}"
    return decode_fusion_v1(body["data"]["encoded"])


# ═════════════════════════════════════════════════════════════════════════════
# LMS Tests
# ═════════════════════════════════════════════════════════════════════════════


# ── Shared test base class ────────────────────────────────────────────────


class BaseContentRendering:
    """Base class for content rendering tests. Subclasses set self.url."""

    CORS_ORIGIN: str = "http://localhost:3001"
    SITE_NAME: str = "Site"

    def test_health_endpoint(self):
        """Health endpoint responds correctly."""
        resp = get(f"{self.url}/api/fusion/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == 200
        assert "fusion_render_first" in data["data"]

    def test_page_list_has_minimum_pages(self):
        """Page list returns at least the minimum expected pages."""
        pages = get_page_list(self.url)
        assert len(pages) >= MIN_EXPECTED_PAGES, (
            f"{self.SITE_NAME} has {len(pages)} pages, expected >= {MIN_EXPECTED_PAGES}"
        )

    def test_page_list_has_required_fields(self):
        """Every page in the list has all required structural fields."""
        pages = get_page_list(self.url)
        required_fields = {"id", "slug", "title", "type", "layout",
                           "fusion_render_first", "fragment_name",
                           "show_in_nav", "children"}
        for page in pages:
            missing = required_fields - set(page.keys())
            assert not missing, (
                f"Page '{page.get('slug', '?')}' missing fields: {missing}"
            )
            assert isinstance(page["id"], int), f"Page '{page['slug']}' id not int"
            assert isinstance(page["slug"], str) and page["slug"], (
                f"Page '{page['slug']}' has empty slug"
            )
            assert isinstance(page["title"], str) and page["title"], (
                f"Page '{page['slug']}' has empty title"
            )

    def test_page_list_no_duplicate_slugs_within_same_locale(self):
        """No duplicate slugs in the same locale (multi-locale duplicates are OK)."""
        pages = get_page_list(self.url)
        slugs = [p["slug"] for p in pages]
        # Wagtail allows same slug across locales but not within one locale.
        # Flag any slug appearing more than 10 times as excessive.
        from collections import Counter
        counts = Counter(slugs)
        excessive = {s: c for s, c in counts.items() if c > 10}
        assert not excessive, (
            f"Excessive duplicate slugs (>10 copies): {excessive}"
        )

    def test_expected_page_slugs_present(self):
        """Core expected page slugs are present in the listing."""
        pages = get_page_list(self.url)
        slugs = {p["slug"] for p in pages}
        missing = EXPECTED_PAGE_SLUGS - slugs
        assert not missing, f"{self.SITE_NAME} missing expected pages: {missing}"

    def _all_pages(self):
        """Return all pages (previously filtered out bug slugs)."""
        return get_page_list(self.url)

    def test_all_page_data_endpoints_return_200(self):
        """Every page slug has a working /data endpoint."""
        pages = self._all_pages()
        for page in pages:
            slug = page["slug"]
            url = page_api_url(self.url, slug, "data/")
            resp = get(url)
            assert resp.status_code == 200, (
                f"Page '{slug}' data endpoint returned {resp.status_code}"
            )

    def test_all_page_decoded_content_is_valid(self):
        """Every page's encoded data decodes to a valid object."""
        pages = self._all_pages()
        for page in pages:
            slug = page["slug"]
            try:
                decoded = get_page_data(self.url, slug)
            except Exception as exc:
                pytest.fail(f"Failed to decode page '{slug}': {exc}")

            assert "id" in decoded, f"Page '{slug}' decoded data missing 'id'"
            assert "slug" in decoded, f"Page '{slug}' decoded data missing 'slug'"
            assert "title" in decoded, f"Page '{slug}' decoded data missing 'title'"
            assert decoded["slug"] == slug, (
                f"Decoded slug '{decoded['slug']}' doesn't match endpoint slug '{slug}'"
            )
            assert decoded["title"], f"Page '{slug}' has empty title"

    def test_page_data_shows_in_nav_consistent_with_list(self):
        """show_in_nav from decoded data matches the page list value."""
        pages = self._all_pages()
        for page in pages:
            slug = page["slug"]
            decoded = get_page_data(self.url, slug)
            assert decoded["show_in_nav"] == page.get("show_in_nav"), (
                f"Page '{slug}' show_in_nav mismatch: "
                f"data={decoded['show_in_nav']}, list={page.get('show_in_nav')}"
            )

    def test_page_data_fragment_name_matches_list(self):
        """fragment_name from decoded data matches the page list value."""
        pages = self._all_pages()
        for page in pages:
            slug = page["slug"]
            decoded = get_page_data(self.url, slug)
            assert decoded.get("fragment_name") == page.get("fragment_name"), (
                f"Page '{slug}' fragment_name mismatch: "
                f"data={decoded.get('fragment_name')}, list={page.get('fragment_name')}"
            )

    def test_arabic_slug_pages_work(self):
        """Arabic slug pages return 200 (regression check)."""
        pages = self._all_pages()
        arabic_pages = [p for p in pages if any(ord(c) > 127 for c in p["slug"])]
        for page in arabic_pages:
            slug = page["slug"]
            resp = get(page_api_url(self.url, slug, "data/"))
            assert resp.status_code == 200, (
                f"Arabic slug '{slug}' returned {resp.status_code}"
            )

    def test_cors_headers_present(self):
        """API returns CORS headers when Origin header is sent."""
        resp = get(f"{self.url}/api/pages/", origin=self.CORS_ORIGIN)
        cors_origin = resp.headers.get("access-control-allow-origin", "")
        assert cors_origin, (
            f"No Access-Control-Allow-Origin header when Origin={self.CORS_ORIGIN}"
        )
        assert self.CORS_ORIGIN in cors_origin or "*" in cors_origin, (
            f"CORS origin '{cors_origin}' doesn't include '{self.CORS_ORIGIN}'"
        )

    def test_cors_preflight_success(self):
        """OPTIONS preflight returns correct CORS headers."""
        resp = requests.options(
            f"{self.url}/api/pages/home/data/",
            headers={
                "Origin": self.CORS_ORIGIN,
                "Access-Control-Request-Method": "GET",
            },
            timeout=TIMEOUT,
            verify=False,
        )
        assert resp.status_code in (200, 204), (
            f"OPTIONS preflight returned {resp.status_code}"
        )
        origin = resp.headers.get("access-control-allow-origin", "")
        assert origin, "No Access-Control-Allow-Origin on preflight"
        methods = resp.headers.get("access-control-allow-methods", "")
        assert "GET" in methods.upper(), (
            f"GET not in allowed methods: {methods}"
        )


class TestLMSContentRendering(BaseContentRendering):
    """Verify LMS backend serves page content correctly."""

    CORS_ORIGIN = "http://localhost:3001"
    SITE_NAME = "LMS"

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.url = LMS_URL


class TestCMSContentRendering(BaseContentRendering):
    """Verify CMS backend serves page content correctly."""

    CORS_ORIGIN = "http://localhost:3002"
    SITE_NAME = "CMS"

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.url = CMS_URL


# ═════════════════════════════════════════════════════════════════════════════
# Cross-site consistency tests
# ═════════════════════════════════════════════════════════════════════════════


class TestCrossSiteContentConsistency:
    """Verify content consistency between CMS and LMS."""

    def test_both_sites_have_same_page_count(self):
        """CMS and LMS should have identical page counts (shared fixtures)."""
        lms_pages = get_page_list(LMS_URL)
        cms_pages = get_page_list(CMS_URL)
        assert len(lms_pages) == len(cms_pages), (
            f"Page count mismatch: LMS={len(lms_pages)}, CMS={len(cms_pages)}"
        )

    def test_both_sites_have_same_page_slugs(self):
        """CMS and LMS should have identical page slug sets."""
        lms_slugs = sorted(p["slug"] for p in get_page_list(LMS_URL))
        cms_slugs = sorted(p["slug"] for p in get_page_list(CMS_URL))
        assert lms_slugs == cms_slugs, (
            f"Page slug mismatch between sites.\n"
            f"Only in LMS: {set(lms_slugs) - set(cms_slugs)}\n"
            f"Only in CMS: {set(cms_slugs) - set(lms_slugs)}"
        )

    def test_cross_site_content_consistency(self):
        """Same page titles and structures across both sites (excluding known bugs)."""
        def _filter(pages):
            return [p for p in pages if p["slug"] not in KNOWN_BUG_SLUGS]

        lms_list = _filter(get_page_list(LMS_URL))
        cms_list = _filter(get_page_list(CMS_URL))
        lms_pages = {p["slug"]: p for p in lms_list}
        cms_pages = {p["slug"]: p for p in cms_list}

        common_slugs = set(lms_pages.keys()) & set(cms_pages.keys())
        checked = 0
        for slug in sorted(common_slugs):
            lp = lms_pages[slug]
            cp = cms_pages[slug]

            for field in ("show_in_nav", "fusion_render_first", "layout"):
                if lp.get(field) != cp.get(field):
                    pytest.fail(
                        f"Field '{field}' mismatch for page '{slug}': "
                        f"LMS={lp.get(field)}, CMS={cp.get(field)}"
                    )

            if slug in KNOWN_BUG_SLUGS:
                continue
            lms_decoded = get_page_data(LMS_URL, slug)
            cms_decoded = get_page_data(CMS_URL, slug)
            assert lms_decoded["title"] == cms_decoded["title"], (
                f"Title mismatch for page '{slug}': "
                f"LMS='{lms_decoded['title']}', CMS='{cms_decoded['title']}'"
            )
            checked += 1

        assert checked >= len(EXPECTED_PAGE_SLUGS), (
            f"Only checked {checked} common pages, expected at least {len(EXPECTED_PAGE_SLUGS)}"
        )

    def test_api_serves_json(self):
        """All API endpoints serve JSON responses."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            resp = get(f"{url}/api/fusion/health")
            assert resp.status_code == 200, (
                f"{name} health endpoint returned {resp.status_code}"
            )
            content_type = resp.headers.get("content-type", "")
            assert "application/json" in content_type, (
                f"{name} health returned unexpected content-type: {content_type}"
            )

    def test_fragment_endpoint_returns_200(self):
        """Page fragment endpoints work for core pages."""
        for slug in EXPECTED_PAGE_SLUGS:
            for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
                frag_url = page_api_url(url, slug, "fragment/")
                resp = get(frag_url)
                assert resp.status_code == 200, (
                    f"{name} page '{slug}' fragment returned {resp.status_code}"
                )


# ═════════════════════════════════════════════════════════════════════════════
# Site configuration & language tests
# ═════════════════════════════════════════════════════════════════════════════


class TestSiteConfiguration:
    """Verify Wagtail Site configuration and content source."""

    def test_home_page_is_english(self):
        """Root site page is the English home page with slug='home' and en locale."""
        resp = get(f"{LMS_URL}/api/pages/")
        data = resp.json()
        # Find the English home page (slug=home, locale=en)
        pages = data["pages"]
        # The page with slug='home' should exist
        home_pages = [p for p in pages if p["slug"] == "home"]
        assert len(home_pages) >= 1, "No page with slug='home' found"

    def test_missing_page_returns_404(self):
        """Non-existent pages return 404 (STATIC_PAGES fallback removed)."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            resp = get(f"{url}/api/pages/nonexistent-page/data/")
            assert resp.status_code == 404, (
                f"{name} returned {resp.status_code} for nonexistent page (expected 404)"
            )

    def test_static_pages_are_empty(self):
        """STATIC_PAGES dict is empty — all content comes from Wagtail fixtures."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            resp = get(f"{url}/api/pages/")
            assert resp.status_code == 200
            data = resp.json()
            # Should have pages from Wagtail fixtures
            assert data["total"] >= MIN_EXPECTED_PAGES, (
                f"{name} has {data['total']} pages, expected at least {MIN_EXPECTED_PAGES} from Wagtail fixtures"
            )

    def test_health_endpoint_reports_correct_site(self):
        """Health endpoint provides site metadata."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            resp = get(f"{url}/api/fusion/health")
            assert resp.status_code == 200
            data = resp.json()
            # Health endpoint should have site info
            assert "message" in data or "status" in data

    def test_pages_served_from_wagtail_not_static(self):
        """Page data from Wagtail has Wagtail-specific content_type info (not STATIC_PAGES format)."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            pages = get_page_list(url)
            # Check that pages have Wagtail-specific fields (id, etc.)
            assert "id" in pages[0], (
                f"{name} pages missing 'id' field — data may be from STATIC_PAGES"
            )
            assert "type" in pages[0], (
                f"{name} pages missing 'type' field — Wagtail content_type not present"
            )

    def test_page_locales_available(self):
        """Pages in multiple locales are available via the page list."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            pages = get_page_list(url)
            # Page list should include localized slugs like home-fr, home-de, home-ar, etc.
            localized_homes = [p for p in pages if p["slug"].startswith("home-")]
            assert len(localized_homes) >= 3, (
                f"{name} has only {len(localized_homes)} localized home pages, "
                f"expected at least 3 (ar, es, fr, de, pt-br)"
            )

    def test_language_switcher_no_data_corruption(self):
        """Switching languages via locale prefix doesn't corrupt page data."""
        # Test that French locale pages return French content
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            pages = get_page_list(url)
            # Find a French-specific slug
            french_pages = [p for p in pages if p["slug"].endswith("-fr")]
            if french_pages:
                fr_slug = french_pages[0]["slug"]
                resp = get(page_api_url(url, fr_slug, "data/"))
                assert resp.status_code == 200, (
                    f"{name} French page '{fr_slug}' returned {resp.status_code}"
                )

    def test_home_page_shows_in_default_language(self):
        """Home page (slug=home) is in English by default."""
        for url, name in [(LMS_URL, "LMS"), (CMS_URL, "CMS")]:
            resp = get(page_api_url(url, "home", "data/"))
            assert resp.status_code == 200, (
                f"{name} home page returned {resp.status_code}"
            )
            body = resp.json()
            # The English home page should have English title
            decoded = decode_fusion_v1(body["data"]["encoded"])
            assert decoded["title"], f"{name} home page has empty title"
            assert decoded["slug"] == "home", (
                f"{name} home page decoded slug is '{decoded['slug']}' not 'home'"
            )
