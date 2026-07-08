# Feature: libs-consolidation, Property 1: Deferred modules are absent after consolidation

"""
Property-based tests for the deduplication step of libs-consolidation.

Validates: Requirements 3.1, 3.2, 3.3, 3.4
"""

import pathlib

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Deduplication map: deferred path (relative to libs/) → canonical import path
# ---------------------------------------------------------------------------

DEDUPLICATION_MAP: dict[str, str] = {
    "django-fusion/src/django_fusion/utils/text.py": "django_fusion.utils.text",
    "django-fusion/src/django_fusion/utils/responses.py": "django_fusion.utils.responses",
    "django-fusion/src/django_fusion/utils/datetime_utils.py": "django_fusion.utils.datetime_utils",
    "django-fusion/src/django_fusion/models/mixins.py": "django_fusion.models.mixins",
    "ceptor-ai/src/ceptor_ai/email/services.py": "ceptor_ai.services.email",
    "ceptor-ai/src/ceptor_ai/management/commands/send_invitations_from_csv.py": (
        "ceptor_ai.management.commands.send_invitations_from_csv"
    ),
    "ceptor-ai/src/ceptor_ai/workflows/orchestrator.py": "ceptor_ai.orchestrator",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def setup_fake_workspace(tmp_path: pathlib.Path, deferred_paths: list[str]) -> None:
    """Create stub files for each deferred path under tmp_path."""
    for rel_path in deferred_paths:
        full_path = tmp_path / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text("# stub\n")


def apply_deduplication(base_path: pathlib.Path, paths: list[str]) -> None:
    """Delete each deferred path under base_path. Missing files are silently ignored (idempotent)."""
    for rel_path in paths:
        target = base_path / rel_path
        try:
            target.unlink()
        except FileNotFoundError:
            pass


# ---------------------------------------------------------------------------
# Property 1: Deferred modules are absent after consolidation
# ---------------------------------------------------------------------------


@given(
    deferred_paths=st.lists(
        st.sampled_from(list(DEDUPLICATION_MAP.keys())),
        min_size=1,
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_deferred_modules_absent(tmp_path: pathlib.Path, deferred_paths: list[str]) -> None:
    """
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

    For any non-empty subset of deferred paths, after apply_deduplication() is called,
    none of those paths should exist under the base directory.
    """
    setup_fake_workspace(tmp_path, deferred_paths)

    # Pre-condition: files were actually created
    for path in deferred_paths:
        assert (tmp_path / path).exists(), f"Setup failed: {path} was not created"

    apply_deduplication(tmp_path, deferred_paths)

    # Post-condition: all deferred files are gone
    for path in deferred_paths:
        assert not (tmp_path / path).exists(), (
            f"Deferred module still exists after deduplication: {path}"
        )


@given(
    deferred_paths=st.lists(
        st.sampled_from(list(DEDUPLICATION_MAP.keys())),
        min_size=1,
    )
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_apply_deduplication_is_idempotent(
    tmp_path: pathlib.Path, deferred_paths: list[str]
) -> None:
    """
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

    Calling apply_deduplication() twice on the same paths should not raise an error
    (missing files are silently ignored).
    """
    setup_fake_workspace(tmp_path, deferred_paths)
    apply_deduplication(tmp_path, deferred_paths)
    # Second call must not raise
    apply_deduplication(tmp_path, deferred_paths)

    for path in deferred_paths:
        assert not (tmp_path / path).exists()
