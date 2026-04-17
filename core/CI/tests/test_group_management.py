"""
Tests for Wagtail group and role management.

Tests group creation, role hierarchy, permission inheritance, and content access control.
"""

from django.contrib.auth.models import Group, User
from django.test import TestCase

from core.CI.models.group import GroupContentAccess, RoleEmailMapping, WagtailGroupRole
from core.CI.services.group_service import GroupManagementService


class WagtailGroupRoleTestCase(TestCase):
    """Test cases for WagtailGroupRole model."""

    def setUp(self):
        """Set up test data."""
        self.admin_group = Group.objects.create(name='Administrators')
        self.admin_role = WagtailGroupRole.objects.create(
            group=self.admin_group,
            role_type=WagtailGroupRole.RoleType.ADMIN,
            description='Admin role'
        )

        self.supervisor_group = Group.objects.create(name='Supervisors')
        self.supervisor_role = WagtailGroupRole.objects.create(
            group=self.supervisor_group,
            role_type=WagtailGroupRole.RoleType.SUPERVISOR,
            description='Supervisor role',
            parent_role=self.admin_role
        )

    def test_role_creation(self):
        """Test creating a role."""
        self.assertEqual(self.admin_role.group.name, 'Administrators')
        self.assertEqual(self.admin_role.role_type, WagtailGroupRole.RoleType.ADMIN)

    def test_role_hierarchy_level(self):
        """Test getting role hierarchy level."""
        admin_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.ADMIN
        )
        supervisor_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.SUPERVISOR
        )

        self.assertGreater(admin_level, supervisor_level)

    def test_parent_role_assignment(self):
        """Test assigning parent role."""
        self.assertEqual(self.supervisor_role.parent_role, self.admin_role)

    def test_inherited_permissions(self):
        """Test getting inherited permissions."""
        # Add permission to admin group
        from django.contrib.auth.models import Permission
        perm = Permission.objects.first()
        if perm:
            self.admin_group.permissions.add(perm)

            # Supervisor should inherit admin permissions
            inherited = self.supervisor_role.get_inherited_permissions()
            self.assertIn(perm, inherited)

    def test_has_permission_level(self):
        """Test checking permission level."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        user.groups.add(self.supervisor_group)

        # User should have supervisor level
        self.assertTrue(
            WagtailGroupRole.has_permission_level(
                user,
                WagtailGroupRole.RoleType.SUPERVISOR
            )
        )

        # User should not have admin level
        self.assertFalse(
            WagtailGroupRole.has_permission_level(
                user,
                WagtailGroupRole.RoleType.ADMIN
            )
        )


class GroupContentAccessTestCase(TestCase):
    """Test cases for GroupContentAccess model."""

    def setUp(self):
        """Set up test data."""
        self.group = Group.objects.create(name='Editors')
        self.access = GroupContentAccess.objects.create(
            group=self.group,
            content_type='page',
            access_level='edit'
        )

    def test_content_access_creation(self):
        """Test creating content access."""
        self.assertEqual(self.access.group.name, 'Editors')
        self.assertEqual(self.access.content_type, 'page')
        self.assertEqual(self.access.access_level, 'edit')

    def test_has_access_view(self):
        """Test checking view access."""
        self.assertTrue(
            GroupContentAccess.has_access(
                self.group,
                'page',
                'view'
            )
        )

    def test_has_access_edit(self):
        """Test checking edit access."""
        self.assertTrue(
            GroupContentAccess.has_access(
                self.group,
                'page',
                'edit'
            )
        )

    def test_has_access_publish(self):
        """Test checking publish access (should fail)."""
        self.assertFalse(
            GroupContentAccess.has_access(
                self.group,
                'page',
                'publish'
            )
        )

    def test_specific_content_access(self):
        """Test access to specific content."""
        specific_access = GroupContentAccess.objects.create(
            group=self.group,
            content_type='page',
            content_id='page-123',
            access_level='view'
        )

        self.assertTrue(
            GroupContentAccess.has_access(
                self.group,
                'page',
                'view',
                'page-123'
            )
        )


class RoleEmailMappingTestCase(TestCase):
    """Test cases for RoleEmailMapping model."""

    def setUp(self):
        """Set up test data."""
        self.group = Group.objects.create(name='Administrators')
        self.mapping = RoleEmailMapping.objects.create(
            email_role='admin',
            wagtail_group=self.group,
            description='Admin role mapping'
        )

    def test_mapping_creation(self):
        """Test creating email role mapping."""
        self.assertEqual(self.mapping.email_role, 'admin')
        self.assertEqual(self.mapping.wagtail_group.name, 'Administrators')

    def test_get_group_for_email_role(self):
        """Test getting group for email role."""
        group = RoleEmailMapping.get_group_for_email_role('admin')
        self.assertEqual(group, self.group)

    def test_get_group_for_nonexistent_role(self):
        """Test getting group for nonexistent role."""
        group = RoleEmailMapping.get_group_for_email_role('nonexistent')
        self.assertIsNone(group)

    def test_sync_user_groups_from_email_roles(self):
        """Test syncing user groups from email roles."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )

        RoleEmailMapping.sync_user_groups_from_email_roles(
            user,
            ['admin']
        )

        self.assertIn(self.group, user.groups.all())


