"""Backward-compatible registration view helpers.

Only lightweight helper functions are re-exported here so legacy imports do
not need to load the full site view package and its Wagtail model graph.
"""

import json
import logging

from django.core.cache import cache
from django.http import HttpResponse
from django.contrib.auth.models import Group
from django.utils import timezone

logger = logging.getLogger("apps.registration")
RATE_LIMIT_WINDOW = 3600
RATE_LIMIT_MAX_ATTEMPTS = 5


def get_client_ip(request) -> str:
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limit_check(request) -> bool:
    ip = get_client_ip(request)
    cache_key = f"reg_rate_limit:{ip}"
    try:
        attempts = cache.get(cache_key, 0)
    except Exception as exc:
        logger.warning("Cache failure in rate_limit_check for IP %s: %s — failing open", ip, exc)
        return True
    return attempts < RATE_LIMIT_MAX_ATTEMPTS


def rate_limit_increment(request):
    ip = get_client_ip(request)
    cache_key = f"reg_rate_limit:{ip}"
    try:
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, RATE_LIMIT_WINDOW)
    except Exception as exc:
        logger.warning("Cache failure in rate_limit_increment for IP %s: %s — counter not updated", ip, exc)


def trigger_notification(response: HttpResponse, message: str, notification_type: str = "success") -> HttpResponse:
    response["HX-Trigger"] = json.dumps({
        "showNotification": {
            "message": message,
            "type": notification_type,
        }
    })
    return response


def ensure_groups_exist():
    """Ensure registration roles required by the account flow exist."""
    for group_name in ["Instructor", "Content Manager"]:
        _group, created = Group.objects.get_or_create(name=group_name)
        if created:
            logger.info("Created group: %s at %s", group_name, timezone.now().isoformat())


def assign_default_group(user):
    """Assign the default Content Manager group to a registered user."""
    group, _ = Group.objects.get_or_create(name="Content Manager")
    user.groups.add(group)
    logger.info("Assigned user %s to group '%s'", getattr(user, "email", user), group.name)


def _ensure_profile_exists(user):
    try:
        from crafts_ai.models import Person

        Person.objects.get_or_create(
            user=user,
            defaults={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "full_name": user.get_full_name(),
                "status": "ACTIVE",
                "is_registered": True,
                "registration_date": timezone.now(),
            },
        )
    except Exception as exc:
        logger.warning("Could not create profile for %s: %s", getattr(user, "email", user), exc)


__all__ = [
    "RATE_LIMIT_MAX_ATTEMPTS",
    "RATE_LIMIT_WINDOW",
    "assign_default_group",
    "ensure_groups_exist",
    "get_client_ip",
    "rate_limit_check",
    "rate_limit_increment",
    "trigger_notification",
    "_ensure_profile_exists",
]
