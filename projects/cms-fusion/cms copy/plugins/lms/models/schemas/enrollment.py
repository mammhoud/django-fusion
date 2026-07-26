from datetime import datetime

from .base import BaseSchema
from .references import _CourseReference, _UserReference


class EnrollmentSchema(BaseSchema):
    """Schema for course enrollment"""

    student: _UserReference  # Reference to the enrolled student
    course: _CourseReference  # Reference to the enrolled course
    is_active: bool  # Whether the enrollment is active
    completed_at: datetime | None  # Completion date (optional)
    progress: float  # Progress percentage
