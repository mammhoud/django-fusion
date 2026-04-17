"""
Management command to synchronize user groups based on email roles.

This command:
1. Reads email roles from CSV
2. Synchronizes user groups with Wagtail groups
3. Updates role assignments
"""

import csv
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.CI.models.group import RoleEmailMapping


class Command(BaseCommand):
    help = 'Synchronize user groups based on email roles from CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='test_email.csv',
            help='Path to CSV file with email roles (default: test_email.csv)'
        )
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Create users if they do not exist'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        try:
            self.sync_email_roles(
                options['csv'],
                create_users=options['create_users'],
                dry_run=options['dry_run']
            )

            self.stdout.write(
                self.style.SUCCESS('✓ Email roles synchronized successfully')
            )
        except Exception as e:
            raise CommandError(f'Error synchronizing email roles: {str(e)}')

    def sync_email_roles(self, csv_path, create_users=False, dry_run=False):
        """Synchronize user groups based on email roles."""
        csv_file = Path(csv_path)
        if not csv_file.exists():
            raise CommandError(f'CSV file not found: {csv_path}')

        self.stdout.write(f'Reading email roles from {csv_path}...')

        updates = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').strip()
                role_str = row.get('role', '').strip()

                if not email or not role_str:
                    continue

                # Parse hierarchical roles (e.g., "admin/supervisor")
                roles = [r.strip() for r in role_str.split('/')]

                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    if create_users:
                        if dry_run:
                            self.stdout.write(
                                f'  [DRY-RUN] Would create user: {email}'
                            )
                        else:
                            user = User.objects.create_user(
                                username=email.split('@')[0],
                                email=email
                            )
                            self.stdout.write(f'  ✓ Created user: {email}')
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ✗ User not found: {email}')
                        )
                        continue

                # Get groups for these roles
                groups = []
                for role in roles:
                    group = RoleEmailMapping.get_group_for_email_role(role)
                    if group:
                        groups.append(group)
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'  ✗ No group mapping for role: {role}')
                        )

                updates.append((user, email, roles, groups))

        # Apply updates
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY-RUN MODE] Changes not applied\n'))

        with transaction.atomic():
            for user, email, roles, groups in updates:
                if dry_run:
                    current_groups = list(user.groups.values_list('name', flat=True))
                    new_groups = [g.name for g in groups]
                    self.stdout.write(
                        f'  [DRY-RUN] {email}:'
                        f'\n    Roles: {", ".join(roles)}'
                        f'\n    Current groups: {", ".join(current_groups) or "None"}'
                        f'\n    New groups: {", ".join(new_groups) or "None"}'
                    )
                else:
                    user.groups.set(groups)
                    group_names = [g.name for g in groups]
                    self.stdout.write(
                        f'  ✓ {email}: {", ".join(roles)} → {", ".join(group_names) or "No groups"}'
                    )
