#!/usr/bin/env python3
"""Browser smoke test for the deployed precis-landing learning flow.

Usage::

    E2E_BASE_URL=http://127.0.0.1:3000 npm run test:e2e

The backend and Astro/proxy must already be running. The test intentionally
uses the real browser road so it catches missing static assets, proxy errors,
HTMX regressions, unsafe external links, and console failures that unit tests
cannot see.
"""
from __future__ import annotations

import json
import os
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen

try:
    from selenium import webdriver
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
except ImportError as exc:  # pragma: no cover - exercised by local setup only
    raise SystemExit(
        "Selenium is required for the deployed browser smoke test. "
        "Install it in the workspace before running npm run test:e2e."
    ) from exc


BASE_URL = os.environ.get("E2E_BASE_URL", "http://127.0.0.1:3000").rstrip("/")
COURSE_TITLE = "Ship Django Products with HTMX and Alpine"
COURSE_PATH = "/learning/course/ship-django-products/"
YOUTUBE_URL = "https://www.youtube.com/@mammhoud"


def wait_for(url: str, timeout: int = 30) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=3) as response:
                if response.status < 400:
                    return
        except (OSError, URLError):
            pass
        time.sleep(0.5)
    raise AssertionError(f"Timed out waiting for {url}")


def check(name: str, condition: bool, detail: str = "") -> None:
    if not condition:
        raise AssertionError(f"{name} failed{': ' + detail if detail else ''}")
    print(f"PASS {name}{': ' + detail if detail else ''}")


def page_contains_course_title(driver) -> bool:
    """Match the visible course title independently of CSS text casing.

    The industrial learning stylesheet uppercases structural headings, while
    Selenium's ``element.text`` reports the rendered text. This keeps the
    smoke test about visible content rather than a presentation detail.
    ""
    body = driver.find_element(By.TAG_NAME, "body")
    rendered = body.text or ""
    return COURSE_TITLE.casefold() in rendered.casefold()


def main() -> int:
    wait_for(f"{BASE_URL}/learning/")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,1000")
    options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

    driver = webdriver.Chrome(options=options)
    checks = 0
    try:
        driver.get(f"{BASE_URL}/learning/")
        wait = WebDriverWait(driver, 20)
        wait.until(page_contains_course_title)
        check("catalog title", True)
        checks += 1

        primary_learning_links = driver.find_elements(
            By.CSS_SELECTOR, "header nav[aria-label='Main'] a[href^='/learning/']"
        )
        check("learning hidden from primary navigation", not primary_learning_links)
        mobile_learning_links = driver.find_elements(
            By.CSS_SELECTOR, "header nav[aria-label='Mobile'] a[href^='/learning/']"
        )
        check("learning hidden from mobile navigation", not mobile_learning_links)
        try:
            with urlopen(f"{BASE_URL}/apis/navigation/", timeout=5) as response:
                navigation = json.load(response)
            api_learning_links = [
                item for item in navigation.get("nav_items", [])
                if item.get("href") == "/learning/"
            ]
        except (OSError, URLError, json.JSONDecodeError) as exc:
            raise AssertionError(f"navigation API unavailable: {exc}") from exc
        check("learning hidden from navigation API", not api_learning_links)
        checks += 3

        youtube = driver.find_elements(By.XPATH, f"//a[@href='{YOUTUBE_URL}']")
        check("catalog YouTube link", bool(youtube))
        check(
            "catalog YouTube security",
            bool(youtube)
            and youtube[0].get_attribute("target") == "_blank"
            and "noopener" in (youtube[0].get_attribute("rel") or "")
            and "noreferrer" in (youtube[0].get_attribute("rel") or ""),
        )
        checks += 2

        course_link = driver.find_element(
            By.CSS_SELECTOR, f"a[href*='{COURSE_PATH}']"
        )
        driver.get(course_link.get_attribute("href"))
        wait.until(lambda current: current.current_url.endswith(COURSE_PATH))
        wait.until(
            lambda current: current.find_elements(
                By.CSS_SELECTOR, "[data-course-module-count='4']"
            )
            and current.find_elements(
                By.CSS_SELECTOR, "[data-course-lesson-count='12']"
            )
        )
        check("course detail URL", driver.current_url.endswith(COURSE_PATH))
        check(
            "course syllabus",
            "syllabus" in (driver.find_element(By.TAG_NAME, "body").text or "").casefold(),
        )
        check(
            "course counts",
            bool(driver.find_elements(By.CSS_SELECTOR, "[data-course-module-count='4']"))
            and bool(driver.find_elements(By.CSS_SELECTOR, "[data-course-lesson-count='12']")),
        )
        check(
            "syllabus accessibility",
            bool(driver.find_elements(By.CSS_SELECTOR, "button[aria-controls^='module-panel-']")),
        )
        detail_youtube = driver.find_elements(By.XPATH, f"//a[@href='{YOUTUBE_URL}']")
        check(
            "detail YouTube security",
            bool(detail_youtube)
            and detail_youtube[0].get_attribute("target") == "_blank"
            and "noopener" in (detail_youtube[0].get_attribute("rel") or "")
            and "noreferrer" in (detail_youtube[0].get_attribute("rel") or ""),
        )
        checks += 5

        driver.get(f"{BASE_URL}/learning/")
        wait.until(lambda current: current.find_element(By.ID, "course-search"))
        search = driver.find_element(By.ID, "course-search")
        search.clear()
        search.send_keys("HTMX")
        search.submit()
        wait.until(page_contains_course_title)
        wait.until(
            lambda current: "q=HTMX" in current.current_url
            and current.find_element(By.ID, "course-list").find_elements(
                By.CSS_SELECTOR, "article.learning-course-card"
            )
        )
        result_cards = driver.find_elements(By.CSS_SELECTOR, "#course-list article.learning-course-card")
        result_text = " ".join(card.text for card in result_cards).casefold()
        check("HTMX course search", COURSE_TITLE.casefold() in result_text)
        check("HTMX search URL", "q=HTMX" in driver.current_url)
        check("HTMX result target", bool(result_cards))
        checks += 3

        browser_errors = [
            entry
            for entry in driver.get_log("browser")
            if entry.get("level") in {"SEVERE", "ERROR"}
        ]
        failed_resources = []
        for entry in driver.get_log("performance"):
            try:
                message = json.loads(entry["message"])["message"]
                if message["method"] != "Network.responseReceived":
                    continue
                response = message["params"]["response"]
                if int(response.get("status", 0)) >= 400:
                    failed_resources.append(
                        {"status": response.get("status"), "url": response.get("url")}
                    )
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
        check("browser console", not browser_errors, json.dumps(browser_errors))
        check("network responses", not failed_resources, json.dumps(failed_resources))
        checks += 2
        print(f"SUMMARY PASS ({checks} checks) base={BASE_URL}")
        return 0
    except TimeoutException as exc:
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            detail = f"url={driver.current_url} body={((body.text or '')[:500])!r}"
        except Exception:  # pragma: no cover - diagnostic fallback
            detail = f"url={driver.current_url}"
        print(f"FAIL browser timeout: {exc}; {detail}", file=sys.stderr)
        return 1
    except AssertionError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    finally:
        driver.quit()


if __name__ == "__main__":
    raise SystemExit(main())
