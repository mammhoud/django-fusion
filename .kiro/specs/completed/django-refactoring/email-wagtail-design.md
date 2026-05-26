# Email Testing and Wagtail Integration Design

## Overview
This document outlines the design for enhanced email testing with CSV integration and Wagtail group/role management.

## 1. Email Testing System Design

### 1.1 CSV File Structure
```
test_email.csv structure:
email,role,group,permissions
user1@example.com,admin,Administrators,all
user2@example.com,editor,Editors,edit_content
user3@example.com,viewer,Viewers,view_content
```

### 1.2 Email Service Enhancement
```python
class EnhancedEmailService(EmailService):
    """Enhanced email service with CSV integration"""

    def __init__(self, csv_file_path: str = None):
        super().__init__()
        self.csv_file_path = csv_file_path or "test_email.csv"
        self.email_data = self.load_email_data()

    def load_email_data(self) -> List[Dict]:
        """Load email data from CSV file"""
        data = []
        with open(self.csv_file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data

    def send_role_based_email(self, role: str, template_name: str, context: Dict = None) -> Dict:
        """Send email to all users with specific role"""
        recipients = [row for row in self.email_data if row['role'] == role]
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }

        for recipient in recipients:
            try:
                success = self.send_email(
                    to=recipient['email'],
                    template_name=template_name,
                    context=context or {}
                )
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to send to {recipient['email']}")
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))

        return results
```

### 1.3 Management Commands
```python
# management/commands/send_invite_emails.py
class Command(BaseCommand):
    help = 'Send invitation emails from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('--csv-file', type=str, help='CSV file path')
        parser.add_argument('--role', type=str, help='Filter by role')
        parser.add_argument('--template', type=str, required=True, help='Email template')

    def handle(self, *args, **options):
        service = EnhancedEmailService(options['csv_file'])
        role = options.get('role')

        if role:
            results = service.send_role_based_email(role, options['template'])
        else:
            results = service.send_bulk_emails(options['template'])

        self.stdout.write(f"Sent: {results['sent']}")
        self.stdout.write(f"Failed: {results['failed']}")
```

## 2. Wagtail Group and Role Integration

### 2.1 Group Structure
```python
class WagtailGroupManager:
    """Manage Wagtail groups and roles"""

    def __init__(self):
        self.groups = {}
        self.load_groups()

    def load_groups(self):
        """Load groups from CSV or database"""
        # Load from CSV or sync with existing Wagtail groups
        self.groups = {
            'admin': {
                'name': 'Administrators',
                'permissions': ['add', 'change', 'delete', 'publish'],
                'parent': None
            },
            'editor': {
                'name': 'Editors',
                'permissions': ['add', 'change', 'publish'],
                'parent': 'admin'
            },
            'viewer': {
                'name': 'Viewers',
                'permissions': ['view'],
                'parent': 'editor'
            }
        }

    def get_main_role(self, roles: List[str]) -> str:
        """Get main role (first in list)"""
        return roles[0] if roles else None

    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role with inheritance"""
        if role not in self.groups:
            return []

        permissions = set(self.groups[role]['permissions'])
        parent = self.groups[role].get('parent')

        # Inherit permissions from parent
        while parent:
            if parent in self.groups:
                permissions.update(self.groups[parent]['permissions'])
                parent = self.groups[parent].get('parent')
            else:
                break

        return list(permissions)
```

### 2.2 Permission Inheritance
```python
class PermissionInheritance:
    """Handle permission inheritance for Wagtail groups"""

    def __init__(self):
        self.permission_map = {
            'admin': ['all'],
            'editor': ['add_page', 'change_page', 'publish_page'],
            'viewer': ['view_page']
        }

    def get_inherited_permissions(self, role: str) -> List[str]:
        """Get all permissions including inherited ones"""
        permissions = set()

        # Add direct permissions
        if role in self.permission_map:
            permissions.update(self.permission_map[role])

        # Add inherited permissions based on role hierarchy
        if role == 'viewer':
            # Viewer inherits from editor
            permissions.update(self.permission_map.get('editor', []))
        elif role == 'editor':
            # Editor inherits from admin
            permissions.update(self.permission_map.get('admin', []))

        return list(permissions)
```

## 3. Data Loading System

### 3.1 Comprehensive Data Fixtures
```python
class DataLoader:
    """Load comprehensive test data with translations"""

    def __init__(self):
        self.languages = ['en', 'ar', 'fr', 'es']
        self.models = [
            'auth.User',
            'wagtailcore.Page',
            'wagtailcore.Site',
            'wagtailimages.Image',
            'wagtaildocs.Document'
        ]

    def create_fixture_file(self) -> str:
        """Create comprehensive fixture file"""
        fixture_data = []

        # Add users
        fixture_data.extend(self.create_user_fixtures())

        # Add pages with translations
        fixture_data.extend(self.create_page_fixtures())

        # Add images and documents
        fixture_data.extend(self.create_media_fixtures())

        # Save to file
        fixture_file = 'complete_fixture.json'
        with open(fixture_file, 'w') as f:
            json.dump(fixture_data, f, indent=2)

        return fixture_file

    def create_user_fixtures(self) -> List[Dict]:
        """Create user fixtures with different roles"""
        users = []

        # Admin user
        users.append({
            "model": "auth.user",
            "pk": 1,
            "fields": {
                "username": "admin",
                "email": "vresume@structa.cloud",
                "is_staff": True,
                "is_superuser": True,
                "groups": [1]  # Administrators group
            }
        })

        # Editor user
        users.append({
            "model": "auth.user",
            "pk": 2,
            "fields": {
                "username": "editor",
                "email": "editor@example.com",
                "is_staff": True,
                "is_superuser": False,
                "groups": [2]  # Editors group
            }
        })

        return users
```

