from datetime import datetime

from ninja import Schema

from .base import BaseSchema
from .references import _CourseReference, _ModuleReference, _UserReference


class ModuleSchema(BaseSchema):
    """Schema for a module"""

    title: str  # Title of the module
    description: str | None  # Description of the module (optional)
    order: int  # Order of the module
    course: _CourseReference  # Reference to the course the module belongs to


class VideoSchema(BaseSchema):
    """Schema for a video"""

    title: str  # Title of the video
    description: str | None  # Description of the video (optional)
    video_url: str  # URL of the video
    duration: int  # Duration of the video in seconds
    thumbnail: str | None  # Thumbnail image URL (optional)
    is_preview: bool  # Whether the video is a preview
    order: int  # Order of the video
    module: _ModuleReference  # Reference to the module the video belongs to


class DocumentSchema(BaseSchema):
    """Schema for a document"""

    title: str  # Title of the document
    description: str | None  # Description of the document (optional)
    file: str  # File path or URL
    file_type: str  # Type of the file
    file_size: int  # Size of the file in bytes
    language: str  # Language of the document
    version: str | None  # Version of the document (optional)
    is_downloadable: bool  # Whether the document is downloadable
    order: int  # Order of the document
    module: _ModuleReference  # Reference to the module the document belongs to


class DocumentVersionSchema(BaseSchema):
    """Schema for a document version"""

    document: _ModuleReference  # Reference to the document
    file: str  # File path or URL
    version_number: str  # Version number
    changelog: str | None  # Changelog (optional)
    created_by: _UserReference  # Reference to the user who created the version


class AssignmentSchema(BaseSchema):
    """Schema for an assignment"""

    title: str  # Title of the assignment
    description: str | None  # Description of the assignment (optional)
    instructions: str  # Instructions for the assignment
    due_date: datetime  # Due date of the assignment
    max_score: int  # Maximum score for the assignment
    order: int  # Order of the assignment
    module: _ModuleReference  # Reference to the module the assignment belongs to


class PatchModuleSchema(Schema):
    """Patch schema for a module with all fields optional"""

    title: str | None  # Title of the module (optional)
    description: str | None  # Description of the module (optional)
    order: int | None  # Order of the module (optional)
    course: int | None  # Course ID (optional)


class PatchVideoSchema(Schema):
    """Patch schema for a video with all fields optional"""

    title: str | None  # Title of the video (optional)
    description: str | None  # Description of the video (optional)
    video_url: str | None  # URL of the video (optional)
    duration: int | None  # Duration of the video in seconds (optional)
    thumbnail: str | None  # Thumbnail image URL (optional)
    is_preview: bool | None  # Whether the video is a preview (optional)
    order: int | None  # Order of the video (optional)
    module: int | None  # Module ID (optional)


class PatchDocumentSchema(Schema):
    """Patch schema for a document with all fields optional"""

    title: str | None  # Title of the document (optional)
    description: str | None  # Description of the document (optional)
    file: str | None  # File path or URL (optional)
    file_type: str | None  # Type of the file (optional)
    file_size: int | None  # Size of the file in bytes (optional)
    language: str | None  # Language of the document (optional)
    version: str | None  # Version of the document (optional)
    is_downloadable: bool | None  # Whether the document is downloadable (optional)
    order: int | None  # Order of the document (optional)
    module: int | None  # Module ID (optional)


class PatchDocumentVersionSchema(Schema):
    """Patch schema for a document version with all fields optional"""

    document: int | None  # Document ID (optional)
    file: str | None  # File path or URL (optional)
    version_number: str | None  # Version number (optional)
    changelog: str | None  # Changelog (optional)
    created_by: int | None  # User ID of the creator (optional)


class PatchAssignmentSchema(Schema):
    """Patch schema for an assignment with all fields optional"""

    title: str | None  # Title of the assignment (optional)
    description: str | None  # Description of the assignment (optional)
    instructions: str | None  # Instructions for the assignment (optional)
    due_date: datetime | None  # Due date of the assignment (optional)
    max_score: int | None  # Maximum score for the assignment (optional)
    order: int | None  # Order of the assignment (optional)
    module: int | None  # Module ID (optional)


class ModuleFilterSchema(Schema):
    """Filter schema for modules"""

    course_id: int | None  # Course ID (optional)
    order: int | None  # Order of the module (optional)


class VideoFilterSchema(Schema):
    """Filter schema for videos"""

    module_id: int | None  # Module ID (optional)
    is_preview: bool | None  # Whether the video is a preview (optional)


class DocumentFilterSchema(Schema):
    """Filter schema for documents"""

    module_id: int | None  # Module ID (optional)
    file_type: str | None  # Type of the file (optional)


class AssignmentFilterSchema(Schema):
    """Filter schema for assignments"""

    module_id: int | None  # Module ID (optional)
    due_date: datetime | None  # Due date of the assignment (optional)
