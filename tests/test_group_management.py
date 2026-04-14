"""
Tests for Django Group and Role Management

Tests the creation of groups from CSV, permission inheritance,
role hierarchy, and group-based access control.
"""

import csv
import tempfile
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import TestCase

User = get_user_model()


class TestRoleHierarchyManager(TestCase):
    """Test role hierarchy and permission inheritance."""

    def setUp(self):
        # Import here to avoid Django setup issues
        from apps.handlers.services.groups import RoleHierarchyManager
        self.manager = RoleHierarchyManager()

    def test_get_all_permissions_for_role(self):
        """Test that permissions are inherited from child roles."""
        # Admin should have all permissions
        admin_perms = self.manager.get_all_permissions_for_role("admin")
        self.assertIn("auth.add_user", admin_perms)
        self.assertIn("auth.change_user", admin_perms)
        self.assertIn("auth.view_user", admin_perms)  # Inherited from user role

        # Supervisor should have supervisor and user permissions
        supervisor_perms = self.manager.get_all_permissions_for_role("supervisor")
        self.assertIn("auth.change_user", supervisor_perms)
        self.assertIn("auth.view_user", supervisor_perms)  # Inherited from user role
        self.assertNotIn("auth.add_user", supervisor_perms)  # Not in supervisor

        # User should only have user permissions
        user_perms = self.manager.get_all_permissions_for_role("user")
        self.assertIn("auth.view_user", user_perms)
        self.assertNotIn("auth.change_user", user_perms)

    def test_get_role_hierarchy(self):
        """Test that role hierarchy is correctly retrieved."""
        admin_hierarchy = self.manager.get_role_hierarchy("admin")
        self.assertEqual(admin_hierarchy, ["admin", "supervisor", "user"])

        supervisor_hierarchy = self.manager.get_role_hierarchy("supervisor")
        self.assertEqual(supervisor_hierarchy, ["supervisor", "user"])

        user_hierarchy = self.manager.get_role_hierarchy("user")
        self.assertEqual(user_hierarchy, ["user"])

    def test_create_or_update_group(self):
        """Test group creation with permissions."""
        group, created = self.manager.create_or_update_group("admin")
        self.assertTrue(created)
        self.assertEqual(group.name, "admin")

        # Check that permissions were assigned
        self.assertGreater(group.permissions.count(), 0)

        # Update the group
        group2, created2 = self.manager.create_or_update_group("admin")
        self.assertFalse(created2)
        self.assertEqual(group.id, group2.id)

    def test_assign_user_to_role(self):
        """Test assigning a user to a role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Assign user to supervisor role
        self.manager.assign_user_to_role(user, "supervisor")

        # User should be in supervisor and user groups
        user_groups = set(user.groups.values_list("name", flat=True))
        self.assertIn("supervisor", user_groups)
        self.assertIn("user", user_groups)

    def test_assign_user_to_multiple_roles(self):
        """Test assigning a user to multiple roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Assign user to multiple roles
        self.manager.assign_user_to_multiple_roles(user, ["admin", "supervisor"])

        # User should be in all roles
        user_groups = set(user.groups.values_list("name", flat=True))
        self.assertIn("admin", user_groups)
        self.assertIn("supervisor", user_groups)
        self.assertIn("user", user_groups)

    def test_get_user_roles(self):
        """Test retrieving user roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "admin")

        roles = self.manager.get_user_roles(user)
        self.assertIn("admin", roles)

    def test_get_user_permissions(self):
        """Test retrieving user permissions."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "user")

        permissions = self.manager.get_user_permissions(user)
        self.assertIn("auth.view_user", permissions)

    def test_has_role(self):
        """Test checking if user has a role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "supervisor")

        self.assertTrue(self.manager.has_role(user, "supervisor"))
        self.assertTrue(self.manager.has_role(user, "user"))
        self.assertFalse(self.manager.has_role(user, "admin"))

    def test_has_permission(self):
        """Test checking if user has a permission."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "user")

        self.assertTrue(self.manager.has_permission(user, "auth.view_user"))
        self.assertFalse(self.manager.has_permission(user, "auth.change_user"))


class TestGroupAccessControl(TestCase):
    """Test group-based access control."""

    def setUp(self):
        from apps.handlers.services.groups import RoleHierarchyManager
        self.manager = RoleHierarchyManager()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_check_group_access(self):
        """Test checking group access."""
        self.manager.assign_user_to_role(self.user, "supervisor")

        # User should have access to supervisor and user groups
        self.assertTrue(
            GroupAccessControl.check_group_access(self.user, ["supervisor"])
        )
        self.assertTrue(GroupAccessControl.check_group_access(self.user, ["user"]))
        self.assertFalse(
            GroupAccessControl.check_group_access(self.user, ["admin"])
        )

    def test_check_role_access(self):
        """Test checking role access."""
        self.manager.assign_user_to_role(self.user, "supervisor")

        self.assertTrue(GroupAccessControl.check_role_access(self.user, "supervisor"))
        self.assertTrue(GroupAccessControl.check_role_access(self.user, "user"))
        self.assertFalse(GroupAccessControl.check_role_access(self.user, "admin"))

    def test_get_accessible_groups(self):
        """Test getting accessible groups."""
        self.manager.assign_user_to_role(self.user, "supervisor")

        groups = GroupAccessControl.get_accessible_groups(self.user)
        group_names = [g.name for g in groups]

        self.assertIn("supervisor", group_names)
        self.assertIn("user", group_names)
        self.assertNotIn("admin", group_names)

    def test_superuser_access(self):
        """Test that superusers have access to all groups."""
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        # Superuser should have access to all groups
        self.assertTrue(
            GroupAccessControl.check_group_access(superuser, ["admin"])
        )
        self.assertTrue(
            GroupAccessControl.check_group_access(superuser, ["supervisor"])
        )
        self.assertTrue(GroupAccessControl.check_group_access(superuser, ["user"]))


