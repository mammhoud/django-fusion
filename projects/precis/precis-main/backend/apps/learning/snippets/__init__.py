"""Wagtail snippet view sets for the learning app (mirrors Precis structure)."""
from .specialization import SpecializationSnippetViewSet
from .tag import CourseTagSnippetViewSet

__all__ = ["SpecializationSnippetViewSet", "CourseTagSnippetViewSet"]
