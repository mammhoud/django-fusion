# ctc-research.com Pydoc Reference

## Overview

This document provides pydoc-style documentation for the ctc-research.com (CTC Research LMS Platform) project. It covers all major modules, classes, and functions.

## Project Structure

```
ctc-research.com/
├── apps/                    # Thin layer apps
│   ├── accounts/            # User management
│   ├── lms/                 # Learning management
│   ├── content/             # CMS content
│   └── blog/                # Blog functionality
├── core/                    # ASGI/WSGI entry points
├── configs/                 # Settings and URL configuration
├── assets/                  # Static files, media, templates
├── components/              # Reusable HTML components
├── email_templates/         # Email HTML templates
├── locale/                  # Translation files
└── tests/                   # Test suite
```

## Apps Module

### apps.accounts

User authentication, registration, profiles, and permissions.

#### Models

```python
class User(django_osoul.models.AbstractUser):
    """
    Custom user model for ctc-research.com.

    Extends django_osoul.models.AbstractUser with project-specific fields.

    Attributes:
        phone (str): User phone number
        bio (str): User biography
        avatar (ImageField): User profile picture
        preferences (JSONField): User preferences

    Example:
        >>> user = User.objects.create_user(
        ...     username='john',
        ...     email='john@example.com',
        ...     password='secure_password'
        ... )
    """
    pass

class Group(django_osoul.models.Group):
    """
    Custom group model for ctc-research.com.

    Extends django_osoul.models.Group with project-specific fields.

    Attributes:
        description (str): Group description
        is_active (bool): Group active status

    Example:
        >>> group = Group.objects.create(name='Instructors')
    """
    pass
```

#### Services

```python
class UserService(crafts_ai.pipelines.services.UserServiceBase):
    """
    CTC Research user service.

    Delegates to crafts_ai.pipelines.services.UserServiceBase.

    Methods:
        create_user(username, email, password, **kwargs): Create new user
        update_user(user, **kwargs): Update user profile
        delete_user(user): Delete user account
        get_user_by_id(user_id): Get user by ID
        get_user_by_email(email): Get user by email

    Example:
        >>> from apps.accounts.services import UserService
        >>> user = UserService.create_user('john', 'john@example.com', 'password')
    """
    pass

class GroupService(crafts_ai.pipelines.services.GroupServiceBase):
    """
    CTC Research group service.

    Delegates to crafts_ai.pipelines.services.GroupServiceBase.

    Methods:
        create_group(name, **kwargs): Create new group
        add_user_to_group(user, group): Add user to group
        remove_user_from_group(user, group): Remove user from group
        get_group_members(group): Get all group members

    Example:
        >>> from apps.accounts.services import GroupService
        >>> GroupService.add_user_to_group(user, group)
    """
    pass
```

### apps.lms

Learning management system with courses, lessons, enrollments, and progress tracking.

#### Models

```python
class Course(crafts_ai.models.BasePage):
    """
    Course model for CTC Research LMS.

    Extends crafts_ai.models.BasePage with course-specific fields.

    Attributes:
        title (str): Course title
        description (str): Course description
        instructor (ForeignKey): Course instructor
        price (DecimalField): Course price
        duration (int): Course duration in hours
        is_published (bool): Course publication status

    Example:
        >>> course = Course.objects.create(
        ...     title='Python Basics',
        ...     description='Learn Python from scratch',
        ...     instructor=instructor_user
        ... )
    """
    pass

class Lesson(crafts_ai.models.BasePage):
    """
    Lesson model for CTC Research LMS.

    Attributes:
        title (str): Lesson title
        content (StreamField): Lesson content
        course (ForeignKey): Parent course
        order (int): Lesson order in course
        duration (int): Lesson duration in minutes

    Example:
        >>> lesson = Lesson.objects.create(
        ...     title='Introduction to Python',
        ...     course=course,
        ...     order=1
        ... )
    """
    pass

class Enrollment(django_osoul.models.TimestampedModel):
    """
    Enrollment model for CTC Research LMS.

    Attributes:
        user (ForeignKey): Enrolled user
        course (ForeignKey): Enrolled course
        enrolled_at (datetime): Enrollment timestamp
        completed_at (datetime): Completion timestamp
        progress (int): Progress percentage (0-100)

    Example:
        >>> enrollment = Enrollment.objects.create(
        ...     user=user,
        ...     course=course
        ... )
    """
    pass

class Cart(django_osoul.models.TimestampedModel):
    """
    Shopping cart model for CTC Research LMS.

    Attributes:
        user (ForeignKey): Cart owner
        items (ManyToManyField): Cart items
        total (DecimalField): Cart total
        created_at (datetime): Cart creation timestamp

    Example:
        >>> cart = Cart.objects.create(user=user)
        >>> cart.items.add(course)
    """
    pass
```

#### Services

