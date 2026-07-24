"""
POS Full — AboutFragment.

Version and system information for the About page.

Fragment name: ``pos.about``

Template context::

    {
        "title": "Forge POS",
        "version": "1.2.3",
        "description": "...",
        "year": 2026,
        "node_count": 5,
        "db_size_mb": 12.5,
        "uptime_days": 14,
    }
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
        from __about__ import __title_full__, __version__
        from models.node import Node

        # Node count (other registered devices)
        node_count = Node.objects.filter(is_active=True).count()

        # Database file size in MB
        db_path = Path(__file__).resolve().parent.parent.parent / "restaurant.db"
        db_size_mb = round(db_path.stat().st_size / (1024 * 1024), 1) if db_path.exists() else 0.0

        return {
            "title": __title_full__,
            "version": __version__,
            "description": (
                "A modern point-of-sale system built with Rust, Tauri, and React. "
                "Manage products, process sales, track inventory, and run your "
                "restaurant efficiently."
            ),
            "year": datetime.now(timezone.utc).year,
            "node_count": node_count,
            "db_size_mb": db_size_mb,
        }
