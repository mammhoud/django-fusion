"""Pydantic response schemas, serializers, and user data schemas.

Modules
-------
schemas.response        Generic API response envelope schema.
schemas.serializer      ModelSerializer-compatible Pydantic base class.
schemas.model_schema    Schema helpers for Django model field introspection.
schemas.message         Message and notification schemas.
schemas.notification    Push notification payload schema.
schemas.logging         Structured log entry schema.
schemas.file            File upload response schema.
schemas.users/          User-specific schemas: token, user details, utilities.

Usage::

    from django_fusion.routes.schemas.response import APIResponse
    from django_fusion.routes.schemas.users.user import UserSchema
"""
