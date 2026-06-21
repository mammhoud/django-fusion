"""django_rseal.pipelines.models.users — compatibility shim."""
from django_rseal.content.models.users.users import Person  # noqa: F401

try:
    from django_rseal.content.models.users.team import Team  # noqa: F401
except ImportError:
    Team = None  # type: ignore[assignment,misc]
