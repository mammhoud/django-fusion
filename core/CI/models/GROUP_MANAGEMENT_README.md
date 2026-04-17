# Wagtail Group and Role Management

This module provides comprehensive group and role management for Wagtail CMS with role-based permission inheritance and group-based content access control.

## Overview

The Wagtail group and role management system consists of three main models:

1. **WagtailGroupRole** - Extended Wagtail groups with role hierarchy and permission inheritance
2. **GroupContentAccess** - Group-based content access control
3. **RoleEmailMapping** - Synchronization between email roles and Wagtail groups

## Models

### WagtailGroupRole

Manages role-based permission inheritance and group hierarchy.

**Features:**
- Role hierarchy (Admin > Supervisor > Manager > Editor > Contributor > Viewer)
- Permission inheritance from parent roles
- Active/inactive status management
- Automatic permission synchronization

**Fields:**
- `group` - OneToOneField to Django Group
- `role_type` - Role type in the hierarchy
- `description` - Role description
- `parent_role` - Parent role for permission inheritance
- `is_active` - Whether the group is active
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Methods:**
- `get_inherited_permissions()` - Get all permissions including inherited ones
- `sync_permissions_from_parent()` - Synchronize permissions from parent role
- `get_role_hierarchy_level(role_type)` - Get hierarchy level for a role
- `has_permission_level(user, required_role_type)` - Check if user has required role level

### GroupContentAccess

Manages group-based content access control.

**Features:**
- Fine-grained access control (view, edit, publish, admin)
- Content type and specific content ID support
- Hierarchical access levels

**Fields:**
- `group` - ForeignKey to Django Group
- `content_type` - Content type identifier
- `access_level` - Access level (view, edit, publish, admin)
- `content_id` - Specific content ID (optional)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Methods:**
- `has_access(group, content_type, access_level, content_id)` - Check group access
- `get_user_accessible_content(user, content_type, access_level)` - Get accessible content

### RoleEmailMapping

Maps email roles to Wagtail groups for synchronization.

**Features:**
- Email role to Wagtail group mapping
- Active/inactive status
- Automatic user group synchronization

**Fields:**
- `email_role` - Email role identifier
- `wagtail_group` - ForeignKey to Django Group
- `description` - Mapping description
- `is_active` - Whether the mapping is active
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

**Methods:**
- `get_group_for_email_role(email_role)` - Get Wagtail group for email role
- `sync_user_groups_from_email_roles(user, email_roles)` - Sync user groups

## Management Commands

### setup_wagtail_groups

Set up Wagtail groups and roles with permission inheritance.

**Usage:**
```bash
python manage.py setup_wagtail_groups [options]
```

**Options:**
- `--csv CSV` - Path to CSV file with email roles (default: test_email.csv)
- `--reset` - Reset existing groups and roles before setup
- `--sync-permissions` - Sync permissions from parent roles

**Example:**
```bash
# Set up groups with reset
python manage.py setup_wagtail_groups --reset

# Set up groups and sync permissions
python manage.py setup_wagtail_groups --reset --sync-permissions

# Use custom CSV file
python manage.py setup_wagtail_groups --csv custom_roles.csv
```

### sync_email_roles

Synchronize user groups based on email roles from CSV.

**Usage:**
```bash
python manage.py sync_email_roles [options]
```

**Options:**
- `--csv CSV` - Path to CSV file with email roles (default: test_email.csv)
- `--create-users` - Create users if they do not exist
- `--dry-run` - Show what would be done without making changes

**Example:**
```bash
# Sync email roles
python manage.py sync_email_roles

# Create users and sync
python manage.py sync_email_roles --create-users

# Dry run to preview changes
python manage.py sync_email_roles --dry-run
```

## Service Layer

The `GroupManagementService` provides high-level operations for group management.

**Key Methods:**
- `create_group_with_role()` - Create group with role configuration
- `assign_user_to_group()` - Assign user to group
- `remove_user_from_group()` - Remove user from group
- `sync_user_email_roles()` - Sync user groups from email roles
- `grant_content_access()` - Grant content access to group
- `revoke_content_access()` - Revoke content access from group
- `check_user_content_access()` - Check if user has content access
- `check_user_role_level()` - Check if user has required role level
- `get_user_highest_role()` - Get user's highest role
- `deactivate_group()` - Deactivate a group
- `activate_group()` - Activate a group

