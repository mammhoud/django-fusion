from ninja import Schema


class _UserReference(Schema):
    """Reference schema for User model"""

    id: int  # User ID
    username: str  # Username
    first_name: str | None  # First name (optional)
    last_name: str | None  # Last name (optional)


class _CourseReference(Schema):
    """Reference schema for Course model"""

    id: int  # Course ID
    title: str  # Course title
    slug: str  # Course slug


class _ModuleReference(Schema):
    """Reference schema for Module model"""

    id: int  # Module ID
    title: str  # Module title
    order: int  # Order of the module


class _DocumentReference(Schema):
    """Reference schema for Document model"""

    id: int  # Document ID
    title: str  # Document title
    file_type: str  # Type of the file


class _QuizReference(Schema):
    """Reference schema for Quiz model"""

    id: int  # Quiz ID
    title: str  # Quiz title
    passing_score: int  # Passing score for the quiz


class _CategoryReference(Schema):
    """Reference schema for Category model"""

    id: int  # Category ID
    name: str  # Category name
    slug: str  # Category slug
