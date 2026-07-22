"""
Shared API utilities — legacy helpers retained for backward compatibility.

Most functionality has been replaced by ``www.api.data.helpers`` and
``www.api.data_adapter``. This module re-exports for convenience.
"""

from www.api.data_adapter import (
    paginate_queryset,
    parse_body,
    get_current_user,
    get_image_url,
    get_user_display_name,
)
from www.auth import authenticate_request, extract_bearer_token
