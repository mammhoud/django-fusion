"""
Handlers Views Module
"""

from . import privacy
from .tags import (
    ArticlesByTagView,
    ProductsByTagView,
    TagDetailView,
    TagListView,
    filter_by_tags,
    search_tags,
)

__all__ = [
    "privacy",
    "TagListView",
    "TagDetailView",
    "ArticlesByTagView",
    "ProductsByTagView",
    "search_tags",
    "filter_by_tags",
]
