# Blog and LMS Wagtail CMS Integration - Design Document

**Category Context: Integration**
- **Category**: Integration
- **Scope**: System integrations, API connections, data synchronization, component interoperability
- **Related Specs**: blog-lms-wagtail-integration
- **Common Patterns**: API integration, data sync, system-to-system connections, middleware
- **Avoid Duplicates**: Check existing integration specs before creating new integration features


## Overview

This design document specifies the technical architecture for integrating Blog and Learning Management System (LMS) applications with Wagtail CMS within the Structa project. The integration provides a unified content management platform leveraging Wagtail's page hierarchy, versioning, and publishing workflows while maintaining clean separation of concerns and extensibility.

### Key Design Goals

- Seamless integration with Wagtail CMS for content management
- Comprehensive API endpoints for programmatic access
- Robust data models with proper relationships and constraints
- Property-based testing for correctness verification
- Clear documentation and installation procedures

## System Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Structa Core Project                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Wagtail CMS                           │   │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐ │   │
│  │  │  Blog App        │  │  LMS App                     │ │   │
│  │  │  ┌────────────┐  │  │  ┌────────────────────────┐ │ │   │
│  │  │  │ BlogPost   │  │  │  │ Course                 │ │ │   │
│  │  │  │ Category   │  │  │  │ ├─ Module              │ │ │   │
│  │  │  │ Tag        │  │  │  │ │  └─ Lesson           │ │ │   │
│  │  │  │ Comment    │  │  │  │ Enrollment             │ │ │   │
│  │  │  └────────────┘  │  │  │ Progress               │ │ │   │
│  │  │                  │  │  │ Assessment             │ │ │   │
│  │  │                  │  │  │ Certificate            │ │ │   │
│  │  │                  │  │  └────────────────────────┘ │ │   │
│  │  └──────────────────┘  └──────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────┴──────────────────────────────┐   │
│  │                    API Layer                            │   │
│  │  ┌──────────────────┐  ┌──────────────────────────────┐ │   │
│  │  │ Blog API         │  │ LMS API                      │ │   │
│  │  │ /api/blog/*      │  │ /api/courses/*               │ │   │
│  │  │ /api/categories/ │  │ /api/enrollments/*           │ │   │
│  │  │ /api/tags/       │  │ /api/progress/*              │ │   │
│  │  │ /api/comments/   │  │ /api/assessments/*           │ │   │
│  │  │                  │  │ /api/certificates/*          │ │   │
│  │  └──────────────────┘  └──────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────┴──────────────────────────────┐   │
│  │              Data Persistence Layer                     │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │         PostgreSQL Database                      │  │   │
│  │  │  - Blog tables (posts, categories, tags, etc.)   │  │   │
│  │  │  - LMS tables (courses, enrollments, etc.)       │  │   │
│  │  │  - Wagtail core tables (pages, revisions, etc.)  │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Points with Core Structa

1. **Django Framework**: Both apps extend Django models and use Django ORM
2. **Wagtail CMS**: Blog and LMS apps register custom page types with Wagtail
3. **Authentication**: Leverages Structa's user authentication system
4. **Database**: Uses shared PostgreSQL instance with Structa
5. **API Framework**: Integrates with Django REST Framework for API endpoints
6. **Admin Interface**: Extends Django admin and Wagtail admin

### Plugin Architecture

The Blog and LMS apps follow a plugin architecture pattern:

```
blog_lms_plugin/
├── __init__.py
├── apps.py                 # Django app configuration
├── models/
│   ├── __init__.py
│   ├── blog.py            # Blog models
│   └── lms.py             # LMS models
├── wagtail_hooks.py       # Wagtail integration hooks
├── api/
│   ├── __init__.py
│   ├── serializers.py     # DRF serializers
│   └── views.py           # API viewsets
├── migrations/            # Django migrations
├── templates/             # Wagtail page templates
├── static/                # CSS, JS assets
└── management/
    └── commands/
        └── install_blog_lms.py  # Installation script
```

**Plugin Loading Process**:
1. Installation script adds app to INSTALLED_APPS
2. Django discovers models and creates migrations
3. Wagtail hooks register custom page types
4. API routes are auto-discovered and registered
5. Admin interfaces are configured

## Data Models

### Blog App Models

#### BlogPost Model

```python
class BlogPost(Page):
    """
    Wagtail page type for blog posts with metadata and versioning.
    Inherits from Wagtail's Page model for built-in versioning support.
    """
    author = ForeignKey(User, on_delete=CASCADE, related_name='blog_posts')
    publication_date = DateTimeField(null=True, blank=True)
    meta_description = CharField(max_length=160, blank=True)
    featured_image = ForeignKey(Image, on_delete=SET_NULL, null=True, blank=True)
    content = StreamField([...])  # Rich text content
    is_published = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    # Relationships
    categories = ManyToManyField('Category', related_name='posts')
    tags = ManyToManyField('Tag', related_name='posts')

    class Meta:
        ordering = ['-publication_date']
        indexes = [
            Index(fields=['-publication_date']),
            Index(fields=['author']),
            Index(fields=['is_published']),
        ]
```

#### Category Model

```python
class Category(models.Model):
    """Hierarchical category for organizing blog posts."""
    name = CharField(max_length=100, unique=True)
    slug = SlugField(unique=True)
    description = TextField(blank=True)
    parent = ForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='children')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
```

#### Tag Model

```python
class Tag(models.Model):
    """Simple tag for categorizing blog posts."""
    name = CharField(max_length=50, unique=True)
    slug = SlugField(unique=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
```

#### Comment Model

```python
class Comment(models.Model):
    """User comments on blog posts with moderation support."""
    post = ForeignKey(BlogPost, on_delete=CASCADE, related_name='comments')
    author_name = CharField(max_length=100)
    author_email = EmailField()
    content = TextField()
    parent = ForeignKey('self', on_delete=CASCADE, null=True, blank=True, related_name='replies')
    is_approved = BooleanField(default=False)
    is_spam = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            Index(fields=['post', 'is_approved']),
            Index(fields=['is_spam']),
        ]
```

### LMS App Models

#### Course Model

```python
class Course(Page):
    """
    Wagtail page type for courses with hierarchical structure.
    Inherits from Wagtail's Page model for versioning support.
    """
    instructor = ForeignKey(User, on_delete=CASCADE, related_name='courses')
    description = TextField()
    content = StreamField([...])  # Rich course content
    is_published = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['instructor']),
            Index(fields=['is_published']),
        ]
```

#### Module Model

```python
class Module(models.Model):
    """Logical grouping of lessons within a course."""
    course = ForeignKey(Course, on_delete=CASCADE, related_name='modules')
    title = CharField(max_length=255)
    description = TextField(blank=True)
    learning_objectives = TextField(blank=True)
    order = PositiveIntegerField()
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['course', 'order']
        unique_together = [['course', 'order']]
        indexes = [
            Index(fields=['course', 'order']),
        ]
```

#### Lesson Model

```python
class Lesson(models.Model):
    """Individual learning unit within a module."""
    module = ForeignKey(Module, on_delete=CASCADE, related_name='lessons')
    title = CharField(max_length=255)
    content = TextField()
    learning_outcomes = TextField(blank=True)
    order = PositiveIntegerField()
    duration_minutes = PositiveIntegerField(null=True, blank=True)
    prerequisites = ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_lessons')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['module', 'order']
        unique_together = [['module', 'order']]
        indexes = [
            Index(fields=['module', 'order']),
        ]
```

#### Enrollment Model

```python
class Enrollment(models.Model):
    """Student enrollment in a course."""
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DROPPED = 'dropped'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (COMPLETED, 'Completed'),
        (DROPPED, 'Dropped'),
    ]

    student = ForeignKey(User, on_delete=CASCADE, related_name='enrollments')
    course = ForeignKey(Course, on_delete=CASCADE, related_name='enrollments')
    status = CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    enrolled_at = DateTimeField(auto_now_add=True)
    completed_at = DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['student', 'course']]
        ordering = ['-enrolled_at']
        indexes = [
            Index(fields=['student', 'status']),
            Index(fields=['course', 'status']),
        ]
```

#### Progress Model

```python
class Progress(models.Model):
    """Track student progress through lessons."""
    NOT_STARTED = 'not_started'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    STATUS_CHOICES = [
        (NOT_STARTED, 'Not Started'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]

    enrollment = ForeignKey(Enrollment, on_delete=CASCADE, related_name='progress_records')
    lesson = ForeignKey(Lesson, on_delete=CASCADE, related_name='progress_records')
    status = CharField(max_length=20, choices=STATUS_CHOICES, default=NOT_STARTED)
    progress_percentage = PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    started_at = DateTimeField(null=True, blank=True)
    completed_at = DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['enrollment', 'lesson']]
        ordering = ['lesson__module__order', 'lesson__order']
        indexes = [
            Index(fields=['enrollment', 'status']),
            Index(fields=['lesson']),
        ]
```

#### Assessment Model

```python
class Assessment(models.Model):
    """Quiz or assignment for evaluating learning."""
    MULTIPLE_CHOICE = 'multiple_choice'
    SHORT_ANSWER = 'short_answer'
    ESSAY = 'essay'
    QUESTION_TYPES = [
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (SHORT_ANSWER, 'Short Answer'),
        (ESSAY, 'Essay'),
    ]

    lesson = ForeignKey(Lesson, on_delete=CASCADE, related_name='assessments')
    title = CharField(max_length=255)
    description = TextField(blank=True)
    passing_score = PositiveIntegerField(default=70, validators=[MaxValueValidator(100)])
    time_limit_minutes = PositiveIntegerField(null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['lesson', 'created_at']
        indexes = [
            Index(fields=['lesson']),
        ]
```

#### Certificate Model

```python
class Certificate(models.Model):
    """Digital credential for course completion."""
    enrollment = OneToOneField(Enrollment, on_delete=CASCADE, related_name='certificate')
    certificate_id = CharField(max_length=50, unique=True)
    issued_date = DateTimeField(auto_now_add=True)
    pdf_file = FileField(upload_to='certificates/')
    verification_token = CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['-issued_date']
        indexes = [
            Index(fields=['certificate_id']),
            Index(fields=['verification_token']),
        ]
```

### Database Schema Relationships

```
User (1) ──────────────── (M) BlogPost
  │                            │
  │                            ├─ (M) Category
  │                            ├─ (M) Tag
  │                            └─ (M) Comment
  │
  ├─ (1) ──────────────── (M) Course
  │                            │
  │                            ├─ (1) ──────────────── (M) Module
  │                            │                            │
  │                            │                            └─ (1) ──────────────── (M) Lesson
  │                            │                                                      │
  │                            │                                                      ├─ (M) Assessment
  │                            │                                                      └─ (M) Progress
  │                            │
  │                            └─ (M) Enrollment ──────────────── (1) Certificate
  │                                      │
  │                                      └─ (M) Progress
  │
  └─ (M) Enrollment
```

## API Design

### Blog API Endpoints (Implemented)

**Note**: Only implemented endpoints are documented. Unimplemented DRF endpoints have been removed.

#### Posts (Implemented)

```
GET    /api/blog/posts/                    # List published posts (paginated)
GET    /api/blog/posts/{id}/               # Retrieve single post
```

#### Categories (Implemented)

```
GET    /api/blog/categories/               # List all categories
```

#### Tags (Implemented)

```
GET    /api/blog/tags/                     # List all tags
```

#### Comments (Implemented)

```
GET    /api/blog/posts/{id}/comments/      # List approved comments for post
```

### LMS API Endpoints (Implemented)

**Note**: Only implemented endpoints are documented. Unimplemented DRF endpoints have been removed.

#### Courses (Implemented)

```
GET    /api/courses/                       # List published courses (paginated)
GET    /api/courses/{id}/                  # Retrieve course with modules/lessons
```

#### Enrollments (Implemented)

```
GET    /api/enrollments/                   # List user's enrollments (authenticated)
```

#### Progress (Implemented)

```
GET    /api/progress/                      # List user's progress (authenticated)
GET    /api/progress/{enrollment_id}/      # Get progress for enrollment
```

#### Assessments (Implemented)

```
GET    /api/assessments/                   # List assessments (paginated)
GET    /api/assessments/{id}/              # Retrieve assessment with questions
```

#### Certificates (Implemented)

```
GET    /api/certificates/                  # List user's certificates (authenticated)
GET    /api/certificates/{id}/             # Retrieve certificate details
GET    /api/certificates/verify/{token}/   # Verify certificate authenticity
```

### Request/Response Formats

#### Blog Post Response

```json
{
  "id": 1,
  "title": "Getting Started with Django",
  "slug": "getting-started-with-django",
  "author": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "content": "<p>Rich HTML content...</p>",
  "meta_description": "Learn the basics of Django web framework",
  "featured_image": {
    "id": 1,
    "url": "/media/images/django.jpg",
    "alt_text": "Django logo"
  },
  "categories": [
    {"id": 1, "name": "Web Development", "slug": "web-development"}
  ],
  "tags": [
    {"id": 1, "name": "django"},
    {"id": 2, "name": "python"}
  ],
  "publication_date": "2024-01-15T10:30:00Z",
  "is_published": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "comment_count": 5
}
```

#### Course Response

```json
{
  "id": 1,
  "title": "Advanced Python Programming",
  "slug": "advanced-python-programming",
  "instructor": {
    "id": 2,
    "username": "jane_smith",
    "email": "jane@example.com"
  },
  "description": "Master advanced Python concepts",
  "is_published": true,
  "modules": [
    {
      "id": 1,
      "title": "Module 1: Decorators",
      "description": "Understanding Python decorators",
      "order": 1,
      "lessons": [
        {
          "id": 1,
          "title": "Lesson 1: Function Decorators",
          "order": 1,
          "duration_minutes": 45,
          "prerequisites": []
        }
      ]
    }
  ],
  "enrollment_count": 150,
  "completion_rate": 0.75,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Enrollment Response

```json
{
  "id": 1,
  "student": {
    "id": 3,
    "username": "student_user",
    "email": "student@example.com"
  },
  "course": {
    "id": 1,
    "title": "Advanced Python Programming"
  },
  "status": "active",
  "enrolled_at": "2024-01-10T08:00:00Z",
  "completed_at": null,
  "progress": {
    "total_lessons": 20,
    "completed_lessons": 8,
    "progress_percentage": 40
  }
}
```

### Error Handling

All API endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field_name": ["Error message for this field"]
    }
  }
}
```

**Common Status Codes**:
- 200: Success
- 201: Created
- 400: Bad Request (validation error)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 409: Conflict (e.g., duplicate enrollment)
- 500: Internal Server Error

### Authentication and Authorization

**Authentication Methods**:
- JWT tokens for API access
- Session cookies for web interface
- API key for service-to-service communication

**Authorization Patterns**:
- Blog posts: Author or admin can edit/delete
- Comments: Author or admin can edit/delete
- Courses: Instructor or admin can edit/delete
- Enrollments: Student can view own, instructor can view course enrollments
- Assessments: Instructor can grade, student can view own results

## Installation and Configuration

### Plugin Installation Script

The installation script (`manage.py install_blog_lms`) automates the setup process:

```python
# management/commands/install_blog_lms.py

class Command(BaseCommand):
    """Install Blog and LMS apps into Structa project."""

    def handle(self, *args, **options):
        # 1. Verify Django version compatibility
        # 2. Check for dependency conflicts
        # 3. Add apps to INSTALLED_APPS
        # 4. Run migrations
        # 5. Create initial admin user (optional)
        # 6. Configure Wagtail settings
        # 7. Display installation summary
```

**Installation Flow**:

```
1. Dependency Check
   ├─ Verify Django >= 4.2
   ├─ Verify Wagtail >= 5.0
   ├─ Check for conflicting packages
   └─ Report any issues

2. Database Setup
   ├─ Create migrations
   ├─ Run migrations
   └─ Create indexes

3. Wagtail Configuration
   ├─ Register page types
   ├─ Configure StreamFields
   └─ Set up admin interface

4. API Configuration
   ├─ Register API routes
   ├─ Configure serializers
   └─ Set up authentication

5. Verification
   ├─ Test database connections
   ├─ Verify all models created
   ├─ Check API endpoints
   └─ Display summary
```

### Configuration Settings

**Required Environment Variables**:

```bash
# Blog settings
BLOG_ENABLE_COMMENTS=true
BLOG_COMMENT_MODERATION=true
BLOG_POSTS_PER_PAGE=10

# LMS settings
LMS_ENABLE_CERTIFICATES=true
LMS_CERTIFICATE_TEMPLATE=default
LMS_ASYNC_CERTIFICATE_GENERATION=true

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**Django Settings Configuration**:

```python
# settings.py

INSTALLED_APPS = [
    # ... other apps
    'wagtail',
    'wagtail.admin',
    'wagtail.search',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.contrib.redirects',
    'wagtail.contrib.forms',
    'wagtail.contrib.table_block',
    'wagtail.contrib.typed_table_block',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.contrib.settings',
    'wagtail.api.v2',
    'rest_framework',
    'corsheaders',
    'blog_lms',  # Our plugin
]

# Blog and LMS Configuration
BLOG_SETTINGS = {
    'ENABLE_COMMENTS': True,
    'COMMENT_MODERATION': True,
    'POSTS_PER_PAGE': 10,
    'AUTO_GENERATE_SLUG': True,
}

LMS_SETTINGS = {
    'ENABLE_CERTIFICATES': True,
    'CERTIFICATE_TEMPLATE': 'default',
    'ASYNC_CERTIFICATE_GENERATION': True,
    'PASSING_SCORE_DEFAULT': 70,
}
```

### Database Migration Strategy

**Migration Phases**:

1. **Initial Setup**: Create all Blog and LMS tables
2. **Relationships**: Add foreign keys and constraints
3. **Indexes**: Create performance indexes
4. **Data Migration**: Populate initial data if needed

**Migration Files**:

```
migrations/
├── 0001_initial.py          # Create Blog models
├── 0002_initial_lms.py      # Create LMS models
├── 0003_add_indexes.py      # Add performance indexes
└── 0004_initial_data.py     # Populate initial data
```

### Initial Setup Procedures

**Step 1: Install Dependencies**

```bash
pip install wagtail>=5.0 djangorestframework django-cors-headers
```

**Step 2: Run Installation Script**

```bash
python manage.py install_blog_lms
```

**Step 3: Create Admin User**

```bash
python manage.py createsuperuser
```

**Step 4: Collect Static Files**

```bash
python manage.py collectstatic --noinput
```

**Step 5: Start Development Server**

```bash
python manage.py runserver
```

**Step 6: Access Admin Interface**

Navigate to `http://localhost:8000/admin/` and log in with admin credentials.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Blog Post Metadata Persistence

*For any* blog post with all required metadata fields (author, publication_date, tags, categories, meta_description), when the post is created and retrieved from the database, all fields should match exactly including nested relationships.

**Validates: Requirements 1.2, 2.1**

### Property 2: Draft Post Access Control

*For any* blog post in Draft_State and any unauthenticated user, attempting to access the post should return a 403 Forbidden response. For the post author or admin, access should be allowed.

**Validates: Requirements 1.4, 4.3**

### Property 3: Published Post Visibility

*For any* blog post transitioned to Published_State, the post should be publicly accessible and the publication_date should be set to a timestamp within the last minute.

**Validates: Requirements 1.5, 4.4**

### Property 4: Slug Uniqueness

*For any* set of blog posts with identical titles, each post should have a unique slug. If conflicts occur, numeric suffixes should be appended (e.g., "my-post", "my-post-2", "my-post-3").

**Validates: Requirements 1.6, 1.7**

### Property 5: Version History Preservation

*For any* blog post that is edited multiple times, all previous versions should be preserved in the version history with timestamps and author information.

**Validates: Requirements 1.3, 4.2**

### Property 6: Tag-Based Filtering

*For any* set of blog posts and any tag, filtering posts by that tag should return only posts that have that tag assigned, and the returned set should be a subset of all posts.

**Validates: Requirements 2.4, 25.1**

### Property 7: Hierarchical Categories

*For any* category with a parent category, the parent-child relationship should be maintained and queryable. Filtering by a parent category should return all posts in that category and its subcategories.

**Validates: Requirements 2.5**

### Property 8: Meta Description Validation

*For any* blog post with a meta_description, the description should be between 120-160 characters. If not provided, an auto-generated description should be created from the post excerpt.

**Validates: Requirements 2.6, 2.7**

### Property 9: Comment Moderation

*For any* comment submitted on a published blog post, the comment should not be publicly visible until explicitly approved by a moderator. Once approved, it should appear with the commenter's name and timestamp.

**Validates: Requirements 3.2, 3.3, 3.4**

### Property 10: Nested Comments Structure

*For any* comment with a parent comment (reply), the nested structure should be maintained and queryable. Retrieving comments should return the complete thread hierarchy.

**Validates: Requirements 3.5**

### Property 11: Course Hierarchical Structure

*For any* course with modules and lessons, the hierarchical relationships should be maintained: Course → Modules → Lessons. Querying a course should return all modules with all their lessons in order.

**Validates: Requirements 6.3, 6.4, 7.1**

### Property 12: Draft Course Enrollment Prevention

*For any* course in Draft_State, attempting to enroll should return a 403 Forbidden response. Only published courses should allow enrollment.

**Validates: Requirements 6.5, 6.6**

### Property 13: Enrollment Uniqueness

*For any* student and course combination, creating multiple enrollment records should result in only one Enrollment record existing in the database. Subsequent enrollment attempts should return the existing record.

**Validates: Requirements 8.1, 24.2**

### Property 14: Progress Calculation

*For any* enrollment, the progress percentage should equal (completed_lessons / total_lessons) * 100. When all lessons are completed, progress should be 100%.

**Validates: Requirements 8.2, 8.3**

### Property 15: Module Completion

*For any* module, when all lessons in that module are marked as completed, the module should automatically be marked as complete.

**Validates: Requirements 8.4**

### Property 16: Course Completion

*For any* course, when all modules in that course are marked as complete, the course should automatically be marked as complete and a Certificate should be generated.

**Validates: Requirements 8.5, 10.1**

### Property 17: Assessment Scoring

*For any* assessment with multiple choice questions, when a student submits responses, the score should be calculated as (correct_answers / total_questions) * 100. The score should be stored with the submission.

**Validates: Requirements 9.3, 9.4**

### Property 18: Certificate Uniqueness

*For any* course completion, generating a certificate multiple times should produce identical certificates with the same certificate_id and verification_token.

**Validates: Requirements 10.2, 10.3, 24.3**

### Property 19: Certificate Verification

*For any* certificate with a verification_token, accessing the verification endpoint with that token should return the certificate details and confirm authenticity.

**Validates: Requirements 10.6**

### Property 20: Blog Post Round-Trip Serialization

*For any* blog post, serializing it to JSON and deserializing it should produce an equivalent BlogPost object with all fields matching exactly, including nested relationships (author, categories, tags).

**Validates: Requirements 22.1, 23.1**

### Property 21: Course Round-Trip Serialization

*For any* course with modules and lessons, serializing it to JSON and deserializing it should produce an equivalent Course object with the complete hierarchical structure intact.

**Validates: Requirements 22.2, 23.2**

### Property 22: Enrollment Round-Trip Serialization

*For any* enrollment, serializing it to JSON and deserializing it should produce an equivalent Enrollment object with all fields and relationships preserved.

**Validates: Requirements 23.3**

### Property 23: Assessment Round-Trip Serialization

*For any* assessment with questions, serializing it to JSON and deserializing it should produce an equivalent Assessment object with all questions and their properties preserved.

**Validates: Requirements 23.4**

### Property 24: Idempotent Blog Post Publishing

*For any* blog post, publishing it multiple times should result in the same published state without creating duplicate records or side effects.

**Validates: Requirements 24.1**

### Property 25: Idempotent Comment Approval

*For any* comment, approving it multiple times should result in the same approved state without duplication or side effects.

**Validates: Requirements 24.4**

### Property 26: Idempotent Progress Update

*For any* enrollment and lesson, marking the lesson as complete multiple times should result in only one progress record with the same completion status.

**Validates: Requirements 24.5**

### Property 27: Enrollment Count Constraint

*For any* course, the number of enrollments should be less than or equal to the total number of users in the system.

**Validates: Requirements 25.2**

### Property 28: Lesson Completion Constraint

*For any* course, the number of completed lessons should be less than or equal to the total number of lessons in the course.

**Validates: Requirements 25.3**

### Property 29: Certificate Count Constraint

*For any* course, the number of issued certificates should be less than or equal to the number of completed enrollments.

**Validates: Requirements 25.5**

### Property 30: Comment Moderation Constraint

*For any* blog post, the number of approved comments should be less than or equal to the total number of comments submitted.

**Validates: Requirements 25.6**

## Error Handling

### Blog App Error Scenarios

**Post Creation Errors**:
- Invalid author (user doesn't exist): Return 400 Bad Request
- Duplicate slug: Auto-append numeric suffix
- Missing required fields: Return 400 with field-specific errors
- Unauthorized user: Return 401 Unauthorized

**Comment Submission Errors**:
- Post not found: Return 404 Not Found
- Invalid email format: Return 400 Bad Request
- Spam detected: Flag for review, return 202 Accepted
- Comment moderation required: Return 202 Accepted

**Category/Tag Errors**:
- Duplicate name: Return 409 Conflict
- Invalid parent category: Return 400 Bad Request
- Circular hierarchy: Return 400 Bad Request

### LMS App Error Scenarios

**Enrollment Errors**:
- Course not published: Return 403 Forbidden
- Student already enrolled: Return 409 Conflict
- Course not found: Return 404 Not Found
- User not authenticated: Return 401 Unauthorized

**Progress Update Errors**:
- Lesson not found: Return 404 Not Found
- Enrollment not found: Return 404 Not Found
- Invalid progress percentage: Return 400 Bad Request
- Prerequisite not completed: Return 403 Forbidden

**Assessment Errors**:
- Assessment not found: Return 404 Not Found
- Time limit exceeded: Return 400 Bad Request
- Invalid response format: Return 400 Bad Request
- Assessment already submitted: Return 409 Conflict

**Certificate Errors**:
- Course not completed: Return 403 Forbidden
- Certificate already generated: Return 409 Conflict
- Invalid verification token: Return 404 Not Found

### Error Response Format

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field_name": ["Specific error for this field"],
      "another_field": ["Another error"]
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Logging and Monitoring

- All errors logged with context (user, resource, action)
- Critical errors (database failures) trigger alerts
- API errors tracked for analytics
- Failed operations logged for debugging

## Testing Strategy

### Dual Testing Approach

The testing strategy combines unit tests and property-based tests for comprehensive coverage:

**Unit Tests**: Verify specific examples, edge cases, and error conditions
- Test individual model methods
- Test API endpoint responses
- Test error handling
- Test edge cases (empty inputs, null values, etc.)

**Property-Based Tests**: Verify universal properties across all inputs
- Test data persistence and retrieval
- Test serialization round-trips
- Test idempotent operations
- Test metamorphic relationships

### Property-Based Testing Configuration

**Testing Library**: Hypothesis (Python)

**Test Structure**:

```python
from hypothesis import given, strategies as st
from blog_lms.models import BlogPost, Course, Enrollment

class TestBlogPostProperties:
    """Property-based tests for Blog Post model."""

    @given(st.text(min_size=1, max_size=255), st.emails())
    def test_blog_post_metadata_persistence(self, title, author_email):
        """
        Property 1: Blog Post Metadata Persistence
        For any blog post with all required metadata fields, when the post is
        created and retrieved from the database, all fields should match exactly.

        Feature: blog-lms-wagtail-integration, Property 1: Blog Post Metadata Persistence
        """
        # Generate random blog post
        post = BlogPost.objects.create(
            title=title,
            author=self.user,
            meta_description="Test description"
        )

        # Retrieve from database
        retrieved = BlogPost.objects.get(id=post.id)

        # Verify all fields match
        assert retrieved.title == post.title
        assert retrieved.author == post.author
        assert retrieved.meta_description == post.meta_description

class TestEnrollmentProperties:
    """Property-based tests for Enrollment model."""

    @given(st.integers(min_value=1, max_value=100))
    def test_enrollment_uniqueness(self, student_id):
        """
        Property 13: Enrollment Uniqueness
        For any student and course combination, creating multiple enrollment
        records should result in only one Enrollment record existing.

        Feature: blog-lms-wagtail-integration, Property 13: Enrollment Uniqueness
        """
        # Attempt to create multiple enrollments
        enrollment1 = Enrollment.objects.create(
            student_id=student_id,
            course_id=self.course.id
        )

        # Second attempt should fail or return existing
        try:
            enrollment2 = Enrollment.objects.create(
                student_id=student_id,
                course_id=self.course.id
            )
            # Should not reach here due to unique constraint
            assert False, "Should have raised IntegrityError"
        except IntegrityError:
            # Expected behavior
            pass

        # Verify only one enrollment exists
        count = Enrollment.objects.filter(
            student_id=student_id,
            course_id=self.course.id
        ).count()
        assert count == 1
```

**Test Configuration**:

```python
# conftest.py or settings for tests

HYPOTHESIS_SETTINGS = {
    'max_examples': 100,  # Minimum 100 iterations per property test
    'deadline': None,     # No time limit per example
}

# In test files
from hypothesis import settings

@settings(max_examples=100)
@given(...)
def test_property(...):
    pass
```

### Unit Testing Examples

```python
class TestBlogPostAPI(TestCase):
    """Unit tests for Blog Post API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'pass')
        self.post = BlogPost.objects.create(
            title='Test Post',
            author=self.user,
            is_published=True
        )

    def test_list_published_posts(self):
        """Test retrieving list of published posts."""
        response = self.client.get('/api/blog/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_draft_post_not_visible(self):
        """Test that draft posts are not visible to unauthenticated users."""
        draft_post = BlogPost.objects.create(
            title='Draft Post',
            author=self.user,
            is_published=False
        )
        response = self.client.get(f'/api/blog/posts/{draft_post.id}/')
        self.assertEqual(response.status_code, 403)

    def test_create_post_requires_authentication(self):
        """Test that creating a post requires authentication."""
        response = self.client.post('/api/blog/posts/', {
            'title': 'New Post',
            'content': 'Content'
        })
        self.assertEqual(response.status_code, 401)

    def test_comment_moderation(self):
        """Test that comments require moderation before appearing."""
        response = self.client.post(f'/api/blog/posts/{self.post.id}/comments/', {
            'author_name': 'John',
            'author_email': 'john@example.com',
            'content': 'Great post!'
        })
        self.assertEqual(response.status_code, 201)

        # Comment should not be approved yet
        comment = Comment.objects.latest('id')
        self.assertFalse(comment.is_approved)
```

### Test Coverage Goals

- **Models**: 90%+ coverage of model methods and properties
- **API Endpoints**: 85%+ coverage of all endpoints
- **Error Handling**: 100% coverage of error scenarios
- **Properties**: All 30 correctness properties tested

### Continuous Integration

Tests run automatically on:
- Every commit to main branch
- Every pull request
- Nightly full test suite run

**Test Command**:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=blog_lms --cov-report=html

# Run property-based tests only
pytest tests/ -k "property" -v

# Run specific test class
pytest tests/test_blog.py::TestBlogPostProperties -v
```

## Documentation Structure

### Model Documentation Template

Each model should be documented with the following structure:

```markdown
## [Model Name]

### Overview
Brief description of the model's purpose and role in the system.

### Fields
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| field_name | CharField | Yes | Description of field |

### Relationships
- **Foreign Keys**: Description of relationships
- **Many-to-Many**: Description of relationships
- **Reverse Relations**: Description of reverse relationships

### Methods
- `method_name()`: Description of what the method does

### Example Queries
\`\`\`python
# Get all active posts
BlogPost.objects.filter(is_published=True)

# Get posts by author
BlogPost.objects.filter(author=user)
\`\`\`

### Constraints
- Unique constraints
- Check constraints
- Index information
```

### API Reference Format

```markdown
## [Endpoint Name]

### Description
Brief description of what the endpoint does.

### HTTP Method
GET | POST | PUT | DELETE

### URL
`/api/path/to/endpoint/`

### Authentication
Required | Optional | None

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| param_name | string | Yes | Description |

### Request Body
\`\`\`json
{
  "field": "value"
}
\`\`\`

### Response
**Status Code**: 200 OK

\`\`\`json
{
  "id": 1,
  "field": "value"
}
\`\`\`

### Error Responses
| Status | Code | Message |
|--------|------|---------|
| 400 | VALIDATION_ERROR | Invalid input |
| 401 | UNAUTHORIZED | Authentication required |

### Examples
\`\`\`bash
curl -X GET http://localhost:8000/api/endpoint/ \
  -H "Authorization: Bearer TOKEN"
\`\`\`
```

### Installation Guide Structure

```markdown
# Installation Guide

## Prerequisites
- Python 3.9+
- Django 4.2+
- PostgreSQL 12+

## Step-by-Step Installation

### 1. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Run Installation Script
\`\`\`bash
python manage.py install_blog_lms
\`\`\`

### 3. Verify Installation
\`\`\`bash
python manage.py test blog_lms
\`\`\`

## Troubleshooting
- Common issues and solutions
- FAQ
- Support contacts
```

### Configuration Guide Structure

```markdown
# Configuration Guide

## Environment Variables

### Blog Settings
- `BLOG_ENABLE_COMMENTS`: Enable/disable comments (default: true)
- `BLOG_COMMENT_MODERATION`: Require moderation (default: true)

### LMS Settings
- `LMS_ENABLE_CERTIFICATES`: Enable/disable certificates (default: true)
- `LMS_ASYNC_CERTIFICATE_GENERATION`: Generate certificates asynchronously (default: true)

## Django Settings

### INSTALLED_APPS
Add the following to your INSTALLED_APPS:
\`\`\`python
INSTALLED_APPS = [
    'blog_lms',
]
\`\`\`

### Configuration Options
\`\`\`python
BLOG_SETTINGS = {
    'ENABLE_COMMENTS': True,
    'COMMENT_MODERATION': True,
}
\`\`\`

## Best Practices
- Security considerations
- Performance optimization
- Backup strategies
```

### Feature Documentation Template

```markdown
# [Feature Name]

## Overview
Description of the feature and its purpose.

## User Guide

### Getting Started
Step-by-step instructions for using the feature.

### Common Tasks
- Task 1: How to...
- Task 2: How to...

### Advanced Usage
For power users and administrators.

## Screenshots
[Include relevant screenshots]

## Limitations
Known limitations and workarounds.

## FAQ
Frequently asked questions and answers.
```

### Documentation Files to Create

```
docs/
├── models/
│   ├── blog-models.md          # Blog model documentation
│   ├── lms-models.md           # LMS model documentation
│   └── relationships.md        # Model relationships and ERD
├── api/
│   ├── blog-api.md             # Blog API reference
│   ├── lms-api.md              # LMS API reference
│   └── authentication.md       # API authentication guide
├── installation/
│   ├── installation-guide.md   # Step-by-step installation
│   ├── requirements.md         # System requirements
│   └── troubleshooting.md      # Common issues
├── configuration/
│   ├── configuration-guide.md  # Configuration options
│   ├── environment-variables.md # Environment setup
│   └── security.md             # Security best practices
├── features/
│   ├── blog-features.md        # Blog feature guide
│   ├── lms-features.md         # LMS feature guide
│   ├── comments.md             # Comment system guide
│   └── assessments.md          # Assessment guide
└── development/
    ├── architecture.md         # System architecture
    ├── testing.md              # Testing guide
    └── contributing.md         # Contribution guidelines
```

## Pretty Printer Implementation

### Purpose

The pretty printer converts serialized data structures back to human-readable format for verification and debugging. It ensures data integrity through serialization cycles and provides clear output for testing.

### Pretty Printer Design

```python
# utils/pretty_printer.py

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

class PrettyPrinter:
    """Format data structures into human-readable JSON."""

    @staticmethod
    def format_blog_post(post: 'BlogPost') -> str:
        """Format BlogPost object to indented JSON."""
        data = {
            'id': post.id,
            'title': post.title,
            'slug': post.slug,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'email': post.author.email,
            },
            'content': post.content,
            'meta_description': post.meta_description,
            'categories': [
                {'id': c.id, 'name': c.name, 'slug': c.slug}
                for c in post.categories.all()
            ],
            'tags': [
                {'id': t.id, 'name': t.name, 'slug': t.slug}
                for t in post.tags.all()
            ],
            'publication_date': post.publication_date.isoformat() if post.publication_date else None,
            'is_published': post.is_published,
            'created_at': post.created_at.isoformat(),
            'updated_at': post.updated_at.isoformat(),
        }
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_course(course: 'Course') -> str:
        """Format Course object with hierarchical structure."""
        data = {
            'id': course.id,
            'title': course.title,
            'slug': course.slug,
            'instructor': {
                'id': course.instructor.id,
                'username': course.instructor.username,
            },
            'description': course.description,
            'is_published': course.is_published,
            'modules': [
                {
                    'id': module.id,
                    'title': module.title,
                    'order': module.order,
                    'lessons': [
                        {
                            'id': lesson.id,
                            'title': lesson.title,
                            'order': lesson.order,
                            'duration_minutes': lesson.duration_minutes,
                        }
                        for lesson in module.lessons.all()
                    ]
                }
                for module in course.modules.all()
            ],
            'created_at': course.created_at.isoformat(),
            'updated_at': course.updated_at.isoformat(),
        }
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_enrollment(enrollment: 'Enrollment') -> str:
        """Format Enrollment object with progress."""
        progress_records = enrollment.progress_records.all()
        completed = progress_records.filter(status='completed').count()
        total = progress_records.count()

        data = {
            'id': enrollment.id,
            'student': {
                'id': enrollment.student.id,
                'username': enrollment.student.username,
            },
            'course': {
                'id': enrollment.course.id,
                'title': enrollment.course.title,
            },
            'status': enrollment.status,
            'enrolled_at': enrollment.enrolled_at.isoformat(),
            'completed_at': enrollment.completed_at.isoformat() if enrollment.completed_at else None,
            'progress': {
                'completed_lessons': completed,
                'total_lessons': total,
                'progress_percentage': (completed / total * 100) if total > 0 else 0,
            }
        }
        return json.dumps(data, indent=2, default=str)

    @staticmethod
    def format_assessment(assessment: 'Assessment') -> str:
        """Format Assessment object with questions."""
        data = {
            'id': assessment.id,
            'title': assessment.title,
            'description': assessment.description,
            'passing_score': assessment.passing_score,
            'time_limit_minutes': assessment.time_limit_minutes,
            'questions': [
                {
                    'id': q.id,
                    'text': q.question_text,
                    'type': q.question_type,
                    'order': q.order,
                }
                for q in assessment.questions.all()
            ],
            'created_at': assessment.created_at.isoformat(),
        }
        return json.dumps(data, indent=2, default=str)
```

### Usage Examples

```python
# In tests or debugging
from blog_lms.utils.pretty_printer import PrettyPrinter

post = BlogPost.objects.get(id=1)
print(PrettyPrinter.format_blog_post(post))

course = Course.objects.get(id=1)
print(PrettyPrinter.format_course(course))
```

## Serialization and Round-Trip Testing

### Round-Trip Property Testing

Round-trip testing verifies that data survives serialization and deserialization cycles:

```python
# tests/test_serialization.py

from hypothesis import given, strategies as st
from blog_lms.models import BlogPost, Course, Enrollment, Assessment
from blog_lms.serializers import (
    BlogPostSerializer, CourseSerializer,
    EnrollmentSerializer, AssessmentSerializer
)

class TestBlogPostSerialization:
    """Test Blog Post serialization round-trips."""

    @given(st.text(min_size=1, max_size=255))
    def test_blog_post_round_trip(self, title):
        """
        Property 20: Blog Post Round-Trip Serialization
        For any blog post, serializing to JSON and deserializing should
        produce an equivalent BlogPost object.

        Feature: blog-lms-wagtail-integration, Property 20: Blog Post Round-Trip Serialization
        """
        # Create original post
        original = BlogPost.objects.create(
            title=title,
            author=self.user,
            meta_description="Test"
        )

        # Serialize
        serializer = BlogPostSerializer(original)
        serialized_data = serializer.data

        # Deserialize
        deserialized = BlogPostSerializer(data=serialized_data)
        assert deserialized.is_valid()

        # Verify equivalence
        assert deserialized.validated_data['title'] == original.title
        assert deserialized.validated_data['author'] == original.author
        assert deserialized.validated_data['meta_description'] == original.meta_description

class TestCourseSerialization:
    """Test Course serialization with nested objects."""

    def test_course_round_trip_with_hierarchy(self):
        """
        Property 21: Course Round-Trip Serialization
        For any course with modules and lessons, serializing to JSON and
        deserializing should preserve the complete hierarchical structure.

        Feature: blog-lms-wagtail-integration, Property 21: Course Round-Trip Serialization
        """
        # Create course with modules and lessons
        course = Course.objects.create(
            title="Python Course",
            instructor=self.user
        )

        module = Module.objects.create(
            course=course,
            title="Module 1",
            order=1
        )

        lesson = Lesson.objects.create(
            module=module,
            title="Lesson 1",
            content="Content",
            order=1
        )

        # Serialize
        serializer = CourseSerializer(course)
        serialized_data = serializer.data

        # Verify structure is preserved
        assert len(serialized_data['modules']) == 1
        assert len(serialized_data['modules'][0]['lessons']) == 1
        assert serialized_data['modules'][0]['lessons'][0]['title'] == "Lesson 1"

        # Deserialize and verify
        deserialized = CourseSerializer(data=serialized_data)
        assert deserialized.is_valid()

class TestEnrollmentSerialization:
    """Test Enrollment serialization."""

    def test_enrollment_round_trip(self):
        """
        Property 22: Enrollment Round-Trip Serialization
        For any enrollment, serializing to JSON and deserializing should
        produce an equivalent Enrollment object.

        Feature: blog-lms-wagtail-integration, Property 22: Enrollment Round-Trip Serialization
        """
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            status='active'
        )

        serializer = EnrollmentSerializer(enrollment)
        serialized_data = serializer.data

        deserialized = EnrollmentSerializer(data=serialized_data)
        assert deserialized.is_valid()
        assert deserialized.validated_data['status'] == 'active'

class TestAssessmentSerialization:
    """Test Assessment serialization with questions."""

    def test_assessment_round_trip(self):
        """
        Property 23: Assessment Round-Trip Serialization
        For any assessment with questions, serializing to JSON and deserializing
        should produce an equivalent Assessment object.

        Feature: blog-lms-wagtail-integration, Property 23: Assessment Round-Trip Serialization
        """
        assessment = Assessment.objects.create(
            lesson=self.lesson,
            title="Quiz 1",
            passing_score=70
        )

        serializer = AssessmentSerializer(assessment)
        serialized_data = serializer.data

        deserialized = AssessmentSerializer(data=serialized_data)
        assert deserialized.is_valid()
        assert deserialized.validated_data['passing_score'] == 70
```

### Serializer Implementation

```python
# serializers.py

from rest_framework import serializers
from blog_lms.models import BlogPost, Course, Module, Lesson, Enrollment, Assessment

class BlogPostSerializer(serializers.ModelSerializer):
    """Serialize BlogPost with all relationships."""
    author = serializers.StringRelatedField()
    categories = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'author', 'content',
            'meta_description', 'categories', 'tags',
            'publication_date', 'is_published', 'created_at', 'updated_at'
        ]

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'order', 'duration_minutes']

class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'lessons']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    instructor = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'instructor', 'description',
            'is_published', 'modules', 'created_at', 'updated_at'
        ]

class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    course = serializers.StringRelatedField()

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'status',
            'enrolled_at', 'completed_at'
        ]

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = [
            'id', 'title', 'description', 'passing_score',
            'time_limit_minutes', 'created_at'
        ]
```

## Implementation Notes

### Key Design Decisions

1. **Wagtail Page Inheritance**: Blog and LMS models inherit from Wagtail's Page model to leverage built-in versioning, publishing workflows, and admin interface.

2. **Separate Models for Relationships**: While BlogPost and Course are Wagtail pages, related models (Category, Tag, Comment, Module, Lesson, etc.) are standard Django models for flexibility and performance.

3. **Hierarchical Structure**: LMS uses a strict hierarchy (Course → Module → Lesson) to ensure clear organization and prevent circular dependencies.

4. **Unique Constraints**: Database-level unique constraints (e.g., Enrollment) prevent duplicate records and ensure data integrity.

5. **Async Certificate Generation**: Certificates are generated asynchronously to avoid blocking API responses during bulk operations.

6. **API-First Design**: All functionality is exposed through REST APIs, enabling integration with external systems and mobile applications.

### Performance Considerations

1. **Database Indexes**: Strategic indexes on frequently queried fields (author, publication_date, status, etc.) improve query performance.

2. **Select Related**: API views use `select_related()` and `prefetch_related()` to minimize database queries.

3. **Pagination**: All list endpoints implement pagination to handle large datasets efficiently.

4. **Caching**: Frequently accessed data (published posts, courses) can be cached using Redis.

5. **Async Tasks**: Long-running operations (certificate generation, email notifications) use Celery for asynchronous processing.

### Security Considerations

1. **Authentication**: All write operations require authentication via JWT tokens.

2. **Authorization**: Fine-grained permissions ensure users can only modify their own content.

3. **Input Validation**: All API inputs are validated using serializers to prevent injection attacks.

4. **CORS**: Cross-origin requests are restricted to trusted domains.

5. **Rate Limiting**: API endpoints implement rate limiting to prevent abuse.

### Scalability

1. **Stateless Design**: API services are stateless, enabling horizontal scaling.

2. **Database Connection Pooling**: Connection pooling optimizes database resource usage.

3. **Load Balancing**: Multiple API instances can be deployed behind a load balancer.

4. **Caching Layer**: Redis caching reduces database load for frequently accessed data.

## Related Documentation

- [System Architecture Overview](../../docs/architecture/01-system-architecture-overview.md)
- [Database Schema Design](../../docs/architecture/03-database-schema-design.md)
- [Django Volt Migration Guide](../../docs/architecture/02-django-volt-migration-guide.md)

## Appendix: Technology Stack

### Core Technologies

- **Django 4.2+**: Web framework
- **Wagtail 5.0+**: CMS platform
- **Django REST Framework**: API framework
- **PostgreSQL 12+**: Database
- **Redis**: Caching and task queue
- **Celery**: Async task processing

### Testing Libraries

- **Hypothesis**: Property-based testing
- **pytest**: Test framework
- **pytest-django**: Django integration
- **factory-boy**: Test data generation

### Documentation Tools

- **Sphinx**: Documentation generation
- **Markdown**: Documentation format
- **Mermaid**: Diagram generation

## Design Review Checklist

- [x] All requirements addressed in design
- [x] Data models properly normalized
- [x] API endpoints RESTful and consistent
- [x] Error handling comprehensive
- [x] Security considerations included
- [x] Performance optimizations identified
- [x] Testing strategy defined
- [x] Documentation structure planned
- [x] Correctness properties formalized
- [x] Installation procedures documented

