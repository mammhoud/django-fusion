"""django_rseal.pipelines.services — compatibility shim."""
from django_rseal.services.infrastructure.base import BaseService  # noqa: F401
from django_rseal.services.infrastructure.token import TokenService  # noqa: F401

try:
    from django_rseal.services.content.form_submission import FormSubmissionService  # noqa: F401
except ImportError:
    FormSubmissionService = None  # type: ignore[assignment,misc]


class CRUDService(BaseService):
    """Compatibility stub for CRUDService."""
    pass


class PersonServiceBase(BaseService):
    """Compatibility stub for PersonServiceBase."""
    pass