class TestCreateGroupsFromCSV(TestCase):
    """Test creating groups from CSV file."""

    def setUp(self):
        from apps.handlers.services.groups import RoleHierarchyManager
        self.manager = RoleHierarchyManager()

    def test_create_groups_from_csv(self):
        """Test creating groups from CSV data."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["email", "role"])
            writer.writeheader()
            writer.writerow({"email": "admin@example.com", "role": "admin"})
            writer.writerow(
                {"email": "supervisor@example.com", "role": "supervisor"}
            )
            writer.writerow({"email": "user@example.com", "role": "user"})
            csv_file = f.name

        try:
            # Create groups
            roles = {"admin", "supervisor", "user"}
            for role in roles:
                group, created = self.manager.create_or_update_group(role)
                self.assertTrue(created)
                self.assertEqual(group.name, role)

            # Verify groups were created
            self.assertEqual(Group.objects.count(), 3)
        finally:
            Path(csv_file).unlink()

    def test_hierarchical_roles_in_csv(self):
        """Test handling hierarchical roles like 'admin/supervisor'."""
        # Create a temporary CSV file with hierarchical roles
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["email", "role"])
            writer.writeheader()
            writer.writerow(
                {"email": "user@example.com", "role": "admin/supervisor"}
            )
            csv_file = f.name

        try:
            # Parse roles
            roles = set()
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    role = row.get("role", "").strip()
                    if role:
                        for r in role.split("/"):
                            roles.add(r.strip())

            # Create groups
            for role in roles:
                group, created = self.manager.create_or_update_group(role)
                self.assertTrue(created)

            # Verify groups were created
            self.assertEqual(Group.objects.count(), 2)
            self.assertTrue(Group.objects.filter(name="admin").exists())
            self.assertTrue(Group.objects.filter(name="supervisor").exists())
        finally:
            Path(csv_file).unlink()


class TestRoleHierarchyManager(TestCase):
    """Test role hierarchy and permission inheritance."""

    def setUp(self):
        self.manager = RoleHierarchyManager()

    def test_get_all_permissions_for_role(self):
        """Test that permissions are inherited from child roles."""
        # Admin should have all permissions
        admin_perms = self.manager.get_all_permissions_for_role("admin")
        self.assertIn("auth.add_user", admin_perms)
        self.assertIn("auth.change_user", admin_perms)
        self.assertIn("auth.view_user", admin_perms)  # Inherited from user role

        # Supervisor should have supervisor and user permissions
        supervisor_perms = self.manager.get_all_permissions_for_role("supervisor")
        self.assertIn("auth.change_user", supervisor_perms)
        self.assertIn("auth.view_user", supervisor_perms)  # Inherited from user role
        self.assertNotIn("auth.add_user", supervisor_perms)  # Not in supervisor

        # User should only have user permissions
        user_perms = self.manager.get_all_permissions_for_role("user")
        self.assertIn("auth.view_user", user_perms)
        self.assertNotIn("auth.change_user", user_perms)

    def test_get_role_hierarchy(self):
        """Test that role hierarchy is correctly retrieved."""
        admin_hierarchy = self.manager.get_role_hierarchy("admin")
        self.assertEqual(admin_hierarchy, ["admin", "supervisor", "user"])

        supervisor_hierarchy = self.manager.get_role_hierarchy("supervisor")
        self.assertEqual(supervisor_hierarchy, ["supervisor", "user"])

        user_hierarchy = self.manager.get_role_hierarchy("user")
        self.assertEqual(user_hierarchy, ["user"])

    def test_create_or_update_group(self):
        """Test group creation with permissions."""
        group, created = self.manager.create_or_update_group("admin")
        self.assertTrue(created)
        self.assertEqual(group.name, "admin")

        # Check that permissions were assigned
        self.assertGreater(group.permissions.count(), 0)

        # Update the group
        group2, created2 = self.manager.create_or_update_group("admin")
        self.assertFalse(created2)
        self.assertEqual(group.id, group2.id)

    def test_assign_user_to_role(self):
        """Test assigning a user to a role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Assign user to supervisor role
        self.manager.assign_user_to_role(user, "supervisor")

        # User should be in supervisor and user groups
        user_groups = set(user.groups.values_list("name", flat=True))
        self.assertIn("supervisor", user_groups)
        self.assertIn("user", user_groups)

    def test_assign_user_to_multiple_roles(self):
        """Test assigning a user to multiple roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        # Assign user to multiple roles
        self.manager.assign_user_to_multiple_roles(user, ["admin", "supervisor"])

        # User should be in all roles
        user_groups = set(user.groups.values_list("name", flat=True))
        self.assertIn("admin", user_groups)
        self.assertIn("supervisor", user_groups)
        self.assertIn("user", user_groups)

    def test_get_user_roles(self):
        """Test retrieving user roles."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "admin")

        roles = self.manager.get_user_roles(user)
        self.assertIn("admin", roles)

    def test_get_user_permissions(self):
        """Test retrieving user permissions."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "user")

        permissions = self.manager.get_user_permissions(user)
        self.assertIn("auth.view_user", permissions)

    def test_has_role(self):
        """Test checking if user has a role."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "supervisor")

        self.assertTrue(self.manager.has_role(user, "supervisor"))
        self.assertTrue(self.manager.has_role(user, "user"))
        self.assertFalse(self.manager.has_role(user, "admin"))

    def test_has_permission(self):
        """Test checking if user has a permission."""
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

        self.manager.assign_user_to_role(user, "user")

        self.assertTrue(self.manager.has_permission(user, "auth.view_user"))
        self.assertFalse(self.manager.has_permission(user, "auth.change_user"))


