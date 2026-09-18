"""Loop-CRM role-based access control.

Mirrors the Twenty/Postiz role matrix in pure-Django permission helpers (DRF
permission classes are added in the API phase per the plan). Roles live on
``core.UserProfile`` attached to the standard ``auth.User``.
"""
from __future__ import annotations

SALES_ROLES = {"super_admin", "sales_manager", "sales_rep"}
MARKETING_ROLES = {"super_admin", "marketing_manager", "marketing_specialist"}
REVOPS_ROLES = {"super_admin", "revops_manager"}


def role_of(user) -> str:
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", "") if profile else ""


def is_sales(user) -> bool:
    return bool(user and user.is_authenticated and role_of(user) in SALES_ROLES)


def is_marketing(user) -> bool:
    return bool(user and user.is_authenticated and role_of(user) in MARKETING_ROLES)


def is_revops(user) -> bool:
    return bool(user and user.is_authenticated and role_of(user) in REVOPS_ROLES)


def can_manage_deals(user) -> bool:
    return bool(user and user.is_authenticated and role_of(user) in {"super_admin", "sales_manager", "revops_manager"})


def can_manage_posts(user) -> bool:
    return bool(user and user.is_authenticated and role_of(user) in {"super_admin", "marketing_manager", "revops_manager"})
