"""
Examples of using the Wagtail group and role management system.

This file demonstrates common use cases and patterns.
"""

from django.contrib.auth.models import Group, User

from core.CI.models.group import (
    GroupContentAccess,
    RoleEmailMapping,
    WagtailGroupRole,
)
from core.CI.services.group_service import GroupManagementService

# ============================================================================
# Example 1: Setting up role hierarchy
# ============================================================================

def example_setup_role_hierarchy():
    """Example: Set up a role hierarchy."""

    # Create admin role
    admin_group = Group.objects.create(name='Administrators')
    admin_role = WagtailGroupRole.objects.create(
        group=admin_group,
        role_type=WagtailGroupRole.RoleType.ADMIN,
        description='Full system access'
    )

    # Create supervisor role with admin as parent
    supervisor_group = Group.objects.create(name='Supervisors')
    supervisor_role = WagtailGroupRole.objects.create(
        group=supervisor_group,
        role_type=WagtailGroupRole.RoleType.SUPERVISOR,
        description='Supervisory access',
        parent_role=admin_role
    )

    # Create manager role with supervisor as parent
    manager_group = Group.objects.create(name='Managers')
    manager_role = WagtailGroupRole.objects.create(
        group=manager_group,
        role_type=WagtailGroupRole.RoleType.MANAGER,
        description='Content management',
        parent_role=supervisor_role
    )

    print("Role hierarchy created successfully")


# ============================================================================
# Example 2: Assigning users to groups
# ============================================================================

def example_assign_users_to_groups():
    """Example: Assign users to groups."""

    # Get or create users
    admin_user = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com'}
    )[0]

    manager_user = User.objects.get_or_create(
        username='manager',
        defaults={'email': 'manager@example.com'}
    )[0]

    # Get groups
    admin_group = Group.objects.get(name='Administrators')
    manager_group = Group.objects.get(name='Managers')

    # Assign users to groups
    GroupManagementService.assign_user_to_group(admin_user, admin_group)
    GroupManagementService.assign_user_to_group(manager_user, manager_group)

    print("Users assigned to groups successfully")


# ============================================================================
# Example 3: Checking user role levels
# ============================================================================

def example_check_user_role_levels():
    """Example: Check user role levels."""

    user = User.objects.get(username='admin')

    # Check if user is admin
    is_admin = GroupManagementService.check_user_role_level(
        user,
        WagtailGroupRole.RoleType.ADMIN
    )
    print(f"User is admin: {is_admin}")

    # Get user's highest role
    highest_role = GroupManagementService.get_user_highest_role(user)
    print(f"User's highest role: {highest_role}")


# ============================================================================
# Example 4: Setting up content access control
# ============================================================================

def example_setup_content_access():
    """Example: Set up content access control."""

    # Get group
    editor_group = Group.objects.get(name='Editors')

    # Grant edit access to all pages
    GroupManagementService.grant_content_access(
        editor_group,
        'page',
        'edit'
    )

    # Grant view access to specific page
    GroupManagementService.grant_content_access(
        editor_group,
        'page',
        'view',
        'page-123'
    )

    # Grant publish access to blog posts
    GroupManagementService.grant_content_access(
        editor_group,
        'blog',
        'publish'
    )

    print("Content access configured successfully")


# ============================================================================
# Example 5: Checking user content access
# ============================================================================

def example_check_user_content_access():
    """Example: Check user content access."""

    user = User.objects.get(username='editor')

    # Check if user can edit pages
    can_edit_pages = GroupManagementService.check_user_content_access(
        user,
        'page',
        'edit'
    )
    print(f"User can edit pages: {can_edit_pages}")

    # Check if user can publish blog posts
    can_publish_blog = GroupManagementService.check_user_content_access(
        user,
        'blog',
        'publish'
    )
    print(f"User can publish blog posts: {can_publish_blog}")

    # Get all accessible pages
    accessible_pages = GroupManagementService.get_user_accessible_content(
        user,
        'page',
        'edit'
    )
    print(f"Accessible pages: {accessible_pages}")


# ============================================================================
# Example 6: Email role synchronization
# ============================================================================

def example_email_role_sync():
    """Example: Synchronize user groups from email roles."""

    # Create email role mappings
    admin_group = Group.objects.get(name='Administrators')
    RoleEmailMapping.objects.get_or_create(
        email_role='admin',
        defaults={'wagtail_group': admin_group}
    )

    supervisor_group = Group.objects.get(name='Supervisors')
    RoleEmailMapping.objects.get_or_create(
        email_role='supervisor',
        defaults={'wagtail_group': supervisor_group}
    )

    # Get user
    user = User.objects.get(username='testuser')

    # Sync user groups from email roles
    GroupManagementService.sync_user_email_roles(
        user,
        ['admin', 'supervisor']
    )

    print("User groups synced from email roles")


# ============================================================================
# Example 7: Permission inheritance
# ============================================================================