class TestGroupAccessControl(TestCase):
    """Test group-based access control."""

    def setUp(self):
        self.manager = RoleHierarchyManager()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_check_group_access(self):
        """Test checking group access."""
        self.manager.assign_user_to_role(self.user, "supervisor")

        # User should have access to supervisor and user groups
        self.assertTrue(
            GroupAccessControl.check_group_access(self.user, ["supervisor"])
        )
        self.assertTrue(GroupAccessControl.check_group_access(self.user, ["user"]))
        self.assertFalse(
            GroupAccessControl.check_group_access(self.user, ["admin"])
        )

    def test_check_role_access(self):
        """Test checking role access."""
        self.manager.assign_user_to_role(self.user, "supervisor")

        self.assertTrue(GroupAccessControl.check_role_access(self.user, "supervisor"))
        self.assertTrue(GroupAccessControl.check_role_access(self.user, "user"))
        self.assertFalse(GroupAccessControl.check_role_access(self.user, "admin"))

    def test_get_accessible_groups(self):
        """Test getting accessible groups."""
        self.manager.assign_user_to_role(self.user, "supervisor")

        groups = GroupAccessControl.get_accessible_groups(self.user)
        group_names = [g.name for g in groups]

        self.assertIn("supervisor", group_names)
        self.assertIn("user", group_names)
        self.assertNotIn("admin", group_names)

    def test_superuser_access(self):
        """Test that superusers have access to all groups."""
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        # Superuser should have access to all groups
        self.assertTrue(
            GroupAccessControl.check_group_access(superuser, ["admin"])
        )
        self.assertTrue(
            GroupAccessControl.check_group_access(superuser, ["supervisor"])
        )
        self.assertTrue(GroupAccessControl.check_group_access(superuser, ["user"]))


class TestCreateGroupsFromCSV(TestCase):
    """Test creating groups from CSV file."""

    def setUp(self):
        self.manager = RoleHierarchyManager()

    def test_create_groups_from_csv(self):
        """Test creating groups from CSV data."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["email", "role"])
            writer.writeheader()
            writer.writerow({"email": "admin@example.com", "role": "admin"})
            writer.writerow(
                {"email": "supervisor@example.com", "role": "supervisor"}
            )
            writer.writerow({"email": "user@example.com", "role": "user"})
            csv_file = f.name

        try:
            # Create groups
            roles = {"admin", "supervisor", "user"}
            for role in roles:
                group, created = self.manager.create_or_update_group(role)
                self.assertTrue(created)
                self.assertEqual(group.name, role)

            # Verify groups were created
            self.assertEqual(Group.objects.count(), 3)
        finally:
            Path(csv_file).unlink()

    def test_hierarchical_roles_in_csv(self):
        """Test handling hierarchical roles like 'admin/supervisor'."""
        # Create a temporary CSV file with hierarchical roles
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as f:
            writer = csv.DictWriter(f, fieldnames=["email", "role"])
            writer.writeheader()
            writer.writerow(
                {"email": "user@example.com", "role": "admin/supervisor"}
            )
            csv_file = f.name

        try:
            # Parse roles
            roles = set()
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    role = row.get("role", "").strip()
                    if role:
                        for r in role.split("/"):
                            roles.add(r.strip())

            # Create groups
            for role in roles:
                group, created = self.manager.create_or_update_group(role)
                self.assertTrue(created)

            # Verify groups were created
            self.assertEqual(Group.objects.count(), 2)
            self.assertTrue(Group.objects.filter(name="admin").exists())
            self.assertTrue(Group.objects.filter(name="supervisor").exists())
        finally:
            Path(csv_file).unlink()
