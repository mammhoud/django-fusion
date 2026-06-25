"""crafts_ai.pipelines.models.users — compatibility shim."""
from crafts_ai.content.models.users.users import Person  # noqa: F401

try:
    from crafts_ai.content.models.users.team import Team  # noqa: F401
except ImportError:
    Team = None  # type: ignore[assignment,misc]
