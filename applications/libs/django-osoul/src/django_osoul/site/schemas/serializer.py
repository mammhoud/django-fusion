from django.db.models import Model


def serialize_instance(instance: Model, schema=None, serializer_class=None):
    """
    Serializes a Django model instance into a dictionary.

    Args:
        instance: The Django model instance.
        schema: A Ninja schema for serialization (optional).
        serializer_class: A DRF serializer class (optional).

    Returns:
        A dictionary representing the serialized data.  Returns None if input is invalid.
    """
    if not isinstance(instance, Model):
        return None  # Handle invalid input

    if schema:
        return schema.from_orm(instance).dict()
    elif serializer_class:
        serializer = serializer_class(instance)
        return serializer.data
    else:
        # Optimized fallback using dict comprehension
        return {
            field.name: getattr(instance, field.name) for field in instance._meta.fields
        }
