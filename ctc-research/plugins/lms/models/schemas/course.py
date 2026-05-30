from ninja import Schema

from .base import BaseSchema
from .references import _CategoryReference, _UserReference


class CourseTranslationSchema(Schema):
    """Schema for course translation"""

    language: str  # Language of the translation
    title: str  # Translated title
    description: str  # Translated description
    prerequisites: str | None  # Translated prerequisites (optional)
    learning_objectives: str | None  # Translated learning objectives (optional)


class CourseCreateSchema(Schema):
    """Schema for creating a course"""

    title: str  # Title of the course
    description: str  # Description of the course
    category_id: int | None  # ID of the category (optional)
    price: float = 0.0  # Price of the course
    prerequisites: str | None  # Prerequisites for the course (optional)
    learning_objectives: str | None  # Learning objectives of the course (optional)
    translations: list[CourseTranslationSchema] | None  # List of translations (optional)


class CourseUpdateSchema(CourseCreateSchema):
    """Schema for updating a course"""

    is_published: bool | None  # Whether the course is published (optional)


class CourseSchema(BaseSchema):
    """Schema for a course"""

    title: str  # Title of the course
    slug: str  # Slug of the course
    description: str  # Description of the course
    instructor: _UserReference  # Reference to the instructor
    category: _CategoryReference | None  # Reference to the category (optional)
    is_published: bool  # Whether the course is published
    price: float  # Price of the course
    prerequisites: str | None  # Prerequisites for the course (optional)
    learning_objectives: str | None  # Learning objectives of the course (optional)
    average_rating: float  # Average rating of the course
    translations: list[CourseTranslationSchema]  # List of translations
