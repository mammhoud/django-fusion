"""
Unit tests for Wagtail group and role models.

Tests model structure and basic functionality without database operations.
"""

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from www.ci.models.group import (
    GroupContentAccess,
    RoleEmailMapping,
    WagtailGroupRole,
)


class WagtailGroupRoleModelTest(TestCase):
    """Test WagtailGroupRole model."""

    def setUp(self):
        """Set up test data."""
        self.group = Group.objects.create(name='Test Group')

    def test_create_wagtail_group_role(self):
        """Test creating a WagtailGroupRole."""
        role = WagtailGroupRole.objects.create(
            group=self.group,
            role_type=WagtailGroupRole.RoleType.ADMIN,
            description='Test admin role'
        )

        self.assertEqual(role.group, self.group)
        self.assertEqual(role.role_type, WagtailGroupRole.RoleType.ADMIN)
        self.assertEqual(role.description, 'Test admin role')
        self.assertTrue(role.is_active)

    def test_role_hierarchy_levels(self):
        """Test role hierarchy levels."""
        admin_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.ADMIN
        )
        supervisor_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.SUPERVISOR
        )
        viewer_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.VIEWER
        )

        self.assertGreater(admin_level, supervisor_level)
        self.assertGreater(supervisor_level, viewer_level)

    def test_parent_role_relationship(self):
        """Test parent role relationship."""
        admin_group = Group.objects.create(name='Admin Group')
        admin_role = WagtailGroupRole.objects.create(
            group=admin_group,
            role_type=WagtailGroupRole.RoleType.ADMIN
        )

        supervisor_role = WagtailGroupRole.objects.create(
            group=self.group,
            role_type=WagtailGroupRole.RoleType.SUPERVISOR,
            parent_role=admin_role
        )

        self.assertEqual(supervisor_role.parent_role, admin_role)

    def test_role_string_representation(self):
        """Test role string representation."""
        role = WagtailGroupRole.objects.create(
            group=self.group,
            role_type=WagtailGroupRole.RoleType.EDITOR
        )

        self.assertIn('Test Group', str(role))
        self.assertIn('Editor', str(role))

    def test_deactivate_role(self):
        """Test deactivating a role."""
        role = WagtailGroupRole.objects.create(
            group=self.group,
            role_type=WagtailGroupRole.RoleType.EDITOR,
            is_active=True
        )

        role.is_active = False
        role.save()

        role.refresh_from_db()
        self.assertFalse(role.is_active)


class GroupContentAccessModelTest(TestCase):
    """Test GroupContentAccess model."""

    def setUp(self):
        """Set up test data."""
        self.group = Group.objects.create(name='Editors')

    def test_create_content_access(self):
        """Test creating content access."""
        access = GroupContentAccess.objects.create(
            group=self.group,
            content_type='page',
            access_level='edit'
        )

        self.assertEqual(access.group, self.group)
        self.assertEqual(access.content_type, 'page')
        self.assertEqual(access.access_level, 'edit')

    def test_content_access_with_specific_id(self):
        """Test content access with specific content ID."""
        access = GroupContentAccess.objects.create(
            group=self.group,
            content_type='page',
            content_id='page-123',
            access_level='view'
        )

        self.assertEqual(access.content_id, 'page-123')

    def test_access_level_choices(self):
        """Test access level choices."""
        access_levels = ['view', 'edit', 'publish', 'admin']

        for level in access_levels:
            access = GroupContentAccess.objects.create(
                group=self.group,
                content_type='page',
                content_id=f'page-{level}',
                access_level=level
            )
            self.assertEqual(access.access_level, level)

    def test_content_access_string_representation(self):
        """Test content access string representation."""
        access = GroupContentAccess.objects.create(
            group=self.group,
            content_type='page',
            access_level='edit'
        )

        self.assertIn('Editors', str(access))
        self.assertIn('Edit', str(access))
        self.assertIn('page', str(access))

    def test_unique_constraint(self):
        """Test unique constraint on group, content_type, content_id."""
        GroupContentAccess.objects.create(
            group=self.group,
            content_type='page',
            content_id='page-123',
            access_level='view'
        )

        # Creating duplicate should fail
        with self.assertRaises(Exception):
            GroupContentAccess.objects.create(
                group=self.group,
                content_type='page',
                content_id='page-123',
                access_level='edit'
            )


