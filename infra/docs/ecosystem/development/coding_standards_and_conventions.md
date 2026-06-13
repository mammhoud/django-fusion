# Code Standards and Conventions

## Overview

This document describes the code standards and conventions for the Xellent Website platform.

## Python Code Style

### PEP 8 Compliance

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Imports**: Organized with isort

### Code Formatting

We use **Black** for automatic code formatting:

```bash
# Format all Python files
black .

# Format specific file
black path/to/file.py
```

### Example

```python
"""Module docstring describing the module."""

import os
from typing import List, Optional

from django.db import models
from django.contrib.auth.models import User

from apps.courses.models import Course


class StudentProgress(models.Model):
    """Track student progress in courses."""

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    progress_percentage = models.IntegerField(default=0)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self) -> str:
        return f"{self.student.username} - {self.course.title}"
```

## Import Organization

Use **isort** to organize imports:

```bash
# Sort imports in all files
isort .

# Sort specific file
isort path/to/file.py
```

### Import Order

1. Standard library imports
2. Third-party imports
3. Django imports
4. Local imports

```python
# Standard library
import os
import sys
from typing import List

# Third-party
import requests
from celery import shared_task

# Django
from django.db import models
from django.contrib.auth.models import User

# Local
from apps.courses.models import Course
from utils.helpers import calculate_score
```

## Naming Conventions

### Variables and Functions

```python
# Good
user_count = 10
def calculate_total_score():
    pass

# Bad
uc = 10
def calc_score():
    pass
```

### Classes

```python
# Good
class StudentEnrollment:
    pass

class CourseProgressTracker:
    pass

# Bad
class student_enrollment:
    pass

class course_progress_tracker:
    pass
```

### Constants

```python
# Good
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
API_BASE_URL = "https://api.example.com"

# Bad
max_retries = 3
default_timeout = 30
api_base_url = "https://api.example.com"
```

### Private Methods/Variables

```python
class User:
    def __init__(self):
        self._private_var = None

    def _private_method(self):
        pass
```

## Type Hints

Always use type hints:

```python
from typing import List, Optional, Dict

def get_user_courses(user_id: int) -> List[str]:
    """Get list of course titles for a user."""
    pass

def find_user(email: str) -> Optional[User]:
    """Find user by email, return None if not found."""
    pass

def get_user_stats(user_id: int) -> Dict[str, int]:
    """Get user statistics."""
    pass
```

## Docstrings

Use Google-style docstrings:

```python
def calculate_grade(score: int, total: int) -> str:
    """
    Calculate letter grade from score.

    Args:
        score: Student's score
        total: Total possible points

    Returns:
        Letter grade (A, B, C, D, F)

    Raises:
        ValueError: If score > total
    """
    if score > total:
        raise ValueError("Score cannot exceed total")

    percentage = (score / total) * 100
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    # ... etc
```

## Django Models

### Model Definition

```python
from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    """Course model."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Courses"

    def __str__(self) -> str:
        return self.title

    def get_student_count(self) -> int:
        """Get number of enrolled students."""
        return self.enrollment_set.count()
```

### Model Methods

```python
class Course(models.Model):
    # ... fields ...

    def is_published(self) -> bool:
        """Check if course is published."""
        return self.status == "published"

    def get_completion_percentage(self, user: User) -> float:
        """Get course completion percentage for user."""
        # Implementation
        pass
```

## Django Views

### Class-Based Views

```python
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class CourseListView(LoginRequiredMixin, ListView):
    """List all courses."""

    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"
    paginate_by = 20

    def get_queryset(self):
        """Filter courses by user."""
        return Course.objects.filter(
            instructor=self.request.user
        ).order_by("-created_at")
```

### Function-Based Views

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def course_detail(request, course_id):
    """Display course details."""
    course = Course.objects.get(id=course_id)
    context = {"course": course}
    return render(request, "courses/course_detail.html", context)
```

## Django Serializers

```python
from rest_framework import serializers
from apps.courses.models import Course

class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""

    instructor_name = serializers.CharField(
        source="instructor.get_full_name",
        read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "instructor",
            "instructor_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
```

## Error Handling

### Exception Handling

```python
from django.core.exceptions import ValidationError

def enroll_student(user: User, course: Course) -> None:
    """Enroll student in course."""
    try:
        enrollment = Enrollment.objects.create(
            user=user,
            course=course
        )
    except IntegrityError:
        raise ValidationError("Student already enrolled")
    except Exception as e:
        logger.error(f"Enrollment error: {e}")
        raise
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def process_enrollment(user_id: int) -> None:
    """Process enrollment."""
    try:
        user = User.objects.get(id=user_id)
        logger.info(f"Processing enrollment for {user.username}")
        # ... process ...
    except User.DoesNotExist:
        logger.warning(f"User {user_id} not found")
    except Exception as e:
        logger.error(f"Enrollment processing failed: {e}", exc_info=True)
```

## JavaScript/TypeScript

### Code Style

```javascript
// Use const by default
const MAX_RETRIES = 3;

// Use let for variables that change
let count = 0;

// Use arrow functions
const calculateScore = (answers, correct) => {
  return answers.filter((a, i) => a === correct[i]).length;
};

// Use template literals
const message = `User ${name} enrolled in ${course}`;
```

### Naming Conventions

```javascript
// Good
const getUserCourses = () => {};
const MAX_ATTEMPTS = 5;
class StudentProgress {}

// Bad
const get_user_courses = () => {};
const max_attempts = 5;
class student_progress {}
```

## CSS/Tailwind

### Class Naming

```html
<!-- Use semantic class names -->
<div class="course-card">
  <h2 class="course-title">Course Title</h2>
  <p class="course-description">Description</p>
</div>

<!-- Use Tailwind utilities -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow">
  <h2 class="text-lg font-semibold">Title</h2>
  <button class="px-4 py-2 bg-blue-500 text-white rounded">Action</button>
</div>
```

## Comments

### When to Comment

```python
# Good - explains why, not what
# We use a custom cache key to avoid conflicts with other apps
cache_key = f"course_{course_id}_stats"

# Bad - explains what the code does
# Get the course ID
course_id = request.GET.get("course_id")
```

### Comment Style

```python
# Single line comment
x = 5

# Multi-line comment
# This is a longer explanation
# that spans multiple lines
y = 10
```

## Related Documentation

- [Development Workflow](01-development-workflow.md)
- [Testing Strategy](02-testing-strategy.md)
- [Local Development Setup](../getting-started/02-local-development-setup.md)
