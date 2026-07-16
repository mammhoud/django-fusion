#!/usr/bin/env python3
"""
Simple test script to verify group management implementation.
This script tests the RoleHierarchyManager without requiring full Django setup.
"""

import sys
from pathlib import Path

# Add the project to the path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
try:
    from django_fusion.core.managers import GroupAccessControl, RoleHierarchyManager
    print("✓ Successfully imported group management services")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

# Test RoleHierarchyManager
def test_role_hierarchy():
    """Test role hierarchy functionality."""
    manager = RoleHierarchyManager()

    # Test 1: Get permissions for admin role
    admin_perms = manager.get_all_permissions_for_role("admin")
    assert "auth.add_user" in admin_perms, "Admin should have add_user permission"
    assert "auth.view_user" in admin_perms, "Admin should inherit view_user from user role"
    print("✓ Test 1: Admin permissions include inherited permissions")

    # Test 2: Get permissions for supervisor role
    supervisor_perms = manager.get_all_permissions_for_role("supervisor")
    assert "auth.change_user" in supervisor_perms, "Supervisor should have change_user"
    assert "auth.view_user" in supervisor_perms, "Supervisor should inherit view_user"
    assert "auth.add_user" not in supervisor_perms, "Supervisor should not have add_user"
    print("✓ Test 2: Supervisor permissions are correct")

    # Test 3: Get role hierarchy
    admin_hierarchy = manager.get_role_hierarchy("admin")
    assert admin_hierarchy == ["admin", "supervisor", "user"], f"Admin hierarchy incorrect: {admin_hierarchy}"
    print("✓ Test 3: Role hierarchy is correct")

    # Test 4: Get supervisor hierarchy
    supervisor_hierarchy = manager.get_role_hierarchy("supervisor")
    assert supervisor_hierarchy == ["supervisor", "user"], f"Supervisor hierarchy incorrect: {supervisor_hierarchy}"
    print("✓ Test 4: Supervisor hierarchy is correct")

    # Test 5: Get user hierarchy
    user_hierarchy = manager.get_role_hierarchy("user")
    assert user_hierarchy == ["user"], f"User hierarchy incorrect: {user_hierarchy}"
    print("✓ Test 5: User hierarchy is correct")

def test_permission_caching():
    """Test permission caching."""
    manager = RoleHierarchyManager()

    # Get permissions twice
    perms1 = manager.get_all_permissions_for_role("admin")
    perms2 = manager.get_all_permissions_for_role("admin")

    # Should be the same object (cached)
    assert perms1 is perms2, "Permissions should be cached"
    print("✓ Test 6: Permission caching works")

def test_role_permissions_structure():
    """Test that role permissions are properly structured."""
    manager = RoleHierarchyManager()

    # Check that all roles have permissions defined
    for role in ["admin", "supervisor", "user"]:
        perms = manager.get_all_permissions_for_role(role)
        assert len(perms) > 0, f"Role {role} should have permissions"

    print("✓ Test 7: All roles have permissions defined")

if __name__ == "__main__":
    print("Running group management tests...\n")

    try:
        test_role_hierarchy()
        test_permission_caching()
        test_role_permissions_structure()

        print("\n✓ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
