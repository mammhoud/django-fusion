from .base import BaseSchema
from .content import AssignmentSchema, DocumentSchema, ModuleSchema, VideoSchema
from .course import CourseCreateSchema, CourseSchema, CourseUpdateSchema
from .enrollment import EnrollmentSchema
from .quiz import QuestionSchema, QuizSchema
from .review import ReviewSchema

__all__ = [
    "AssignmentSchema",
    "BaseSchema",
    "CourseCreateSchema",
    "CourseSchema",
    "CourseUpdateSchema",
    "DocumentSchema",
    "EnrollmentSchema",
    "ModuleSchema",
    "QuestionSchema",
    "QuizSchema",
    "ReviewSchema",
    "VideoSchema",
]
