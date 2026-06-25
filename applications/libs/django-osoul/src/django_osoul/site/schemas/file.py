from ninja import ModelSchema, Schema

from ..file import File


class FileOut(ModelSchema):
    class Config:
        model = File
        model_fields = [
            "id",
            "file_name",
            "file_type",
            "original_file_name",
            "uploaded_at",
            "description",
            "url",
            "is_valid",
        ]


class FileCreate(Schema):
    description: str | None
    content_type_id: int


class FileUpdate(Schema):
    description: str | None
    file_name: str | None


class FileStats(Schema):
    total_files: int
    valid_files: int
    pending_files: int
    total_size: float  # in MB
    file_types_distribution: dict
