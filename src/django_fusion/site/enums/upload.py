from enum import Enum


class FileUploadStrategy(Enum):
    STANDARD = "standard"
    CLOUD_STORAGE = "direct"


class FileUploadStorage(Enum):
    LOCAL = "local"
    S3 = "s3"
