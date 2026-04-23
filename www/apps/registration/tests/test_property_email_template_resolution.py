# Feature: auth-allauth-enhancement, Property 4: Email template snippet resolution
"""
Property test: _resolve_template uses snippet body when snippet is present,
and falls back to file template when no active snippet exists.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from unittest.mock import patch

pytestmark = pytest.mark.django_db


@given(
    template_type=st.sampled_from(["registration_confirmation", "signin_success"]),
    subject=st.text(min_size=1, max_size=100),
    body=st.text(min_size=1, max_size=500),
)
@settings(max_examples=50)
def test_resolve_uses_snippet_when_present(template_type, subject, body):
    from www.apps.registration.models import AuthEmailTemplate
    from www.apps.registration.emails import _resolve_template

    # Deactivate any existing snippets
    AuthEmailTemplate.objects.filter(template_type=template_type).update(is_active=False)

    snippet = AuthEmailTemplate.objects.create(
        template_type=template_type,
        subject=subject,
        body_html=body,
        body_text=body,
        is_active=True,
    )

    resolved_subject, html, text = _resolve_template(template_type, "registration/emails/base.html", {})
    assert resolved_subject == subject
    snippet.delete()


@given(
    template_type=st.sampled_from(["registration_confirmation", "signin_success"]),
)
@settings(max_examples=50)
def test_resolve_falls_back_when_no_snippet(template_type):
    from www.apps.registration.models import AuthEmailTemplate
    from www.apps.registration.emails import _resolve_template

    # Ensure no active snippet
    AuthEmailTemplate.objects.filter(template_type=template_type).update(is_active=False)

    fallback = "registration/emails/registration_confirmation.html"
    with patch("apps.accounts.registration.emails._render_to_string", return_value="<p>fallback</p>") as mock_render:
        resolved_subject, html, text = _resolve_template(template_type, fallback, {"subject": "Fallback"})
        mock_render.assert_called_once()