### 3.2 Docker Data Loading Command
```bash
# docker-compose.yml addition
services:
  web:
    command: >
      sh -c "
      python manage.py migrate &&
      python manage.py loaddata complete_fixture.json &&
      python manage.py runserver 0.0.0.0:8000
      "
```

## 4. Privacy Policy Modal System

### 4.1 HTMX Modal Component
```html
<!-- privacy_policy_modal.html -->
<div id="privacy-policy-modal" class="modal"
     hx-get="/privacy-policy/content/"
     hx-trigger="load"
     hx-target="#modal-content">
  <div class="modal-content">
    <div id="modal-content">
      <!-- Content loaded via HTMX -->
    </div>
    <button class="close-modal"
            hx-get="/privacy-policy/close/"
            hx-target="#privacy-policy-modal"
            hx-swap="outerHTML">
      Close
    </button>
  </div>
</div>
```

### 4.2 Privacy Policy Views
```python
class PrivacyPolicyView(View):
    """Handle privacy policy modal"""

    def get(self, request):
        """Get privacy policy content"""
        policy = PrivacyPolicy.objects.latest('created_at')

        if request.headers.get('HX-Request'):
            # Return HTML fragment for HTMX
            return render(request, 'privacy_policy_content.html', {
                'policy': policy
            })

        # Return full page
        return render(request, 'privacy_policy_page.html', {
            'policy': policy
        })
```

## 5. Notes System Enhancement

### 5.1 Notes Model
```python
class UserNote(models.Model):
    """User notes with database persistence"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated_at']

    def save_note(self, title: str, content: str) -> 'UserNote':
        """Save or update note"""
        self.title = title
        self.content = content
        self.save()
        return self
```

### 5.2 Notes Modal Interface
```html
<!-- notes_modal.html -->
<div id="notes-modal" class="modal">
  <div class="modal-header">
    <h3>My Notes</h3>
    <button class="close" hx-get="/notes/close/" hx-target="#notes-modal">×</button>
  </div>

  <div class="modal-body">
    <!-- Notes list loaded via HTMX -->
    <div id="notes-list" hx-get="/notes/list/" hx-trigger="load">
      Loading notes...
    </div>

    <!-- Add new note form -->
    <form hx-post="/notes/create/" hx-target="#notes-list">
      <input type="text" name="title" placeholder="Note title" required>
      <textarea name="content" placeholder="Note content" required></textarea>
      <button type="submit">Save Note</button>
    </form>
  </div>
</div>
```

## 6. Email Testing Workflow

### 6.1 Test Workflow
```python
class EmailTestWorkflow:
    """Complete email testing workflow"""

    def run_complete_test(self):
        """Run complete email testing workflow"""
        results = {
            'csv_parsing': self.test_csv_parsing(),
            'email_sending': self.test_email_sending(),
            'role_based': self.test_role_based_emails(),
            'wagtail_integration': self.test_wagtail_integration()
        }

        return results

    def test_csv_parsing(self) -> Dict:
        """Test CSV file parsing"""
        try:
            service = EnhancedEmailService('test_email.csv')
            data = service.load_email_data()
            return {
                'success': True,
                'count': len(data),
                'data': data[:5]  # First 5 records
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

## 7. Implementation Strategy

### 7.1 Phase 1: Foundation
1. Enhanced email service with CSV integration
2. Basic Wagtail group management
3. Simple data loading

### 7.2 Phase 2: Integration
1. Role-based email templates
2. Permission inheritance
3. Privacy policy modal

### 7.3 Phase 3: Enhancement
1. Notes system with modal interface
2. Comprehensive data fixtures
3. Docker integration

### 7.4 Phase 4: Testing
1. Complete email testing suite
2. Integration testing
3. Performance testing

## 8. Success Metrics

### 8.1 Email System Metrics
- Email delivery rate: > 99%
- CSV parsing accuracy: 100%
- Role-based filtering: 100% accurate

### 8.2 Wagtail Integration Metrics
- Group synchronization: 100%
- Permission inheritance: Working correctly
- Content access control: Properly enforced

### 8.3 User Experience Metrics
- Modal loading time: < 1 second
- Notes persistence: 100% reliable
- Privacy policy compliance: 100%

This design provides a comprehensive solution for email testing with CSV integration, Wagtail group management, and enhanced user experience features.</string>
