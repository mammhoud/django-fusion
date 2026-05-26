"""
Management command to create Django groups from CSV roles.

This command reads a CSV file with email and role columns, and creates
Django groups based on the roles. It also implements permission inheritance
and role hierarchy.

Usage:
    python manage.py create_groups_from_csv --csv-file test_email.csv
"""

import csv
from pathlib import Path
from typing import Set, Tuple

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError


class GroupHierarchyManager:
    """Manages role hierarchy and permission inheritance."""

    # Define role hierarchy: parent roles inherit permissions from child roles
    ROLE_HIERARCHY = {
        "admin": ["supervisor", "user"],
        "supervisor": ["user"],
        "user": [],
    }

    # Define permissions for each role
    ROLE_PERMISSIONS = {
        "admin": [
            "auth.add_user",
            "auth.change_user",
            "auth.delete_user",
            "auth.add_group",
            "auth.change_group",
            "auth.delete_group",
            "auth.add_permission",
            "auth.change_permission",
            "auth.delete_permission",
        ],
        "supervisor": [
            "auth.change_user",
            "auth.view_user",
            "auth.add_group",
            "auth.change_group",
            "auth.view_group",
        ],
        "user": [
            "auth.view_user",
            "auth.view_group",
        ],
    }

    def __init__(self):
        self.created_groups = {}
        self.permission_cache = {}

    def get_all_permissions_for_role(self, role: str) -> Set[str]:
        """Get all permissions for a role including inherited ones."""
        if role in self.permission_cache:
            return self.permission_cache[role]

        permissions = set(self.ROLE_PERMISSIONS.get(role, []))

        # Add inherited permissions from child roles
        for child_role in self.ROLE_HIERARCHY.get(role, []):
            permissions.update(self.get_all_permissions_for_role(child_role))

        self.permission_cache[role] = permissions
        return permissions

    def create_or_update_group(self, role: str) -> Tuple[Group, bool]:
        """Create or update a group with appropriate permissions."""
        group, created = Group.objects.get_or_create(name=role)

        # Get all permissions for this role
        permission_codenames = self.get_all_permissions_for_role(role)

        # Get permission objects
        permissions = []
        for perm_string in permission_codenames:
            try:
                app_label, codename = perm_string.split(".")
                perm = Permission.objects.get(
                    content_type__app_label=app_label, codename=codename
                )
                permissions.append(perm)
            except Permission.DoesNotExist:
                # Permission doesn't exist, skip it
                pass

        # Set permissions for the group
        group.permissions.set(permissions)

        return group, created


class Command(BaseCommand):
    help = "Create Django groups from CSV roles with permission inheritance"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv-file",
            type=str,
            default="test_email.csv",
            help="Path to CSV file with email and role columns",
        )
        parser.add_argument(
            "--create-users",
            action="store_true",
            help="Create users from CSV if they don't exist",
        )
        parser.add_argument(
            "--assign-groups",
            action="store_true",
            help="Assign users to groups based on CSV roles",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        create_users = options["create_users"]
        assign_groups = options["assign_groups"]

        # Verify CSV file exists
        csv_path = Path(csv_file)
        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_file}")

        self.stdout.write(self.style.SUCCESS(f"Reading CSV file: {csv_file}"))

        # Read CSV and extract roles
        roles = self._extract_roles_from_csv(csv_path)
        self.stdout.write(
            self.style.SUCCESS(f"Found {len(roles)} unique roles: {', '.join(roles)}")
        )

        # Create groups with permission inheritance
        hierarchy_manager = GroupHierarchyManager()
        created_count = 0
        updated_count = 0

        for role in roles:
            group, created = hierarchy_manager.create_or_update_group(role)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created group: {role}")
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f"✓ Updated group: {role}")
                )

            # Display permissions for this group
            perm_count = group.permissions.count()
            self.stdout.write(f"  └─ Permissions: {perm_count}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nGroup Management Summary:"
                f"\n  Created: {created_count}"
                f"\n  Updated: {updated_count}"
            )
        )

        # Optionally assign users to groups
        if assign_groups:
            self._assign_users_to_groups(csv_path, hierarchy_manager)

    def _extract_roles_from_csv(self, csv_path: Path) -> Set[str]:
        """Extract unique roles from CSV file."""
        roles = set()

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                role = row.get("role", "").strip()
                if role:
                    # Handle hierarchical roles like "admin/supervisor"
                    for r in role.split("/"):
                        roles.add(r.strip())

        return roles

    def _assign_users_to_groups(
        self, csv_path: Path, hierarchy_manager: GroupHierarchyManager
    ):
        """Assign users to groups based on CSV roles."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        assigned_count = 0
        skipped_count = 0

        self.stdout.write(self.style.SUCCESS("\nAssigning users to groups..."))

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("email", "").strip()
                role = row.get("role", "").strip()

                if not email or not role:
                    continue

                try:
                    user = User.objects.get(email=email)
                    # Clear existing groups
                    user.groups.clear()

                    # Add user to all roles in hierarchy
                    for r in role.split("/"):
                        r = r.strip()
                        group = Group.objects.get(name=r)
                        user.groups.add(group)

                    assigned_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Assigned {email} to {role}")
                    )
                except User.DoesNotExist:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"✗ User not found: {email}")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nUser Assignment Summary:"
                f"\n  Assigned: {assigned_count}"
                f"\n  Skipped: {skipped_count}"
            )
        )
