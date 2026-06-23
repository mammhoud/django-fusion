"""
Property-based tests for RoleBasedEmailTemplateSelector.

# Feature: core-logic-consolidation-and-app-restructure, Property 1: Template path is always non-empty
# Feature: core-logic-consolidation-and-app-restructure, Property 2: build_context always contains required keys
"""

from crafts_ai.email.templates.template_selector import RoleBasedEmailTemplateSelector
from hypothesis import given, settings
from hypothesis import strategies as st


# Property 1: Template path is always non-empty
# Validates: Requirements 11.1
@given(st.text(min_size=1))
@settings(max_examples=100)
def test_get_template_path_always_non_empty(role: str):
    """For any non-empty role string, get_template_path must return a non-empty string."""
    # Feature: core-logic-consolidation-and-app-restructure, Property 1
    selector = RoleBasedEmailTemplateSelector()
    result = selector.get_template_path(role)
    assert isinstance(result, str), f"Expected str, got {type(result)}"
    assert len(result) > 0, f"Expected non-empty string, got {result!r}"


# Property 2: build_context always contains required keys
# Validates: Requirements 11.2
@given(st.emails(), st.text(min_size=1))
@settings(max_examples=100)
def test_build_context_always_has_required_keys(email: str, role: str):
    """For any valid email and role, build_context must contain all required keys."""
    # Feature: core-logic-consolidation-and-app-restructure, Property 2
    selector = RoleBasedEmailTemplateSelector(
        site_name="Test Site",
        site_url="https://test.example.com",
        support_email="support@test.example.com",
    )
    ctx = selector.build_context(email, role)
    required_keys = ("email", "role", "site_name", "site_url", "support_email")
    for key in required_keys:
        assert key in ctx, f"Missing required key: {key}"
