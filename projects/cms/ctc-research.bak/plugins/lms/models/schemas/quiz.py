from .base import BaseSchema
from .references import _ModuleReference


class QuestionSchema(BaseSchema):
    """Schema for a quiz question"""

    question_type: str  # Type of the question
    question_text: str  # Text of the question
    points: int  # Points awarded for the question
    correct_answer: str  # Correct answer for the question
    explanation: str | None  # Explanation for the answer (optional)


class QuizSchema(BaseSchema):
    """Schema for a quiz"""

    title: str  # Title of the quiz
    description: str | None  # Description of the quiz (optional)
    time_limit: int | None  # Time limit for the quiz in minutes (optional)
    passing_score: int  # Passing score for the quiz
    max_attempts: int  # Maximum number of attempts allowed
    questions: list[QuestionSchema]  # List of questions in the quiz
    pipelines: _ModuleReference  # Reference to the module the quiz belongs to
