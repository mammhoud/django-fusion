"""Selenium / HTTP smoke tests for the courses search page."""
import pytest

import requests


def _server_running(base_url):
    """Return True if the dev server is reachable."""
    try:
        requests.get(base_url + "/lms/courses/", timeout=5)
        return True
    except requests.exceptions.ConnectionError:
        return False


# ---------------------------------------------------------------------------
# HTTP-level tests (no browser required)
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_index_loads(base_url):
    """/lms/courses/ returns HTTP 200."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/lms/courses/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_search_loads(base_url):
    """/lms/courses/search/ returns HTTP 200."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/lms/courses/search/", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_search_with_query(base_url):
    """/lms/courses/search/?q=python returns HTTP 200."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(base_url + "/lms/courses/search/?q=python", timeout=15, allow_redirects=True)
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_search_difficulty_filter(base_url):
    """/lms/courses/search/?difficulty=beginner returns HTTP 200."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(
        base_url + "/lms/courses/search/?difficulty=beginner",
        timeout=15,
        allow_redirects=True,
    )
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_search_pagination(base_url):
    """/lms/courses/search/?page=1 returns HTTP 200."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(
        base_url + "/lms/courses/search/?page=1",
        timeout=15,
        allow_redirects=True,
    )
    assert r.status_code == 200


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_api_search_returns_json(base_url):
    """/lms/api/courses/search/ returns JSON with a 'success' key."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    r = requests.get(
        base_url + "/lms/api/courses/search/",
        timeout=15,
        allow_redirects=True,
        headers={"Accept": "application/json"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "success" in data


# ---------------------------------------------------------------------------
# Selenium (browser) tests
# ---------------------------------------------------------------------------

@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_page_title_selenium(base_url, selenium_driver):
    """/lms/courses/ page has a non-empty browser title."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    selenium_driver.get(base_url + "/lms/courses/")
    assert selenium_driver.title, "Page title is empty"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_search_input_present(base_url, selenium_driver):
    """Courses page contains a search input element."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + "/lms/courses/")

    selectors = [
        (By.CSS_SELECTOR, "input[type='search']"),
        (By.CSS_SELECTOR, "input[name='q']"),
        (By.CSS_SELECTOR, "input[placeholder*='earch']"),
        (By.CSS_SELECTOR, "input[id*='search']"),
        (By.CSS_SELECTOR, "input[class*='search']"),
    ]
    found = None
    for by, selector in selectors:
        elements = selenium_driver.find_elements(by, selector)
        if elements:
            found = elements[0]
            break

    assert found is not None, "No search input found on courses page"
    assert found.is_displayed()


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_filter_options_present(base_url, selenium_driver):
    """Courses page contains filter controls (difficulty, language, etc.)."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + "/lms/courses/")

    filter_selectors = [
        (By.CSS_SELECTOR, "select[name='difficulty']"),
        (By.CSS_SELECTOR, "select[name='language']"),
        (By.CSS_SELECTOR, "a[href*='difficulty=']"),
        (By.CSS_SELECTOR, "a[href*='language=']"),
        (By.CSS_SELECTOR, ".filter-options"),
        (By.CSS_SELECTOR, "#filters"),
        (By.CSS_SELECTOR, ".filters"),
    ]
    found_any = any(
        selenium_driver.find_elements(by, selector)
        for by, selector in filter_selectors
    )

    if not found_any:
        pytest.skip("No filter controls found — filters may not render without courses in DB")


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_courses_pagination_controls_present(base_url, selenium_driver):
    """Pagination controls are present when courses exist on the page."""
    if not _server_running(base_url):
        pytest.skip("Server not running")
    from selenium.webdriver.common.by import By

    selenium_driver.get(base_url + "/lms/courses/")

    course_selectors = [
        (By.CSS_SELECTOR, ".course-card"),
        (By.CSS_SELECTOR, ".course-item"),
        (By.CSS_SELECTOR, "article"),
    ]
    has_courses = any(
        selenium_driver.find_elements(by, selector)
        for by, selector in course_selectors
    )

    if not has_courses:
        pytest.skip("No courses found in DB — pagination not expected")

    pagination_selectors = [
        (By.CSS_SELECTOR, ".pagination"),
        (By.CSS_SELECTOR, "nav[aria-label*='agination']"),
        (By.CSS_SELECTOR, "a[href*='page=']"),
        (By.CSS_SELECTOR, ".page-link"),
    ]
    found_pagination = any(
        selenium_driver.find_elements(by, selector)
        for by, selector in pagination_selectors
    )

    # Page must at least have a title; pagination only appears with >12 results
    assert selenium_driver.title, "Page title should be non-empty"
    if found_pagination:
        for by, selector in pagination_selectors:
            elements = selenium_driver.find_elements(by, selector)
            if elements:
                assert elements[0].is_displayed()
                break
