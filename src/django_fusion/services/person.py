"""
PersonServiceBase: Base class for person service implementations.

Canonical import: from django_fusion.services.person import PersonServiceBase
"""


class PersonServiceBase:
    """Base class for person service implementations."""

    person_model = None  # Injected by subclass

    @classmethod
    def create_person(cls, **kwargs):
        """Create a new person."""
        if cls.person_model is None:
            raise NotImplementedError("person_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def update_person(cls, person, **kwargs):
        """Update person details."""
        if cls.person_model is None:
            raise NotImplementedError("person_model must be set by subclass")
        raise NotImplementedError

    @classmethod
    def get_person(cls, **kwargs):
        """Get person by criteria."""
        if cls.person_model is None:
            raise NotImplementedError("person_model must be set by subclass")
        raise NotImplementedError
