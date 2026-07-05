"""
Unit tests for GroupAccessControl.

Validates: Requirements 2.3
"""
import pytest
from django.contrib.auth.models import Group, User
from django.test import TestCase
from django_fusion.core.managers import GroupAccessControl


@pytest.fixture
def db_setup(db):
    """Setup database for tests."""
    pass


@pytest.fixture
def user_with_groups(db):
    """Create a user with groups."""
    user = User.objects.create_user(username="testuser", password="testpass")
    editors = Group.objects.create(name="editors")
    admins = Group.objects.create(name="admins")
    user.groups.add(editors, admins)
    return user


@pytest.fixture
def user_without_groups(db):
    """Create a user without groups."""
    return User.objects.create_user(username="nobody", password="testpass")


@pytest.fixture
def superuser(db):
    """Create a superuser."""
    return User.objects.create_superuser(username="admin", email="admin@test.com", password="testpass")


class TestCheckGroupAccess:
    """Tests for check_group_access method."""

    def test_user_in_required_group(self, user_with_groups):
        """User belonging to a required group returns True."""
        result = GroupAccessControl.check_group_access(user_with_groups, ["editors"])
        assert result is True

    def test_user_in_one_of_multiple_required_groups(self, user_with_groups):
        """User belonging to one of multiple required groups returns True."""
        result = GroupAccessControl.check_group_access(user_with_groups, ["editors", "moderators"])
        assert result is True

    def test_user_not_in_required_group(self, user_without_groups):
        """User not belonging to any required group returns False."""
        result = GroupAccessControl.check_group_access(user_without_groups, ["editors"])
        assert result is False

    def test_user_not_in_any_required_groups(self, user_with_groups):
        """User not belonging to any of multiple required groups returns False."""
        result = GroupAccessControl.check_group_access(user_with_groups, ["moderators", "superadmins"])
        assert result is False

    def test_superuser_always_passes(self, superuser):
        """Superuser always passes regardless of group membership."""
        result = GroupAccessControl.check_group_access(superuser, ["nonexistent"])
        assert result is True

    def test_empty_required_groups(self, user_with_groups):
        """Empty required groups list returns False for non-superuser."""
        result = GroupAccessControl.check_group_access(user_with_groups, [])
        assert result is False


class TestCheckRoleAccess:
    """Tests for check_role_access method."""

    def test_user_has_required_role(self, user_with_groups):
        """User belonging to the required role returns True."""
        result = GroupAccessControl.check_role_access(user_with_groups, "editors")
        assert result is True

    def test_user_does_not_have_required_role(self, user_without_groups):
        """User not belonging to the required role returns False."""
        result = GroupAccessControl.check_role_access(user_without_groups, "editors")
        assert result is False

    def test_superuser_always_passes_role(self, superuser):
        """Superuser always passes role check."""
        result = GroupAccessControl.check_role_access(superuser, "nonexistent")
        assert result is True


class TestGetAccessibleGroups:
    """Tests for get_accessible_groups method."""

    def test_returns_user_groups(self, user_with_groups):
        """Returns all groups the user belongs to."""
        result = GroupAccessControl.get_accessible_groups(user_with_groups)
        group_names = [g.name for g in result]
        assert "editors" in group_names
        assert "admins" in group_names

    def test_returns_empty_for_user_without_groups(self, user_without_groups):
        """Returns empty list for user without groups."""
        result = GroupAccessControl.get_accessible_groups(user_without_groups)
        assert result == []

    def test_returns_all_groups_for_superuser(self, superuser, db):
        """Superuser gets all groups in the system."""
        Group.objects.create(name="group1")
        Group.objects.create(name="group2")
        result = GroupAccessControl.get_accessible_groups(superuser)
        assert len(result) >= 2


class TestFilterByGroup:
    """Tests for filter_by_group method."""

    def test_filter_by_user_groups(self, user_with_groups, db):
        """Filter queryset to only include objects with user's groups."""
        # Create groups
        editors = Group.objects.get(name="editors")
        admins = Group.objects.get(name="admins")

        # Create test model with groups field
        from django.contrib.auth.models import Group as GroupModel

        # Create a simple test using User model which has groups
        from django.contrib.auth.models import User

        # Create another user in editors group
        other_user = User.objects.create_user(username="other", password="testpass")
        other_user.groups.add(editors)

        # Filter users by group - should return users in same group
        result = GroupAccessControl.filter_by_group(User.objects.all(), user_with_groups)
        usernames = list(result.values_list("username", flat=True))

        # Should include user_with_groups and other_user (both in editors/admins)
        assert "testuser" in usernames
        assert "other" in usernames

    def test_superuser_sees_all(self, superuser, db):
        """Superuser sees all records unfiltered."""
        # Create additional users
        User.objects.create_user(username="newuser", password="testpass")
        User.objects.create_user(username="anotheruser", password="testpass")

        # Get initial count (superuser + newuser + anotheruser = 3)
        initial_count = User.objects.count()

        result = GroupAccessControl.filter_by_group(User.objects.all(), superuser)
        # Superuser should see all users (unfiltered)
        assert result.count() == initial_count

    def test_user_without_groups_gets_empty(self, user_without_groups, db):
        """User without groups gets empty queryset."""
        User.objects.create_user(username="someuser", password="testpass")
        result = GroupAccessControl.filter_by_group(User.objects.all(), user_without_groups)
        # User without groups should see no users (or only themselves if they exist)
        # Since user_without_groups has no groups, they shouldn't see other users
        assert result.count() == 0
