from contextlib import suppress
from typing import Any

from django import template
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission as PermissionModel

register = template.Library()


# For checking if is_staff
@register.filter(name="is_staff")
def is_staff(user):
    return user.is_staff


@register.filter(name="staff_required")
def staff_required(view_func):
    return user_passes_test(is_staff, login_url="login")(view_func)


# --- Role-Based Filters --- #


@register.filter
def has_group(user, group_name: str) -> bool:
    """
    Check if the user belongs to a specific group.

    Usage:
        {% if user|has_group:"admin" %}
    """
    return user.groups.filter(name=group_name).exists()


@register.filter
def has_role(user, role_name: str) -> bool:
    """
    Check if the user has a specific role (mapped to a group name with " Group" suffix).

    Usage:
        {% if user|has_role:"admin" %}
    """
    return user.groups.filter(name=f"{role_name} Group").exists()


@register.filter(name="is_admin")
def is_admin(user) -> bool:
    """Check if the user is in the 'admin' group."""
    return user.groups.filter(name="admin").exists()


@register.filter(name="is_client")
def is_client(user) -> bool:
    """Check if the user is in the 'client' group."""
    return user.groups.filter(name="client").exists()


# --- User Property Filters --- #


@register.filter(name="is_superuser")
def is_superuser(user) -> bool:
    """Check if the user is a superuser."""
    return user.is_superuser


# --- Permission-Based Filters --- #


@register.filter
def has_permission(user, permission_codename: str) -> bool:
    """
    Check if the user has a specific permission (custom backend support included).

    Usage:
        {% if user|has_permission:"app_label.permission_codename" %}
    """
    with suppress(ImportError):
        from core.app.payloads.permissions import Permissions

    return Permissions.has_permission(user, permission_codename)


@register.filter
def has_perm(obj: Any, user: Any) -> bool:
    """
    Check if a user has view permission on an object with custom 'has_view_permission' logic.

    Usage:
        {% if object|has_perm:request.user %}
    """
    if hasattr(obj, "has_view_permission"):
        return obj.has_view_permission(user)
    return True


# --- Utility Tags --- #


@register.simple_tag
def user_has_role_or_permission(
    user, role_name: str | None = None, permission: str | None = None
) -> bool:
    """
    Check if the user has a specific role or permission.

    Usage:
        {% user_has_role_or_permission user 'admin' 'app_label.permission_codename' %}
    """
    if role_name and has_role(user, role_name):
        return True
    if permission and user.has_perm(permission):
        return True
    return False


@register.simple_tag
def show_nav_item(
    user, required_roles: list[str] | None = None, required_permissions: list[str] | None = None
) -> bool:
    """
    Show a navigation item if the user has any of the required roles or permissions.

    Usage:
        {% show_nav_item user required_roles='admin' %}
    """
    if required_roles:
        for role in required_roles:
            if has_role(user, role):
                return True
    if required_permissions:
        for perm in required_permissions:
            if user.has_perm(perm):
                return True
    return False


@register.simple_tag
def assign_role_to_user(user, role_name: str) -> str:
    """
    Assign a role (group) to a user.

    Usage:
        {% assign_role_to_user user 'manager' %}
    """
    try:
        group, _ = Group.objects.get_or_create(name=f"{role_name} Group")
        user.groups.add(group)
        user.save()
        return f"✅ Role '{role_name}' successfully assigned to user '{user.username}'."
    except Exception:
        return f"❌ Failed to assign role '{role_name}' to user '{user.username}'."


# --- Permission Listing Tags --- #


@register.simple_tag
def list_permissions(user) -> set:
    """
    List all permissions for the user (including group-based).

    Usage:
        {% list_permissions user %}
    """
    return user.get_all_permissions()


@register.simple_tag
def list_group_permissions(group: Group):
    """
    List all permissions attached to a group.

    Usage:
        {% list_group_permissions group %}
    """
    return group.permissions.all()


@register.simple_tag
def add_permission_to_role(role_name: str, permission_codename: str) -> str:
    """
    Assign a permission to a role (group).

    Usage:
        {% add_permission_to_role 'manager' 'app_label.permission_codename' %}
    """
    try:
        group = Group.objects.get(name=f"{role_name} Group")
        permission = PermissionModel.objects.get(codename=permission_codename)
        group.permissions.add(permission)
        group.save()
        return f"✅ Permission '{permission_codename}' added to role '{role_name}'."
    except Group.DoesNotExist:
        return f"❌ Role '{role_name}' does not exist."
    except PermissionModel.DoesNotExist:
        return f"❌ Permission '{permission_codename}' does not exist."
    except Exception:
        return f"❌ Failed to add permission '{permission_codename}' to role '{role_name}'."
