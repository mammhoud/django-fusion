from datetime import datetime

from ninja import Schema


class BaseSchema(Schema):
    """Base schema with common fields"""

    id: int  # Unique identifier
    created_at: datetime  # Timestamp when the record was created
    updated_at: datetime  # Timestamp when the record was last updated
