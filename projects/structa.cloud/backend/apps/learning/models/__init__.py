"""
Learning/LMS models — package layout mirroring Precis ``apps/learning``.

The flat ``models.py`` was split into this package so both learning apps share
the same structure:

* ``courses/`` — Course, Module, Lesson, progress, tags, specializations
* ``enrollment.py``, ``certificate.py``, ``review.py``, ``wishlist.py``

This module re-exports every public model so the old flat import
(``from apps.learning.models import Course``) keeps resolving unchanged.
"""
from .certificate import Certificate
from .courses import (
    Course,
    CourseEnrollmentLead,
    CourseSnippetViewSet,
    CourseTag,
    CourseTranslation,
    Lesson,
    LessonProgress,
    LessonResource,
    Module,
    ModuleProgress,
    Specialization,
)
from .enrollment import Enrollment
from .review import Review
from .wishlist import Wishlist

__all__ = [
    "Course",
    "CourseEnrollmentLead",
    "CourseSnippetViewSet",
    "CourseTranslation",
    "CourseTag",
    "Lesson",
    "LessonProgress",
    "LessonResource",
    "Module",
    "ModuleProgress",
    "Specialization",
    "Enrollment",
    "Certificate",
    "Review",
    "Wishlist",
]
