"""Compatibility shim."""
try:
    from ceptor_ai.content.models.users.team import Team  # noqa: F401
except ImportError:
    Team = None  # type: ignore[assignment,misc]
