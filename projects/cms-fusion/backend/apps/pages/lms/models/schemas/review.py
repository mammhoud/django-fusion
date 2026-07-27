from .base import BaseSchema
from .references import _CourseReference, _UserReference


class ReviewSchema(BaseSchema):
    """Schema for a course review"""

    course: _CourseReference  # Reference to the course being reviewed
    user: _UserReference  # Reference to the user who wrote the review
    rating: int  # Rating given by the user
    comment: str  # Comment provided by the user
