"""
POS Solo — AboutFragment.

Version and system information for the About page.

Fragment name: ``pos.about``
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fragments import FragmentComponent, register


@register
class AboutFragment(FragmentComponent):
    """Application version, description, and system-level metadata."""

    fragment_name = "pos.about"

    def get_context(self, **kwargs: Any) -> dict[str, Any]:
        from __about__ import __title__, __version__
        from models.node import Node

        node_count = Node.objects.filter(is_active=True).count()
        db_path = Path(__file__).resolve().parent.parent.parent / "restaurant.db"
        db_size_mb = round(db_path.stat().st_size / (1024 * 1024), 1) if db_path.exists() else 0.0

        return {
            "title": __title__ or "Forge POS Solo",
            "version": __version__,
            "description": (
                "A standalone point-of-sale system for single-restaurant operations. "
                "Fast, lightweight, and runs entirely offline."
            ),
            "year": datetime.now(timezone.utc).year,
            "node_count": node_count,
            "db_size_mb": db_size_mb,
        }
