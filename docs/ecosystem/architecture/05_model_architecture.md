# Model Architecture

## Overview

This document describes the core models and their relationships in the project.

## Base Models

### BaseModel

**Location**: `django_osoul/models.py`

All models inherit from `BaseModel` which provides:

- `created_at` - Timestamp when record was created
- `updated_at` - Timestamp when record was last updated
- `uuid` - Universal unique identifier

```python
from django_osoul.models import BaseModel

class MyModel(BaseModel):
    name = models.CharField(max_length=100)
```

## User-Related Models

### Person

**Location**: `crafts_ai/pipelines/models/users/users.py`

Extended user profile with additional fields.

```python
from crafts_ai.pipelines.models import Person

class Person(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
```

### UserGroup

**Location**: `crafts_ai/pipelines/models/users/group.py`

User groups for organization.

```python
class UserGroup(BaseModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
```

### UserRole

**Location**: `crafts_ai/pipelines/models/users/role.py`

User roles with permissions.

```python
class UserRole(BaseModel):
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=list)
    color = models.CharField(max_length=7, default='#007bff')
```

## Course Models

### Course

**Location**: `apps.lms/models/courses/info.py`

```python
class Course(BaseModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
```

### Module

```python
class Module(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
```

### Lesson

```python
class Lesson(BaseModel):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = RichTextField()
    order = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True)
```

### Enrollment

```python
class Enrollment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
```

### Certificate

```python
class Certificate(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
```

## Blog Models

### BlogPost

**Location**: `apps.accounts/models/blog/post.py`

```python
class BlogPost(BaseModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField()
    content = RichTextField()
    author = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    featured_image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
```

### BlogTag

**Location**: `apps.accounts/models/blog/tags.py`

```python
class BlogTag(BaseModel):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
```

## Model Relationships

```
User 1:1 Person
Person 1:N Enrollment
Person 1:N Certificate
Person 1:N Note
Course 1:N Module
Course 1:N Enrollment
Course 1:N Certificate
Module 1:N Lesson
Lesson 1:N Progress
Enrollment 1:N Progress
UserGroup 1:N UserRole
UserRole N:N Permission (via JSONField)
```

## Model Mixins

### ModelCacheMixin

Provides caching functionality for models.

```python
from crafts_ai.pipelines.models import CachingStorage

class MyModel(BaseModel, CachingStorage):
    # Automatic cache invalidation on save/delete
```

### ContentBase

Base class for content models with publishing capabilities.

```python
from crafts_ai.pipelines.models import ContentBase

class MyContent(ContentBase):
    title = models.CharField(max_length=200)
```