class RoleEmailMappingModelTest(TestCase):
    """Test RoleEmailMapping model."""

    def setUp(self):
        """Set up test data."""
        self.group = Group.objects.create(name='Administrators')

    def test_create_email_role_mapping(self):
        """Test creating email role mapping."""
        mapping = RoleEmailMapping.objects.create(
            email_role='admin',
            wagtail_group=self.group,
            description='Administrator role'
        )

        self.assertEqual(mapping.email_role, 'admin')
        self.assertEqual(mapping.wagtail_group, self.group)
        self.assertTrue(mapping.is_active)

    def test_email_role_unique(self):
        """Test email role uniqueness."""
        RoleEmailMapping.objects.create(
            email_role='admin',
            wagtail_group=self.group
        )

        # Creating duplicate should fail
        with self.assertRaises(Exception):
            RoleEmailMapping.objects.create(
                email_role='admin',
                wagtail_group=self.group
            )

    def test_mapping_string_representation(self):
        """Test mapping string representation."""
        mapping = RoleEmailMapping.objects.create(
            email_role='admin',
            wagtail_group=self.group
        )

        self.assertIn('admin', str(mapping))
        self.assertIn('Administrators', str(mapping))

    def test_deactivate_mapping(self):
        """Test deactivating a mapping."""
        mapping = RoleEmailMapping.objects.create(
            email_role='admin',
            wagtail_group=self.group,
            is_active=True
        )

        mapping.is_active = False
        mapping.save()

        mapping.refresh_from_db()
        self.assertFalse(mapping.is_active)


class RoleHierarchyTest(TestCase):
    """Test role hierarchy functionality."""

    def setUp(self):
        """Set up test data."""
        # Create role hierarchy
        self.admin_group = Group.objects.create(name='Administrators')
        self.admin_role = WagtailGroupRole.objects.create(
            group=self.admin_group,
            role_type=WagtailGroupRole.RoleType.ADMIN
        )

        self.supervisor_group = Group.objects.create(name='Supervisors')
        self.supervisor_role = WagtailGroupRole.objects.create(
            group=self.supervisor_group,
            role_type=WagtailGroupRole.RoleType.SUPERVISOR,
            parent_role=self.admin_role
        )

    def test_hierarchy_levels_correct(self):
        """Test that hierarchy levels are correct."""
        admin_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.ADMIN
        )
        supervisor_level = WagtailGroupRole.get_role_hierarchy_level(
            WagtailGroupRole.RoleType.SUPERVISOR
        )

        self.assertEqual(admin_level, 6)
        self.assertEqual(supervisor_level, 5)

    def test_all_role_types_have_levels(self):
        """Test that all role types have hierarchy levels."""
        for role_type in WagtailGroupRole.RoleType.values:
            level = WagtailGroupRole.get_role_hierarchy_level(role_type)
            self.assertGreater(level, 0)

    def test_role_hierarchy_ordering(self):
        """Test that role hierarchy is correctly ordered."""
        levels = {}
        for role_type in WagtailGroupRole.RoleType.values:
            levels[role_type] = WagtailGroupRole.get_role_hierarchy_level(role_type)

        # Admin should be highest
        self.assertEqual(
            levels[WagtailGroupRole.RoleType.ADMIN],
            max(levels.values())
        )

        # Viewer should be lowest
        self.assertEqual(
            levels[WagtailGroupRole.RoleType.VIEWER],
            min(levels.values())
        )
