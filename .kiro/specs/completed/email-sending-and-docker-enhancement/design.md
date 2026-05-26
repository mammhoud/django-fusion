# Design — Email Sending & Docker Enhancement

## Architecture Overview

```
emails.csv
    ↓
send_invitations_from_csv command
    ├── Parse CSV (email, role)
    ├── For each record:
    │   ├── Get or create Group (from role name)
    │   ├── Get or create Role
    │   ├── Create/get User
    │   ├── Assign first role to user
    │   ├── Add user to all role groups
    │   └── Send invitation email
    └── Log results to EmailLog
```

## Component Designs

### Design 1 — Role and Group Models

**Location**: `django_seed/models.py` or `django_seed/models/roles.py`

```python
class UserRole(models.Model):
    """User role (instructor, manager, content_manager, supervisor, admin)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserGroup(models.Model):
    """User group with role associations"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    roles = models.ManyToManyField(UserRole, related_name='groups')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
```

### Design 2 — Email Sending Command

**Location**: `django_seed/management/commands/send_invitations_from_csv.py`

```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str)

    def handle(self, *args, **options):
        csv_file = options['csv_file']

        # Parse CSV
        records = CSVParser(csv_file).parse()

        for record in records:
            email = record['email']
            roles = record['role'].split('/')  # Handle multiple roles

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'username': email.split('@')[0]}
            )

            # Process roles
            first_role = None
            for role_name in roles:
                # Get or create role
                role, _ = UserRole.objects.get_or_create(
                    name=role_name.strip()
                )

                if first_role is None:
                    first_role = role

                # Get or create group
                group, _ = UserGroup.objects.get_or_create(
                    name=role_name.strip()
                )
                group.roles.add(role)

                # Add user to group
                user.groups.add(group)

            # Assign first role
            if first_role:
                user.role = first_role
                user.save()

            # Send invitation email
            EmailService.send_invitation(user, email)
```

### Design 3 — Docker Rebuild Process

**Steps**:
1. Stop containers: `docker-compose down -v`
2. Rebuild images: `docker-compose up -d --build`
3. Run migrations: `python manage.py migrate`
4. Verify health: `docker ps` and health checks

### Design 4 — Selenium Tests

**Location**: `tests/selenium/test_auth.py`

```python
class TestLoginFlow(SeleniumTestCase):
    def test_login_page_loads(self):
        self.browser.get(self.live_server_url + '/login/')
        self.assertIn('Login', self.browser.title)

    def test_login_form_submission(self):
        # Fill form, submit, verify redirect
        pass

class TestAdminPage(SeleniumTestCase):
    def test_admin_dashboard_loads(self):
        # Login as admin
        # Navigate to admin
        # Verify assets load
        pass
```

## Data Flow

```
CSV Input
  ↓
Parse Records
  ↓
For Each Record:
  ├─ Create/Get User
  ├─ Create/Get Roles
  ├─ Create/Get Groups
  ├─ Assign Roles to User
  ├─ Add User to Groups
  └─ Send Email
  ↓
EmailLog Records
  ↓
Database State Updated
```

## File Changes

| File | Change |
|------|--------|
| `django_seed/models.py` | Add/verify UserRole, UserGroup models |
| `django_seed/management/commands/send_invitations_from_csv.py` | New command |
| `tests/selenium/test_auth.py` | New Selenium tests |
| `docker-compose.yml` | Rebuild containers |