**Example Usage:**
```python
from core.CI.services.group_service import GroupManagementService
from django.contrib.auth.models import User

# Get user
user = User.objects.get(email='user@example.com')

# Check if user has admin role
if GroupManagementService.check_user_role_level(user, 'admin'):
    print("User is admin")

# Check if user can edit pages
if GroupManagementService.check_user_content_access(user, 'page', 'edit'):
    print("User can edit pages")

# Get user's highest role
highest_role = GroupManagementService.get_user_highest_role(user)
print(f"User's highest role: {highest_role}")
```

## CSV Format

The email roles CSV file should have the following format:

```csv
email,role
user1@example.com,admin
user2@example.com,supervisor
user3@example.com,admin/supervisor
```

**Columns:**
- `email` - User email address
- `role` - Role(s) separated by `/` for hierarchical roles

## Role Hierarchy

The role hierarchy is as follows (from highest to lowest privilege):

1. **Admin** (Level 6) - Full system access and administration
2. **Supervisor** (Level 5) - Supervisory access with content management
3. **Manager** (Level 4) - Content management and user management
4. **Editor** (Level 3) - Content editing and publishing
5. **Contributor** (Level 2) - Content contribution and submission
6. **Viewer** (Level 1) - Read-only access to content

## Permission Inheritance

Permissions are inherited from parent roles. For example:
- Supervisors inherit all Admin permissions
- Managers inherit all Supervisor and Admin permissions
- And so on...

To sync permissions from parent roles:
```bash
python manage.py setup_wagtail_groups --sync-permissions
```

## Content Access Control

Content access is controlled through the `GroupContentAccess` model. Access levels are hierarchical:

- **view** - Can view content (includes edit, publish, admin)
- **edit** - Can edit content (includes publish, admin)
- **publish** - Can publish content (includes admin)
- **admin** - Full administrative access

**Example:**
```python
from core.CI.services.group_service import GroupManagementService
from django.contrib.auth.models import Group

# Get group
group = Group.objects.get(name='Editors')

# Grant edit access to all pages
GroupManagementService.grant_content_access(group, 'page', 'edit')

# Grant view access to specific page
GroupManagementService.grant_content_access(group, 'page', 'view', 'page-123')

# Check if group has access
has_access = GroupManagementService.check_user_content_access(user, 'page', 'edit')
```

## Email Role Synchronization

The system can automatically synchronize user groups based on email roles:

```python
from core.CI.models.group import RoleEmailMapping

# Sync user groups from email roles
RoleEmailMapping.sync_user_groups_from_email_roles(user, ['admin', 'supervisor'])
```

## Testing

Run the test suite:

```bash
# Run all group management tests
python manage.py test core.CI.tests.test_group_management

# Run model tests
python manage.py test core.CI.tests.test_group_models

# Run with verbose output
python manage.py test core.CI.tests.test_group_management -v 2
```

## Integration with Wagtail Admin

The group management system integrates with Wagtail's admin interface through the `GroupRolesForm` in `django-rseal`:

```python
from django_rseal.pipelines.forms.group import GroupRolesForm

# Use in admin
class GroupAdmin(admin.ModelAdmin):
    form = GroupRolesForm
```

## Best Practices

1. **Use Role Hierarchy** - Leverage the role hierarchy for permission management
2. **Sync Permissions** - Regularly sync permissions from parent roles
3. **Test Access Control** - Test content access control before deployment
4. **Monitor Active Status** - Deactivate groups instead of deleting them
5. **Use Email Mappings** - Keep email role mappings up to date
6. **Audit Changes** - Monitor group and permission changes

## Troubleshooting

### Groups not syncing
- Check that email roles in CSV match the configured mappings
- Verify that users exist in the system
- Use `--dry-run` to preview changes

### Permissions not inherited
- Run `setup_wagtail_groups --sync-permissions`
- Check parent role configuration
- Verify role hierarchy levels

### Content access not working
- Check `GroupContentAccess` records
- Verify user is in correct group
- Check access level hierarchy

## Future Enhancements

- Wagtail admin interface for group management
- Permission templates for common use cases
- Audit logging for group changes
- Bulk operations for group management
- Integration with LDAP/Active Directory
