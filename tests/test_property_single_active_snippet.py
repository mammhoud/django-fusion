# Feature: ctc-structa-admin-auth-integration, Property 2
"""
Property-based test for the single-active AuthEmailTemplate invariant.

**Validates: Requirements 5.5, 5.11**

For any sequence of AuthEmailTemplate.save() calls that set is_active=True
for a given template_type, after each save the count of records with
is_active=True for that template_type must equal exactly 1.
"""
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from apps.handlers.registration.models import AuthEmailTemplate

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

template_type_strategy = st.sampled_from(
    [choice[0] for choice in AuthEmailTemplate.TemplateType.choices]
)

# Generate a sequence of 1–10 saves, each with is_active=True
save_count_strategy = st.integers(min_value=1, max_value=10)


# ---------------------------------------------------------------------------
# Property 2: Single-active invariant
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True, serialized_rollback=False)
@given(
    template_type=template_type_strategy,
    n_saves=save_count_strategy,
)
@settings(max_examples=100)
def test_single_active_invariant(template_type: str, n_saves: int):
    """
    **Validates: Requirements 5.5, 5.11**

    For any sequence of AuthEmailTemplate saves with is_active=True for a
    given template_type, after each save the count of active records for
    that template_type must equal exactly 1.
    """
    # Clean up any records from previous hypothesis examples
    AuthEmailTemplate.objects.filter(template_type=template_type).delete()

    for i in range(n_saves):
        template = AuthEmailTemplate(
            template_type=template_type,
            subject=f"Subject {i}",
            body_html=f"<p>Body {i}</p>",
            body_text=f"Body {i}",
            is_active=True,
        )
        template.save()

        active_count = AuthEmailTemplate.objects.filter(
            template_type=template_type,
            is_active=True,
        ).count()

        assert active_count == 1, (
            f"After save #{i + 1} for template_type={template_type!r}, "
            f"expected exactly 1 active record but found {active_count}. "
            f"The single-active invariant was violated."
        )
