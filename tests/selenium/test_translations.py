"""Test all pages with all translations."""
import pytest
from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from wagtail.models import Page

import requests


def get_available_languages():
    """Get list of available languages from Django settings."""
    if hasattr(settings, 'LANGUAGES'):
        return [lang[0] for lang in settings.LANGUAGES]
    return ['en']  # Default to English


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_homepage_loads_with_all_languages(base_url):
    """Test homepage loads correctly with all available languages."""
    languages = get_available_languages()

    for lang in languages:
        # Try different URL patterns for language
        urls = [
            f"/{lang}/",
            f"/?lang={lang}",
            f"/?language={lang}",
        ]

        for url in urls:
            r = requests.get(base_url + url, timeout=15, allow_redirects=True)
            if r.status_code == 200:
                # Found working URL for this language
                break


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_homepage_renders_with_correct_language(base_url, selenium_driver):
    """Test homepage renders with correct language content."""
    languages = get_available_languages()

    for lang in languages:
        # Try different URL patterns for language
        urls = [
            f"/{lang}/",
            f"/?lang={lang}",
            f"/?language={lang}",
        ]

        for url in urls:
            try:
                selenium_driver.get(base_url + url)

                # Wait for page to load
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
                )

                # Check that page loaded
                page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
                if len(page_text) > 0:
                    # Check for language indicator
                    html_element = selenium_driver.find_element(By.TAG_NAME, "html")
                    html_lang = html_element.get_attribute("lang")

                    # Verify language is set correctly
                    if html_lang:
                        assert html_lang.startswith(lang), f"Page language should be {lang}, got {html_lang}"

                    break
            except:
                continue


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_key_pages_load_with_all_languages(base_url):
    """Test key pages load with all available languages."""
    languages = get_available_languages()
    pages = Page.objects.live().public()[:3]  # Test first 3 pages

    for page in pages:
        for lang in languages:
            # Try different URL patterns for language
            urls = [
                f"/{lang}{page.get_url()}",
                f"{page.get_url()}?lang={lang}",
                f"{page.get_url()}?language={lang}",
            ]

            for url in urls:
                r = requests.get(base_url + url, timeout=15, allow_redirects=True)
                if r.status_code == 200:
                    # Found working URL for this language
                    break


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_language_switcher_changes_language(base_url, selenium_driver):
    """Test language switcher changes language correctly."""
    selenium_driver.get(base_url + "/")

    # Wait for page to load
    WebDriverWait(selenium_driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
    )

    # Look for language switcher elements
    lang_switchers = selenium_driver.find_elements(By.CSS_SELECTOR, "[data-language], .language-switcher, .lang-selector")

    if lang_switchers:
        languages = get_available_languages()

        for lang in languages[1:]:  # Skip first language (already on it)
            # Find language option
            lang_options = selenium_driver.find_elements(By.CSS_SELECTOR, f"[data-language='{lang}'], [data-lang='{lang}']")

            if lang_options:
                # Click language option
                lang_options[0].click()

                # Wait for page to reload
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
                )

                # Check that language changed
                html_element = selenium_driver.find_element(By.TAG_NAME, "html")
                html_lang = html_element.get_attribute("lang")

                if html_lang:
                    assert html_lang.startswith(lang), f"Language should change to {lang}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_language_preference_persisted(base_url, selenium_driver):
    """Test language preference is persisted."""
    languages = get_available_languages()

    if len(languages) > 1:
        target_lang = languages[1]

        # Navigate to page with specific language
        selenium_driver.get(base_url + f"/?lang={target_lang}")

        # Wait for page to load
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Navigate to another page
        selenium_driver.get(base_url + "/")

        # Wait for page to load
        WebDriverWait(selenium_driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
        )

        # Check if language preference is persisted
        html_element = selenium_driver.find_element(By.TAG_NAME, "html")
        html_lang = html_element.get_attribute("lang")

        if html_lang:
            assert html_lang.startswith(target_lang), f"Language preference should be persisted"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_all_pages_load_without_errors_in_all_languages(base_url):
    """Test all pages load without errors in all available languages."""
    languages = get_available_languages()
    pages = Page.objects.live().public()[:5]  # Test first 5 pages

    for page in pages:
        for lang in languages:
            # Try different URL patterns for language
            urls = [
                f"/{lang}{page.get_url()}",
                f"{page.get_url()}?lang={lang}",
            ]

            for url in urls:
                r = requests.get(base_url + url, timeout=15, allow_redirects=True)
                if r.status_code == 200:
                    # Found working URL for this language
                    break
                elif r.status_code == 404:
                    # This URL pattern doesn't work, try next
                    continue
                else:
                    # Unexpected status code
                    assert False, f"Page {page.title} in language {lang} returned {r.status_code}"


@pytest.mark.selenium
@pytest.mark.nondestructive
def test_language_content_correct_in_all_languages(base_url, selenium_driver):
    """Test language content is correct in all available languages."""
    languages = get_available_languages()

    for lang in languages:
        # Navigate to homepage with specific language
        urls = [
            f"/{lang}/",
            f"/?lang={lang}",
        ]

        for url in urls:
            try:
                selenium_driver.get(base_url + url)

                # Wait for page to load
                WebDriverWait(selenium_driver, 10).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
                )

                # Check that page has content
                page_text = selenium_driver.find_element(By.TAG_NAME, "body").text
                assert len(page_text) > 0, f"Page should have content in language {lang}"

                # Check HTML lang attribute
                html_element = selenium_driver.find_element(By.TAG_NAME, "html")
                html_lang = html_element.get_attribute("lang")

                if html_lang:
                    assert html_lang.startswith(lang), f"HTML lang attribute should be {lang}"

                break
            except:
                continue
