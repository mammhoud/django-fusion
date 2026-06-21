"""
Shared enumerations for django_osoul.

This module provides shared enum types used across django_osoul modules
for consistent type definitions and value constraints.

Classes:
    Direction: Direction enumeration (ascending/descending).
    Environment: Application environment enumeration.
    LogLevel: Logging level enumeration.
    Module: Application module enumeration.
    Runtime: Runtime environment enumeration.
    Workflow: Workflow type enumeration.
    FileUploadStorage: File storage backend enumeration.
    FileUploadStrategy: File upload strategy enumeration.

Usage::

    from django_osoul.contrib.enums import Environment, LogLevel
"""

from django_osoul.site.enums.env import Direction, Environment, LogLevel, Module, Runtime, Workflow
from django_osoul.site.enums.upload import FileUploadStorage, FileUploadStrategy

__all__ = [
    "Direction",
    "Environment",
    "FileUploadStorage",
    "FileUploadStrategy",
    "LogLevel",
    "Module",
    "Runtime",
    "Workflow",
]
