"""Backward-compatibility re-exports for django_fusion.site.schemas.users.user.

The implementation moved to ``django_fusion.ci.schemas.users.user``.
"""
from django_fusion.ci.schemas.users.user import (  # noqa: F401
    GroupSchema,
    TokenBaseSchema,
    UserBaseSchema,
    UserCreateSchema,
    UserDetailSchema,
    UserProfileUpdateSchema,
    UserUpdateSchema,
)

# Historical alias used by external callers.
UserSchema = UserDetailSchema

__all__ = [
    "GroupSchema",
    "TokenBaseSchema",
    "UserBaseSchema",
    "UserCreateSchema",
    "UserDetailSchema",
    "UserProfileUpdateSchema",
    "UserSchema",
    "UserUpdateSchema",
]