```python
class CartService(crafts_ai.pipelines.services.CartServiceBase):
    """
    CTC Research cart service.

    Delegates to crafts_ai.pipelines.services.CartServiceBase.

    Methods:
        add_to_cart(user, item, quantity): Add item to cart
        remove_from_cart(user, item): Remove item from cart
        get_cart_total(user): Get cart total
        checkout(user): Process checkout

    Example:
        >>> from apps.lms.services import CartService
        >>> CartService.add_to_cart(user, course, 1)
    """
    pass

class EnrollmentService(crafts_ai.pipelines.services.EnrollmentServiceBase):
    """
    CTC Research enrollment service.

    Methods:
        enroll_user(user, course): Enroll user in course
        update_progress(enrollment, progress): Update enrollment progress
        complete_enrollment(enrollment): Mark enrollment as complete
        generate_certificate(enrollment): Generate completion certificate

    Example:
        >>> from apps.lms.services import EnrollmentService
        >>> EnrollmentService.enroll_user(user, course)
    """
    pass
```

### apps.content

CMS content management with Wagtail pages.

#### Models

```python
class HomePage(crafts_ai.models.BasePage):
    """
    Home page model for ctc-research.com.

    Attributes:
        hero_title (str): Hero section title
        hero_subtitle (str): Hero section subtitle
        featured_courses (ManyToManyField): Featured courses
        testimonials (StreamField): Testimonials

    Example:
        >>> home = HomePage.objects.first()
    """
    pass

class ContentPage(crafts_ai.models.BasePage):
    """
    Generic content page model.

    Attributes:
        body (StreamField): Page content
        sidebar (StreamField): Sidebar content

    Example:
        >>> page = ContentPage.objects.create(
        ...     title='About Us',
        ...     body=streamfield_content
        ... )
    """
    pass
```

### apps.blog

Blog functionality with posts, tags, and categories.

#### Models

```python
class BlogPost(crafts_ai.models.BasePage):
    """
    Blog post model for ctc-research.com.

    Attributes:
        title (str): Post title
        body (StreamField): Post content
        author (ForeignKey): Post author
        tags (ManyToManyField): Post tags
        published_at (datetime): Publication timestamp
        is_featured (bool): Featured post status

    Example:
        >>> post = BlogPost.objects.create(
        ...     title='New Feature Announcement',
        ...     author=user,
        ...     body=streamfield_content
        ... )
    """
    pass

class Tag(django_osoul.models.NamedModel):
    """
    Tag model for blog posts.

    Attributes:
        name (str): Tag name
        slug (str): Tag slug

    Example:
        >>> tag = Tag.objects.create(name='Python')
    """
    pass
```

## Configuration Module

### configs.settings

Django settings configuration.

```python
# configs/settings/base.py
"""
Base Django settings for ctc-research.com.

Contains all common settings shared across environments.

Settings:
    DEBUG: Debug mode (default: False)
    ALLOWED_HOSTS: Allowed host names
    INSTALLED_APPS: Installed Django apps
    MIDDLEWARE: Django middleware classes
    DATABASES: Database configuration
    CACHES: Cache configuration
    EMAIL_BACKEND: Email backend configuration
"""

# configs/settings/local.py
"""
Local development settings.

Extends base settings with development-specific configuration.

Additional Settings:
    DEBUG: True
    EMAIL_BACKEND: 'django.core.mail.backends.console.EmailBackend'
    CACHES: LocMemCache
"""

# configs/settings/production.py
"""
Production settings.

Extends base settings with production-specific configuration.

Additional Settings:
    DEBUG: False
    SECURE_SSL_REDIRECT: True
    SECURE_HSTS_SECONDS: 31536000
    SECURE_CONTENT_TYPE_NOSNIFF: True
"""
```

## Health Check Module

### Health Endpoints

```python
# Health check endpoints provided by django_osoul

def health_check(request):
    """
    Basic health check endpoint.

    Returns:
        JsonResponse: {"status": "ok"}

    URL: /health/
    """

def health_database(request):
    """
    Database connectivity health check.

    Returns:
        JsonResponse: {"status": "ok", "database": "connected"}

    URL: /health/database/
    """

def health_assets(request):
    """
    Static files health check.

    Returns:
        JsonResponse: {"status": "ok", "assets": "accessible"}

    URL: /health/assets/
    """

def health_media(request):
    """
    Media files health check.

    Returns:
        JsonResponse: {"status": "ok", "media": "accessible"}

    URL: /health/media/
    """
```

## Testing Module

### Test Infrastructure

```python
# tests/base.py
from django_osoul.tests.base import BaseTestCase

class CTCTestCase(BaseTestCase):
    """
    Base test case for ctc-research.com tests.

    Extends django_osoul.tests.base.BaseTestCase with
    project-specific test utilities.

    Features:
        - Hypothesis property-based testing
        - Factory Boy test fixtures
        - Selenium browser testing
        - API testing utilities

    Example:
        >>> class MyTest(CTCTestCase):
        ...     def test_something(self):
        ...         self.assertTrue(True)
    """
    pass
```

## Related Documentation

- [Getting Started with ctc-research.com](../getting-started/ctc_research_getting_started.md)
- [Architecture Overview](../architecture/README.md)
- [API Reference](../api/README.md)
- [Deployment Guide](../deployment/README.md)

---

**Last Updated**: 2026-04-17
