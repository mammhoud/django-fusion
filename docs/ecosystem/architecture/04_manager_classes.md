# Manager Classes Documentation

## Overview

Manager classes provide database query abstractions and business logic for models.

## Role Hierarchy Manager

**Location**: `django_fusion/managers/role_hierarchy.py`

Manages role-based permissions and group hierarchies.

```python
from django_fusion.managers import RoleHierarchyManager
```

### Methods

#### get_all_permissions_for_role(role)

Returns all permissions for a given role, including inherited permissions from parent roles.

```python
permissions = RoleHierarchyManager.get_all_permissions_for_role('admin')
# Returns: {'view_dashboard', 'edit_users', 'manage_settings', ...}
```

#### get_role_hierarchy(role)

Returns the role hierarchy as a list, starting with the queried role and moving up to parent roles.

```python
hierarchy = RoleHierarchyManager.get_role_hierarchy('editor')
# Returns: ['editor', 'contributor', 'viewer']
```

#### create_or_update_group(name, role, description=None)

Creates or updates a group with the specified role.

```python
group = RoleHierarchyManager.create_or_update_group(
    name='Content Editors',
    role='editor',
    description='Can edit and publish content'
)
```

#### assign_user_to_role(user, role)

Assigns a user to a specific role.

```python
RoleHierarchyManager.assign_user_to_role(user, 'admin')
```

#### assign_user_to_multiple_roles(user, roles)

Assigns a user to multiple roles.

```python
RoleHierarchyManager.assign_user_to_multiple_roles(user, ['editor', 'moderator'])
```

#### get_user_roles(user)

Gets all roles for a user.

```python
roles = RoleHierarchyManager.get_user_roles(user)
# Returns: ['admin', 'editor']
```

#### get_user_permissions(user)

Gets all permissions for a user based on their roles.

```python
perms = RoleHierarchyManager.get_user_permissions(user)
```

#### has_role(user, role)

Checks if a user has a specific role.

```python
if RoleHierarchyManager.has_role(user, 'admin'):
    # Do something
```

#### has_permission(user, permission)

Checks if a user has a specific permission.

```python
if RoleHierarchyManager.has_permission(user, 'edit_content'):
    # Do something
```

## Group Access Control

**Location**: `django_fusion/managers/group_access.py`

Provides group-based access control utilities.

```python
from django_fusion.managers import GroupAccessControl
```

### Methods

#### check_group_access(user, group)

Checks if a user has access to a specific group.

```python
if GroupAccessControl.check_group_access(user, 'editors'):
    # Allow access
```

#### check_role_access(user, role)

Checks if a user has access based on their role.

```python
if GroupAccessControl.check_role_access(user, 'admin'):
    # Allow access
```

#### get_accessible_groups(user)

Returns all groups a user has access to.

```python
groups = GroupAccessControl.get_accessible_groups(user)
```

#### filter_by_group(queryset, user, field='group')

Filters a queryset by the user's accessible groups.

```python
from myapp.models import Content
accessible_content = GroupAccessControl.filter_by_group(Content.objects.all(), user)
```

## Enrollments Manager

**Location**: `apps.lms.managers.enrollments`

Manages course enrollment operations.

```python
from apps.lms.managers import EnrollmentsManager
```

### Methods

#### get_user_enrollment_for_course(user, course)

Gets a user's enrollment for a specific course.

```python
enrollment = EnrollmentsManager().get_user_enrollment_for_course(user, course)
```

#### get_user_enrollments(user)

Gets all enrollments for a user.

```python
enrollments = EnrollmentsManager().get_user_enrollments(user)
```

#### get_course_enrollments(course)

Gets all enrollments for a course.

```python
enrollments = EnrollmentsManager().get_course_enrollments(course)
```

## Course Manager

**Location**: `apps.lms.managers.course`

Manages course query operations.

```python
from apps.lms.managers import CourseManager
```

### Methods

#### get_published_courses()

Returns all published courses.

```python
courses = CourseManager.get_published_courses()
```

#### get_featured_courses(limit=6)

Returns featured courses.

```python
courses = CourseManager.get_featured_courses(limit=10)
```

#### search_courses(query, filters=None)

Searches courses by query string.

```python
results = CourseManager.search_courses('python', {'level': 'beginner'})
```
