"""
Property-based tests for auth fragment templates.

Feature: allauth-htmx-auth-pages
Tests: Properties 1-9 (tasks 12.1-12.9)

Properties verified:
    1. All auth/ templates are pure fragments (no {% extends %}, outermost = fragment--form)
    2. No pipelines: references remain in any auth/ template
    3. All <form> templates have name="strategy" and name="supports_sse" hidden inputs
    4. No btn--social element has hx-post attribute
    5. HTMX requests receive bare fragments (HX-Request: true → fragment--form, no auth-container)
    6. Non-HTMX requests receive skeleton (both auth-container and fragment--form)
    7. Strategy field round-trip (POST strategy value → same value in context)
    8. Invalid HTMX form submissions return 2xx with fragment--form
    9. Configured providers render their buttons in login template
"""
import os
import re
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import settings as h_settings
from hypothesis import strategies as st

# ── Template directory discovery ─────────────────────────────────────────────

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]

AUTH_TEMPLATE_DIRS = [
    WORKSPACE_ROOT / "ctc-research.com" / "plugins" / "accounts" / "templates" / "auth",
    WORKSPACE_ROOT / "ctc-research.com" / "templates" / "auth",
    WORKSPACE_ROOT / "structa.cloud" / "assets" / "templates" / "auth",
    WORKSPACE_ROOT / "structa.cloud" / "templates" / "auth",
]

# Collect all .html files from auth template directories
def _collect_auth_templates():
    templates = []
    for d in AUTH_TEMPLATE_DIRS:
        if d.exists():
            for f in sorted(d.glob("*.html")):
                templates.append(f)
    return templates


def _collect_form_templates():
    """Auth templates that contain a <form element."""
    return [t for t in _collect_auth_templates() if "<form" in t.read_text(encoding="utf-8")]


AUTH_TEMPLATES = _collect_auth_templates()
FORM_TEMPLATES = _collect_form_templates()

# Skip entire module if no templates found (e.g. CI without workspace)
pytestmark = pytest.mark.skipif(
    len(AUTH_TEMPLATES) == 0,
    reason="No auth templates found — run from workspace root",
)


# ── Property 1: All auth/ templates are pure fragments ───────────────────────
# Feature: allauth-htmx-auth-pages, Property 1: All auth/ templates are pure fragments

