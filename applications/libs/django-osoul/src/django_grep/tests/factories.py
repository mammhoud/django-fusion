"""
Test data factories for django-grep.

Integrates with nawaai for fake data generation when available.
"""
from typing import Any, Dict, List, Optional, Type

from django.db import models


class ModelFactory:
    """Test data factory for Django models.

    Inspects a model's field definitions and generates sensible fake values
    for required fields. Uses ``Faker`` when installed; falls back to bare
    defaults otherwise.

    Example::

        user = ModelFactory.create(User, username="alice")
        users = ModelFactory.create_batch(User, 5)
        draft = ModelFactory.build(Article)  # unsaved instance
    """

    @classmethod
    def _get_faker(cls) -> Optional[Any]:
        """Return a ``Faker`` instance, or ``None`` if Faker is not installed.

        Returns:
            A ``Faker()`` instance when the ``faker`` package is available,
            otherwise ``None``.
        """
        try:
            from faker import Faker
            return Faker()
        except ImportError:
            return None

    @classmethod
    def _build_defaults(cls, model: Type[models.Model], faker=None) -> Dict[str, Any]:
        """Build a dict of default field values for *model*.

        Iterates over the model's concrete, non-relation fields and generates
        a fake value for each required field (i.e. fields that have no
        ``default`` and are not ``blank``/``null``).

        Args:
            model: The Django model class to inspect.
            faker: A ``Faker`` instance used to generate values.  When
                ``None`` an empty dict is returned.

        Returns:
            A mapping of ``{field_name: generated_value}`` suitable for
            passing to ``model.objects.create(**defaults)``.
        """
        defaults: Dict[str, Any] = {}
        if faker is None:
            return defaults

        for field in model._meta.get_fields():
            if not hasattr(field, "column"):
                continue
            if field.primary_key or field.is_relation:
                continue
            if not field.blank and not field.null and field.default is models.fields.NOT_PROVIDED:
                field_type = field.get_internal_type()
                if field_type in ("CharField", "TextField"):
                    max_len = getattr(field, "max_length", 100) or 100
                    defaults[field.name] = faker.text(max_nb_chars=min(max_len, 50))
                elif field_type in ("IntegerField", "PositiveIntegerField", "SmallIntegerField"):
                    defaults[field.name] = faker.random_int(min=1, max=100)
                elif field_type == "BooleanField":
                    defaults[field.name] = False
                elif field_type == "EmailField":
                    defaults[field.name] = faker.email()
                elif field_type in ("DateField", "DateTimeField"):
                    defaults[field.name] = faker.date_time()
                elif field_type == "DecimalField":
                    defaults[field.name] = faker.pydecimal(left_digits=4, right_digits=2, positive=True)
                elif field_type == "FloatField":
                    defaults[field.name] = faker.pyfloat(positive=True)
                elif field_type == "URLField":
                    defaults[field.name] = faker.url()
                elif field_type == "SlugField":
                    defaults[field.name] = faker.slug()
                elif field_type == "UUIDField":
                    import uuid
                    defaults[field.name] = uuid.uuid4()

        return defaults

    @classmethod
    def create(cls, model: Type[models.Model], **kwargs) -> models.Model:
        """Create and persist a model instance populated with fake data.

        Args:
            model: The Django model class to instantiate.
            **kwargs: Field overrides applied on top of the generated defaults.

        Returns:
            A saved model instance.

        Example::

            article = ModelFactory.create(Article, title="Custom Title")
        """
        faker = cls._get_faker()
        defaults = cls._build_defaults(model, faker)
        defaults.update(kwargs)
        return model.objects.create(**defaults)

    @classmethod
    def create_batch(cls, model: Type[models.Model], count: int, **kwargs) -> List[models.Model]:
        """Create and persist *count* model instances.

        Args:
            model: The Django model class to instantiate.
            count: Number of instances to create.
            **kwargs: Field overrides applied to every instance.

        Returns:
            A list of saved model instances.

        Example::

            articles = ModelFactory.create_batch(Article, 5)
        """
        return [cls.create(model, **kwargs) for _ in range(count)]

    @classmethod
    def build(cls, model: Type[models.Model], **kwargs) -> models.Model:
        """Build an unsaved model instance populated with fake data.

        Useful when you need an object for unit testing without hitting
        the database.

        Args:
            model: The Django model class to instantiate.
            **kwargs: Field overrides applied on top of the generated defaults.

        Returns:
            An unsaved model instance.

        Example::

            draft = ModelFactory.build(Article)
            assert draft.pk is None
        """
        faker = cls._get_faker()
        defaults = cls._build_defaults(model, faker)
        defaults.update(kwargs)
        return model(**defaults)
