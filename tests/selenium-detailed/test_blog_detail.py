"""Selenium / HTTP smoke tests for the blog detail page."""
import pytest
import requests


def _server_running(base_url):
    """Return True if the dev server is reachable."""
    try:
        requests.get(base_url + "/blog/", timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        return False


def _get_first_post_slug(base_url):
    """
    Fetch the blog index and return the slug of the first post link found,
    or None if no posts exist or the server is unreachable.
    """
    try:
        r = requests.get(base_url + "/blog/", timeout=10, allow_redirects=True)
    except requests.exceptions.ConnectionError:
        return None
    if r.status_code != 200:
        return None
    # Post detail links follow the pattern /blog/<slug>/
    import re
    matches = re.findall(r'href=["\'](?:/blog/)([^/"\']+)/["\']', r.text)
    # Filter out known non-post paths
    excluded = {"tag", "category", "search", "tags", "feed", "api"}
    for slug in matches:
        if slug not in excluded:
            return slug
    return None


# ---------------------------------------------------------------------------
# HTTP-level tests (no browser required)
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_loads_for_known_slug(base_url):
    """Blog detail page returns 200 for a real post or 404 if no posts exist."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    r = requests.get(base_url + f"/blog/{slug}/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_has_post_title(base_url):
    """Blog detail page HTML contains the post title in an <h1>."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    r = requests.get(base_url + f"/blog/{slug}/", timeout=15, allow_redirects=True)
    assert r.status_code == 200
    assert "<h1" in r.text


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_has_comment_section(base_url):
    """Blog detail page HTML contains the comments section."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    r = requests.get(base_url + f"/blog/{slug}/", timeout=15, allow_redirects=True)
    assert r.status_code == 200
    assert 'id="comments-section"' in r.text


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_has_social_share_buttons(base_url):
    """Blog detail page HTML contains social share links."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    r = requests.get(base_url + f"/blog/{slug}/", timeout=15, allow_redirects=True)
    assert r.status_code == 200
    # The social share component renders a .social-share container
    assert "social-share" in r.text
    # At least one known share target should be present
    assert any(
        platform in r.text
        for platform in ("twitter.com", "facebook.com", "linkedin.com", "wa.me")
    )


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_unknown_slug_returns_404(base_url):
    """A non-existent slug returns HTTP 404."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(
        base_url + "/blog/this-slug-does-not-exist-xyz-99999/",
        timeout=15,
        allow_redirects=True,
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Selenium (browser) tests
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_page_title_non_empty(base_url, selenium_driver):
    """Blog detail page has a non-empty browser title."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    selenium_driver.get(base_url + f"/blog/{slug}/")
    assert selenium_driver.title, "Page title is empty"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_post_content_visible(base_url, selenium_driver):
    """Blog detail page shows the post content area."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + f"/blog/{slug}/")
    content = selenium_driver.find_element(By.CSS_SELECTOR, ".blog-detail__richtext")
    assert content is not None
    assert content.is_displayed()


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_comment_form_present(base_url, selenium_driver):
    """Blog detail page has a comment section; if user is authenticated, the form has required fields."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + f"/blog/{slug}/")

    # The comments section must always be present
    comments_section = selenium_driver.find_element(By.ID, "comments-section")
    assert comments_section is not None
    assert comments_section.is_displayed()

    # If the comment form is rendered (authenticated user), verify the textarea
    textareas = selenium_driver.find_elements(By.ID, "comment-content")
    if textareas:
        textarea = textareas[0]
        assert textarea.is_displayed()
        assert textarea.get_attribute("name") == "content"
        assert textarea.get_attribute("required") is not None


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_like_button_present(base_url, selenium_driver):
    """Blog detail page has a like button (enabled or disabled depending on auth state)."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + f"/blog/{slug}/")

    # The like area wraps both the authenticated button and the disabled span
    like_area = selenium_driver.find_element(By.CSS_SELECTOR, ".blog-detail__likes")
    assert like_area is not None
    assert like_area.is_displayed()

    # There should be a heart icon element inside the like area
    heart = like_area.find_elements(By.CSS_SELECTOR, ".bi-heart")
    assert heart, "No heart/like icon found in like area"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_blog_detail_social_share_links_visible(base_url, selenium_driver):
    """Blog detail page renders visible social share links."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    slug = _get_first_post_slug(base_url)
    if slug is None:
        pytest.skip("No blog posts found on index page")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + f"/blog/{slug}/")

    share_container = selenium_driver.find_element(By.CSS_SELECTOR, ".social-share")
    assert share_container is not None
    assert share_container.is_displayed()

    # At least one share link should be present
    share_links = share_container.find_elements(By.TAG_NAME, "a")
    assert share_links, "No share links found in .social-share container"
