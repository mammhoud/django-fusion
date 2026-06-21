"""Compatibility shim."""
try:
    from django_rseal.content.models.users.team import Team  # noqa: F401
except ImportError:
    Team = None  # type: ignore[assignment,misc]