class GroupManagementServiceTestCase(TestCase):
    """Test cases for GroupManagementService."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )

    def test_create_group_with_role(self):
        """Test creating group with role."""
        role = GroupManagementService.create_group_with_role(
            'Editors',
            WagtailGroupRole.RoleType.EDITOR,
            'Editor role'
        )

        self.assertEqual(role.group.name, 'Editors')
        self.assertEqual(role.role_type, WagtailGroupRole.RoleType.EDITOR)

    def test_assign_user_to_group(self):
        """Test assigning user to group."""
        group = Group.objects.create(name='Editors')

        result = GroupManagementService.assign_user_to_group(self.user, group)

        self.assertTrue(result)
        self.assertIn(group, self.user.groups.all())

    def test_remove_user_from_group(self):
        """Test removing user from group."""
        group = Group.objects.create(name='Editors')
        self.user.groups.add(group)

        result = GroupManagementService.remove_user_from_group(self.user, group)

        self.assertTrue(result)
        self.assertNotIn(group, self.user.groups.all())

    def test_sync_user_email_roles(self):
        """Test syncing user email roles."""
        admin_group = Group.objects.create(name='Administrators')
        RoleEmailMapping.objects.create(
            email_role='admin',
            wagtail_group=admin_group
        )

        count = GroupManagementService.sync_user_email_roles(
            self.user,
            ['admin']
        )

        self.assertEqual(count, 1)
        self.assertIn(admin_group, self.user.groups.all())

    def test_grant_content_access(self):
        """Test granting content access."""
        group = Group.objects.create(name='Editors')

        access = GroupManagementService.grant_content_access(
            group,
            'page',
            'edit'
        )

        self.assertEqual(access.group, group)
        self.assertEqual(access.content_type, 'page')
        self.assertEqual(access.access_level, 'edit')

    def test_check_user_content_access(self):
        """Test checking user content access."""
        group = Group.objects.create(name='Editors')
        self.user.groups.add(group)

        GroupManagementService.grant_content_access(
            group,
            'page',
            'edit'
        )

        has_access = GroupManagementService.check_user_content_access(
            self.user,
            'page',
            'edit'
        )

        self.assertTrue(has_access)

    def test_check_user_role_level(self):
        """Test checking user role level."""
        admin_group = Group.objects.create(name='Administrators')
        WagtailGroupRole.objects.create(
            group=admin_group,
            role_type=WagtailGroupRole.RoleType.ADMIN
        )
        self.user.groups.add(admin_group)

        has_level = GroupManagementService.check_user_role_level(
            self.user,
            WagtailGroupRole.RoleType.ADMIN
        )

        self.assertTrue(has_level)

    def test_get_user_highest_role(self):
        """Test getting user's highest role."""
        admin_group = Group.objects.create(name='Administrators')
        WagtailGroupRole.objects.create(
            group=admin_group,
            role_type=WagtailGroupRole.RoleType.ADMIN
        )
        self.user.groups.add(admin_group)

        highest_role = GroupManagementService.get_user_highest_role(self.user)

        self.assertEqual(highest_role, WagtailGroupRole.RoleType.ADMIN)

    def test_deactivate_group(self):
        """Test deactivating a group."""
        group = Group.objects.create(name='Editors')
        WagtailGroupRole.objects.create(
            group=group,
            role_type=WagtailGroupRole.RoleType.EDITOR
        )

        result = GroupManagementService.deactivate_group(group)

        self.assertTrue(result)
        role = WagtailGroupRole.objects.get(group=group)
        self.assertFalse(role.is_active)

    def test_activate_group(self):
        """Test activating a group."""
        group = Group.objects.create(name='Editors')
        role = WagtailGroupRole.objects.create(
            group=group,
            role_type=WagtailGroupRole.RoleType.EDITOR,
            is_active=False
        )

        result = GroupManagementService.activate_group(group)

        self.assertTrue(result)
        role.refresh_from_db()
        self.assertTrue(role.is_active)
