"""Branch-scoped database aliases — optional per-branch read/export targets.

The tenant schema remains the source of truth; a branch may point at a
different Postgres target (regional replica, reporting DB) via its
``BranchSettings.settings["database_alias"]``. That alias is an **optional
read-only** target, never a second write path — services use
``QuerySet.using(alias)`` for reporting/export jobs only.
"""

from __future__ import annotations


def branch_database_aliases() -> dict[str, str]:
    """Map branch code → DATABASES alias, from each branch's settings JSON."""
    from django.conf import settings

    from apps.core.models import Branch

    aliases: dict[str, str] = {}
    for branch in Branch.objects.all():
        alias = (branch.branch_settings.settings or {}).get("database_alias")
        if alias and alias in settings.DATABASES:
            aliases[branch.code] = alias
    return aliases
