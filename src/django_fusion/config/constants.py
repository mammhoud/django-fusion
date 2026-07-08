"""
Global constants for Django Forge.

Provides shared constants used across the application.
"""

# Timeout constants (in seconds)
DEFAULT_TIMEOUT = 30
SHORT_TIMEOUT = 5
LONG_TIMEOUT = 300

# Pagination constants
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MIN_PAGE_SIZE = 1

# Cache constants (in seconds)
CACHE_TIMEOUT_SHORT = 60
CACHE_TIMEOUT_MEDIUM = 300
CACHE_TIMEOUT_LONG = 3600

# Retry constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0
DEFAULT_RETRY_BACKOFF = 2.0

# String length limits
MAX_SLUG_LENGTH = 50
MAX_TITLE_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 1000
MAX_EMAIL_LENGTH = 254

# Status choices
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_PENDING = "pending"
STATUS_ARCHIVED = "archived"

STATUS_CHOICES = [
    (STATUS_ACTIVE, "Active"),
    (STATUS_INACTIVE, "Inactive"),
    (STATUS_PENDING, "Pending"),
    (STATUS_ARCHIVED, "Archived"),
]

# Role choices
ROLE_ADMIN = "admin"
ROLE_MODERATOR = "moderator"
ROLE_USER = "user"
ROLE_GUEST = "guest"

ROLE_CHOICES = [
    (ROLE_ADMIN, "Administrator"),
    (ROLE_MODERATOR, "Moderator"),
    (ROLE_USER, "User"),
    (ROLE_GUEST, "Guest"),
]

# Permission constants
PERMISSION_READ = "read"
PERMISSION_WRITE = "write"
PERMISSION_DELETE = "delete"
PERMISSION_ADMIN = "admin"

# Date format constants
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

# HTTP status codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500