def example_permission_inheritance():
    """Example: Permission inheritance from parent roles."""

    # Get roles
    admin_role = WagtailGroupRole.objects.get(
        role_type=WagtailGroupRole.RoleType.ADMIN
    )
    supervisor_role = WagtailGroupRole.objects.get(
        role_type=WagtailGroupRole.RoleType.SUPERVISOR
    )

    # Add permission to admin group
    from django.contrib.auth.models import Permission
    perm = Permission.objects.first()
    if perm:
        admin_role.group.permissions.add(perm)

        # Sync permissions to supervisor role
        supervisor_role.sync_permissions_from_parent()

        # Get inherited permissions
        inherited_perms = supervisor_role.get_inherited_permissions()
        print(f"Supervisor inherited {len(inherited_perms)} permissions")


# ============================================================================
# Example 8: Deactivating groups
# ============================================================================

def example_deactivate_group():
    """Example: Deactivate a group."""

    # Get group
    group = Group.objects.get(name='Viewers')

    # Deactivate group
    GroupManagementService.deactivate_group(group)

    # Verify deactivation
    role = WagtailGroupRole.objects.get(group=group)
    print(f"Group is active: {role.is_active}")


# ============================================================================
# Example 9: Revoking content access
# ============================================================================

def example_revoke_content_access():
    """Example: Revoke content access from group."""

    # Get group
    group = Group.objects.get(name='Contributors')

    # Revoke edit access to pages
    GroupManagementService.revoke_content_access(
        group,
        'page'
    )

    # Revoke access to specific page
    GroupManagementService.revoke_content_access(
        group,
        'page',
        'page-123'
    )

    print("Content access revoked successfully")


# ============================================================================
# Example 10: Bulk operations
# ============================================================================

def example_bulk_operations():
    """Example: Bulk operations on groups."""

    # Get all active roles
    active_roles = WagtailGroupRole.objects.filter(is_active=True)
    print(f"Active roles: {active_roles.count()}")

    # Get all content access for a group
    group = Group.objects.get(name='Editors')
    content_access = GroupContentAccess.objects.filter(group=group)
    print(f"Content access entries: {content_access.count()}")

    # Get all email role mappings
    mappings = RoleEmailMapping.objects.filter(is_active=True)
    print(f"Active email role mappings: {mappings.count()}")


# ============================================================================
# Example 11: Using management commands
# ============================================================================

def example_management_commands():
    """Example: Using management commands."""

    # These commands should be run from the command line:

    # Set up groups with reset
    # python manage.py setup_wagtail_groups --reset

    # Set up groups and sync permissions
    # python manage.py setup_wagtail_groups --reset --sync-permissions

    # Sync email roles from CSV
    # python manage.py sync_email_roles

    # Dry run to preview changes
    # python manage.py sync_email_roles --dry-run

    print("See comments for management command examples")


# ============================================================================
# Example 12: Querying role hierarchy
# ============================================================================

def example_query_role_hierarchy():
    """Example: Query role hierarchy."""

    # Get all roles ordered by hierarchy
    roles = WagtailGroupRole.objects.all().order_by('-role_type')

    for role in roles:
        level = WagtailGroupRole.get_role_hierarchy_level(role.role_type)
        parent = role.parent_role.group.name if role.parent_role else 'None'
        print(f"{role.group.name} (Level {level}, Parent: {parent})")


# ============================================================================
# Example 13: Advanced content access queries
# ============================================================================

def example_advanced_content_access():
    """Example: Advanced content access queries."""

    # Get all groups with edit access to pages
    edit_access = GroupContentAccess.objects.filter(
        content_type='page',
        access_level='edit'
    )

    groups_with_edit = [access.group.name for access in edit_access]
    print(f"Groups with edit access: {groups_with_edit}")

    # Get all content accessible to a user
    user = User.objects.get(username='editor')
    accessible_content = GroupManagementService.get_user_accessible_content(
        user,
        'page',
        'edit'
    )
    print(f"Accessible content: {accessible_content}")


# ============================================================================
# Example 14: Role-based decorators (for views)
# ============================================================================

def example_role_based_decorators():
    """Example: Using role-based access in views."""

    from functools import wraps

    from django.http import HttpResponseForbidden

    def require_role(required_role):
        """Decorator to require a specific role."""
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(request, *args, **kwargs):
                if not GroupManagementService.check_user_role_level(
                    request.user,
                    required_role
                ):
                    return HttpResponseForbidden("Access denied")
                return view_func(request, *args, **kwargs)
            return wrapper
        return decorator

    def require_content_access(content_type, access_level='view'):
        """Decorator to require content access."""
        def decorator(view_func):
            @wraps(view_func)
            def wrapper(request, *args, **kwargs):
                if not GroupManagementService.check_user_content_access(
                    request.user,
                    content_type,
                    access_level
                ):
                    return HttpResponseForbidden("Access denied")
                return view_func(request, *args, **kwargs)
            return wrapper
        return decorator

    # Usage in views:
    # @require_role(WagtailGroupRole.RoleType.ADMIN)
    # def admin_view(request):
    #     return HttpResponse("Admin content")

    # @require_content_access('page', 'edit')
    # def edit_page_view(request):
    #     return HttpResponse("Edit page")

    print("See comments for decorator usage examples")


if __name__ == '__main__':
    print("Wagtail Group and Role Management Examples")
    print("=" * 50)
    print("\nThese examples demonstrate common use cases.")
    print("Run them in Django shell or management commands.")
