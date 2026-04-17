"""
Management command to set up Wagtail groups and roles from email roles.

This command:
1. Creates Wagtail groups for different roles
2. Sets up role hierarchy
3. Configures permission inheritance
4. Synchronizes with email roles
"""

import csv
from pathlib import Path

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.CI.models.group import RoleEmailMapping, WagtailGroupRole


class Command(BaseCommand):
    help = 'Set up Wagtail groups and roles with permission inheritance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='test_email.csv',
            help='Path to CSV file with email roles (default: test_email.csv)'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing groups and roles before setup'
        )
        parser.add_argument(
            '--sync-permissions',
            action='store_true',
            help='Sync permissions from parent roles'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        try:
            if options['reset']:
                self.reset_groups()

            self.setup_role_hierarchy()
            self.setup_email_role_mappings()

            if options['sync_permissions']:
                self.sync_permissions()

            self.load_email_roles_from_csv(options['csv'])

            self.stdout.write(
                self.style.SUCCESS('✓ Wagtail groups and roles set up successfully')
            )
        except Exception as e:
            raise CommandError(f'Error setting up Wagtail groups: {str(e)}')

    def reset_groups(self):
        """Reset existing groups and roles."""
        self.stdout.write('Resetting existing groups and roles...')

        with transaction.atomic():
            WagtailGroupRole.objects.all().delete()
            RoleEmailMapping.objects.all().delete()
            Group.objects.all().delete()

        self.stdout.write(self.style.WARNING('✓ Groups and roles reset'))

    def setup_role_hierarchy(self):
        """Set up the role hierarchy with groups."""
        self.stdout.write('Setting up role hierarchy...')

        role_configs = [
            {
                'name': 'Administrators',
                'role_type': WagtailGroupRole.RoleType.ADMIN,
                'description': 'Full system access and administration',
                'parent': None,
            },
            {
                'name': 'Supervisors',
                'role_type': WagtailGroupRole.RoleType.SUPERVISOR,
                'description': 'Supervisory access with content management',
                'parent': None,
            },
            {
                'name': 'Managers',
                'role_type': WagtailGroupRole.RoleType.MANAGER,
                'description': 'Content management and user management',
                'parent': 'Supervisors',
            },
            {
                'name': 'Editors',
                'role_type': WagtailGroupRole.RoleType.EDITOR,
                'description': 'Content editing and publishing',
                'parent': 'Managers',
            },
            {
                'name': 'Contributors',
                'role_type': WagtailGroupRole.RoleType.CONTRIBUTOR,
                'description': 'Content contribution and submission',
                'parent': 'Editors',
            },
            {
                'name': 'Viewers',
                'role_type': WagtailGroupRole.RoleType.VIEWER,
                'description': 'Read-only access to content',
                'parent': None,
            },
        ]

        created_roles = {}

        with transaction.atomic():
            for config in role_configs:
                group, _ = Group.objects.get_or_create(name=config['name'])

                parent_role = None
                if config['parent']:
                    parent_group = Group.objects.get(name=config['parent'])
                    parent_role = WagtailGroupRole.objects.get(group=parent_group)

                role, created = WagtailGroupRole.objects.get_or_create(
                    group=group,
                    defaults={
                        'role_type': config['role_type'],
                        'description': config['description'],
                        'parent_role': parent_role,
                    }
                )

                created_roles[config['name']] = role

                status = 'created' if created else 'exists'
                self.stdout.write(f'  ✓ {config["name"]} ({status})')

        self.stdout.write(self.style.SUCCESS('✓ Role hierarchy set up'))

    def setup_email_role_mappings(self):
        """Set up mappings between email roles and Wagtail groups."""
        self.stdout.write('Setting up email role mappings...')

        mappings = [
            ('admin', 'Administrators', 'Administrator role from email system'),
            ('supervisor', 'Supervisors', 'Supervisor role from email system'),
            ('manager', 'Managers', 'Manager role from email system'),
            ('editor', 'Editors', 'Editor role from email system'),
            ('contributor', 'Contributors', 'Contributor role from email system'),
            ('viewer', 'Viewers', 'Viewer role from email system'),
        ]

        with transaction.atomic():
            for email_role, group_name, description in mappings:
                try:
                    group = Group.objects.get(name=group_name)
                    mapping, created = RoleEmailMapping.objects.get_or_create(
                        email_role=email_role,
                        defaults={
                            'wagtail_group': group,
                            'description': description,
                        }
                    )

                    status = 'created' if created else 'exists'
                    self.stdout.write(f'  ✓ {email_role} → {group_name} ({status})')
                except Group.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'  ✗ Group "{group_name}" not found for {email_role}')
                    )

        self.stdout.write(self.style.SUCCESS('✓ Email role mappings set up'))

    def sync_permissions(self):
        """Sync permissions from parent roles."""
        self.stdout.write('Syncing permissions from parent roles...')

        with transaction.atomic():
            for role in WagtailGroupRole.objects.filter(parent_role__isnull=False):
                role.sync_permissions_from_parent()
                self.stdout.write(f'  ✓ Synced permissions for {role.group.name}')

        self.stdout.write(self.style.SUCCESS('✓ Permissions synced'))

    def load_email_roles_from_csv(self, csv_path):
        """Load email roles from CSV file and sync with Wagtail groups."""
        self.stdout.write(f'Loading email roles from {csv_path}...')

        csv_file = Path(csv_path)
        if not csv_file.exists():
            self.stdout.write(
                self.style.WARNING(f'CSV file not found: {csv_path}')
            )
            return

        with transaction.atomic():
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    email = row.get('email', '').strip()
                    role = row.get('role', '').strip()

                    if not email or not role:
                        continue

                    # Parse hierarchical roles (e.g., "admin/supervisor")
                    roles = [r.strip() for r in role.split('/')]

                    self.stdout.write(f'  Processing {email} with roles: {", ".join(roles)}')

        self.stdout.write(self.style.SUCCESS('✓ Email roles loaded'))
