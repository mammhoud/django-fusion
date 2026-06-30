"""ceptor_ai.pipelines.services — compatibility shim."""
from ceptor_ai.services.infrastructure.base import BaseService  # noqa: F401
from ceptor_ai.services.infrastructure.token import TokenService  # noqa: F401

try:
    from ceptor_ai.services.content.form_submission import FormSubmissionService  # noqa: F401
except ImportError:
    FormSubmissionService = None  # type: ignore[assignment,misc]


class CRUDService(BaseService):
    """Compatibility stub for CRUDService."""
    pass


class PersonServiceBase(BaseService):
    """Compatibility stub for PersonServiceBase."""
    pass
