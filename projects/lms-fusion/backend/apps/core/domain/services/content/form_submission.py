"""
FormSubmissionService: Base class for form submission service implementations.

Canonical import: from apps.core.domain.services.content.form_submission import FormSubmissionService
"""

class FormSubmissionService:
    """Base class for form submission service implementations."""

    form_submission_model = None  # Injected by subclass

    @classmethod
    def submit_form(cls, form_data: dict, **kwargs):
        """Submit a form."""
        if cls.form_submission_model is None:
            raise NotImplementedError("form_submission_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_submissions(cls, form_id, **kwargs):
        """Get form submissions."""
        if cls.form_submission_model is None:
            raise NotImplementedError("form_submission_model must be set by subclass")
        raise NotImplementedError
