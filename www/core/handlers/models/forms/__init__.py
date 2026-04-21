try:
    from django_rseal.handlers.models.forms.submission import FormSubmission
except ImportError:
    # FormSubmission was moved to django_rseal package (see migration 0003).
    # When django_rseal is not installed, provide a placeholder.
    FormSubmission = None  # type: ignore[assignment,misc]

__all__ = ["FormSubmission"]
