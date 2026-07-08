"""
Property-based tests for RoleHierarchyManager.

# Feature: core-logic-consolidation-and-app-restructure, Property 3: Permission computation is idempotent
# Feature: core-logic-consolidation-and-app-restructure, Property 4: Role hierarchy always starts with the queried role

Validates: Requirements 11.3, 11.4
"""
import sys
from pathlib import Path

# Add django-fusion src to path so the package can be imported
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import directly from the module to avoid loading the full django_fusion package
# which has dependencies like twilio that may not be installed
from django_fusion.core.managers.role_hierarchy import RoleHierarchyManager
from hypothesis import given, settings
from hypothesis import strategies as st

# Defined roles for Property 4 testing
DEFINED_ROLES = ["admin", "supervisor", "user"]


@given(st.text(min_size=1))
@settings(max_examples=100)
def test_get_all_permissions_idempotent(role: str):
    """
    Property 3: Permission computation is idempotent.

    For any role string (including undefined roles), calling
    RoleHierarchyManager.get_all_permissions_for_role(role) twice in succession
    must return the same set[str]. The result must be deterministic and not
    depend on call order or internal mutable state between calls.

    Validates: Requirements 11.3
    """
    mgr = RoleHierarchyManager()
    result1 = mgr.get_all_permissions_for_role(role)
    result2 = mgr.get_all_permissions_for_role(role)
    assert result1 == result2


@given(st.sampled_from(DEFINED_ROLES))
@settings(max_examples=100)
def test_role_hierarchy_starts_with_role(role: str):
    """
    Property 4: Role hierarchy always starts with the queried role.

    For any role defined in RoleHierarchyManager.ROLE_HIERARCHY,
    get_role_hierarchy(role) must return a list whose first element is role itself.
    The role is always a member of its own hierarchy.

    Validates: Requirements 11.4
    """
    mgr = RoleHierarchyManager()
    hierarchy = mgr.get_role_hierarchy(role)
    assert len(hierarchy) >= 1
    assert hierarchy[0] == role
