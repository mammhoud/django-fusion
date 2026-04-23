# Feature: auth-allauth-enhancement, Property 5: Single-active-per-type invariant
"""
Property test: after any sequence of AuthEmailTemplate saves with is_active=True,
at most one record per template_type is active.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

pytestmark = pytest.mark.django_db


@given(
    template_type=st.sampled_from(["registration_confirmation", "signin_success"]),
    n_saves=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=100)
def test_single_active_per_type(template_type, n_saves):
    from www.apps.registration.models import AuthEmailTemplate

    for i in range(n_saves):
        AuthEmailTemplate.objects.create(
            template_type=template_type,
            subject=f"Subject {i}",
            body_html=f"<p>Body {i}</p>",
            body_text=f"Body {i}",
            is_active=True,
        )
        count = AuthEmailTemplate.objects.filter(
            template_type=template_type, is_active=True
        ).count()
        assert count <= 1, (
            f"Expected at most 1 active {template_type} template, found {count}"
        )