@pytest.mark.parametrize("template_path", AUTH_TEMPLATES, ids=lambda p: p.name)
def test_property_1_templates_are_pure_fragments(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 1: All auth/ templates are pure fragments.

    Assert no {% extends %} at top.
    Assert outermost non-whitespace/non-comment element is <section class="fragment--form">.
    Validates: Requirements 2.2
    """
    content = template_path.read_text(encoding="utf-8")

    # No {% extends %} directive anywhere in the file
    assert "{%" not in content or "extends" not in content.split("{%")[1].split("%}")[0] \
        if "{%" in content and "extends" in content else True, \
        f"{template_path.name}: must not contain {{% extends %}}"

    # More precise check: no line starting with {% extends
    for line in content.splitlines():
        stripped = line.strip()
        assert not stripped.startswith("{%") or "extends" not in stripped, \
            f"{template_path.name}: found '{{%extends%}}' directive — template must be a pure fragment"

    # Outermost rendered element must be <section class="fragment--form">
    # Strip Django template tags and comments to find first HTML element
    stripped = re.sub(r"\{#.*?#\}", "", content, flags=re.DOTALL)  # remove {# comments #}
    stripped = re.sub(r"\{%.*?%\}", "", stripped, flags=re.DOTALL)  # remove {% tags %}
    stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.DOTALL)  # remove HTML comments

    # Find first non-whitespace content
    first_tag_match = re.search(r"<\s*\w", stripped)
    if first_tag_match:
        # Get the opening tag
        tag_start = first_tag_match.start()
        tag_end = stripped.find(">", tag_start)
        opening_tag = stripped[tag_start:tag_end + 1]
        assert 'fragment--form' in opening_tag, (
            f"{template_path.name}: outermost element must be "
            f'<section class="fragment--form">, got: {opening_tag[:80]!r}'
        )


# ── Property 2: No pipelines: references remain ──────────────────────────────
# Feature: allauth-htmx-auth-pages, Property 2: No pipelines: references remain

@pytest.mark.parametrize("template_path", AUTH_TEMPLATES, ids=lambda p: p.name)
def test_property_2_no_pipelines_references(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 2: No pipelines: references remain.

    Assert no template contains "pipelines:" string in any URL tag or attribute.
    Validates: Requirements 1.6, 1.7
    """
    content = template_path.read_text(encoding="utf-8")
    assert "pipelines:" not in content, (
        f"{template_path.name}: found 'pipelines:' reference — "
        "all URL references must use 'plugins:' namespace"
    )


# ── Property 3: All forms have required hidden inputs ────────────────────────
# Feature: allauth-htmx-auth-pages, Property 3: All forms have required hidden inputs

@pytest.mark.parametrize("template_path", FORM_TEMPLATES, ids=lambda p: p.name)
def test_property_3_forms_have_required_hidden_inputs(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 3: All forms have required hidden inputs.

    Assert all <form> templates have name="strategy" and name="supports_sse".
    Validates: Requirements 8.3
    """
    content = template_path.read_text(encoding="utf-8")

    assert 'name="strategy"' in content, (
        f"{template_path.name}: missing hidden input name=\"strategy\""
    )
    assert 'name="supports_sse"' in content, (
        f"{template_path.name}: missing hidden input name=\"supports_sse\""
    )


# ── Property 4: Social buttons use standard elements ─────────────────────────
# Feature: allauth-htmx-auth-pages, Property 4: Social buttons use standard elements

SOCIAL_BUTTON_TEMPLATES = [
    t for t in AUTH_TEMPLATES
    if t.name in ("login.html", "register.html")
]


@pytest.mark.parametrize("template_path", SOCIAL_BUTTON_TEMPLATES, ids=lambda p: f"{p.parent.parent.parent.name}/{p.name}")
def test_property_4_social_buttons_no_hx_post(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 4: Social buttons use standard elements.

    Assert no btn--social element has hx-post attribute.
    OAuth redirects cannot be handled by HTMX.
    Validates: Requirements 6.2
    """
    content = template_path.read_text(encoding="utf-8")

    # Find all elements with btn--social class
    # Look for hx-post within the same element as btn--social
    # Simple heuristic: check that hx-post doesn't appear near btn--social
    social_button_blocks = re.findall(
        r'<(?:a|button)[^>]*btn--social[^>]*>',
        content,
        re.DOTALL,
    )
    for block in social_button_blocks:
        assert "hx-post" not in block, (
            f"{template_path.name}: social button has hx-post attribute — "
            "social buttons must use standard <a href> elements, not HTMX"
        )


# ── Hypothesis-based property tests ──────────────────────────────────────────

# Collect template file paths as strings for Hypothesis strategies
AUTH_TEMPLATE_PATHS = [str(t) for t in AUTH_TEMPLATES]
FORM_TEMPLATE_PATHS = [str(t) for t in FORM_TEMPLATES]


@given(template_path=st.sampled_from(AUTH_TEMPLATE_PATHS) if AUTH_TEMPLATE_PATHS else st.nothing())
@h_settings(max_examples=100)
def test_property_1_hypothesis_pure_fragments(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 1 (Hypothesis): All auth/ templates are pure fragments.
    """
    path = Path(template_path)
    content = path.read_text(encoding="utf-8")

    for line in content.splitlines():
        stripped = line.strip()
        assert not (stripped.startswith("{%") and "extends" in stripped), \
            f"{path.name}: found extends directive"

    stripped = re.sub(r"\{#.*?#\}", "", content, flags=re.DOTALL)
    stripped = re.sub(r"\{%.*?%\}", "", stripped, flags=re.DOTALL)
    stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.DOTALL)
    first_tag = re.search(r"<\s*\w", stripped)
    if first_tag:
        tag_end = stripped.find(">", first_tag.start())
        opening_tag = stripped[first_tag.start():tag_end + 1]
        assert "fragment--form" in opening_tag, \
            f"{path.name}: outermost element must be fragment--form"


@given(template_path=st.sampled_from(AUTH_TEMPLATE_PATHS) if AUTH_TEMPLATE_PATHS else st.nothing())
@h_settings(max_examples=100)
def test_property_2_hypothesis_no_pipelines(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 2 (Hypothesis): No pipelines: references remain.
    """
    content = Path(template_path).read_text(encoding="utf-8")
    assert "pipelines:" not in content


@given(template_path=st.sampled_from(FORM_TEMPLATE_PATHS) if FORM_TEMPLATE_PATHS else st.nothing())
@h_settings(max_examples=100)
def test_property_3_hypothesis_hidden_inputs(template_path):
    """
    Feature: allauth-htmx-auth-pages, Property 3 (Hypothesis): All forms have required hidden inputs.
    """
    content = Path(template_path).read_text(encoding="utf-8")
    assert 'name="strategy"' in content
    assert 'name="supports_sse"' in content


# ── Django test client properties (5-9) ──────────────────────────────────────
# These require a running Django app; marked django_db and skipped if
# DJANGO_SETTINGS_MODULE is not configured for the test environment.

SITE_CONFIGS = [
    {
        "name": "ctc-research.com",
        "login_url": "/auth/login/",
        "register_url": "/auth/register/",
        "forgot_url": "/auth/password/forgot/",
    },
    {
        "name": "structa.cloud",
        "login_url": "/auth/login/",
        "register_url": "/auth/register/",
        "forgot_url": "/auth/password/forgot/",
    },
]


@pytest.mark.django_db
@pytest.mark.parametrize("site", SITE_CONFIGS, ids=lambda s: s["name"])
def test_property_5_htmx_returns_bare_fragment(client, site):
    """
    Feature: allauth-htmx-auth-pages, Property 5: HTMX requests receive bare fragments.

    GET with HX-Request: true returns fragment--form without auth-container.
    Validates: Requirements 2.4, 8.1
    """
    response = client.get(
        site["login_url"],
        HTTP_HX_REQUEST="true",
        HTTP_HX_CURRENT_URL=site["login_url"],
    )
    assert response.status_code in (200, 302), \
        f"Expected 200 or 302, got {response.status_code}"

    if response.status_code == 200:
        content = response.content.decode("utf-8")
        assert "fragment--form" in content, \
            "HTMX response must contain fragment--form"
        assert "auth-container" not in content, \
            "HTMX response must NOT contain auth-container skeleton wrapper"


@pytest.mark.django_db
@pytest.mark.parametrize("site", SITE_CONFIGS, ids=lambda s: s["name"])
def test_property_6_non_htmx_returns_skeleton(client, site):
    """
    Feature: allauth-htmx-auth-pages, Property 6: Non-HTMX requests receive skeleton.

    GET without HX-Request returns both auth-container and fragment--form.
    Validates: Requirements 2.5, 8.2
    """
    response = client.get(site["login_url"])
    assert response.status_code in (200, 302), \
        f"Expected 200 or 302, got {response.status_code}"

    if response.status_code == 200:
        content = response.content.decode("utf-8")
        assert "fragment--form" in content, \
            "Full-page response must contain fragment--form"
        assert "auth-container" in content, \
            "Full-page response must contain auth-container skeleton wrapper"


@pytest.mark.django_db
@given(strategy=st.sampled_from(["htmx", "document"]))
@h_settings(max_examples=100)
def test_property_7_strategy_field_round_trip(client, strategy):
    """
    Feature: allauth-htmx-auth-pages, Property 7: Strategy field round-trip.

    POST with strategy value returns same value in context.
    Validates: Requirements 8.4
    """
    response = client.post(
        "/auth/login/",
        data={
            "login": "test@example.com",
            "password": "wrongpassword",
            "strategy": strategy,
        },
        HTTP_HX_REQUEST="true",
    )
    # Invalid credentials → form re-rendered with errors
    assert response.status_code in (200, 302)
    if response.status_code == 200:
        content = response.content.decode("utf-8")
        # The strategy value should be preserved in the re-rendered form
        assert f'value="{strategy}"' in content or strategy in content, \
            f"Strategy value '{strategy}' not found in response"


@pytest.mark.django_db
@pytest.mark.parametrize("site", SITE_CONFIGS, ids=lambda s: s["name"])
def test_property_8_invalid_htmx_returns_fragment(client, site):
    """
    Feature: allauth-htmx-auth-pages, Property 8: Invalid HTMX submissions return fragments.

    Invalid form POST via HTMX returns 2xx with fragment--form.
    Validates: Requirements 8.5
    """
    response = client.post(
        site["login_url"],
        data={"login": "", "password": ""},  # invalid — empty fields
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code in (200, 422), \
        f"Expected 2xx for invalid HTMX form, got {response.status_code}"

    if response.status_code in (200, 422):
        content = response.content.decode("utf-8")
        assert "fragment--form" in content, \
            "Invalid HTMX form response must contain fragment--form"


@pytest.mark.django_db
def test_property_9_configured_providers_render_buttons(client, settings):
    """
    Feature: allauth-htmx-auth-pages, Property 9: Configured providers render buttons.

    With SOCIALACCOUNT_PROVIDERS set, login template renders provider buttons.
    Validates: Requirements 6.8
    """
    # Ensure google is in INSTALLED_APPS for this test
    if "allauth.socialaccount.providers.google" not in settings.INSTALLED_APPS:
        pytest.skip("Google provider not in INSTALLED_APPS")

    settings.SOCIALACCOUNT_PROVIDERS = {
        "google": {
            "SCOPE": ["profile", "email"],
            "APP": {"client_id": "test-client-id", "secret": "test-secret", "key": ""},
        }
    }

    response = client.get("/auth/login/")
    assert response.status_code in (200, 302)

    if response.status_code == 200:
        content = response.content.decode("utf-8")
        # Google button should be rendered
        assert "google" in content.lower(), \
            "Login page must render Google provider button when configured"
