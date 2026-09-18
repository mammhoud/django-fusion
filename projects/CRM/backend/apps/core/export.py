"""Generic per-resource CSV/JSON export for every registered resource table.

The finance module ships its own ``apps.finance.export`` with hand-picked field
shapes for invoices/payments/POS revenue. This module generalizes the same idea
to the whole ``apps.core.resources.RESOURCES`` registry so any resource table
(companies, contacts, deals, touchpoints, …) can be downloaded as a
workspace-scoped CSV or JSON file using its read projection.

Rows come from ``resources.list_rows``, so they are already JSON-safe (Decimal
→ string, date/datetime → ISO-8601) and honour the caller's workspace scoping
and optional ``search`` filter. CSV serialization is a thin ``csv.DictWriter``
pass with ``None`` flattened to an empty cell.
"""

from __future__ import annotations

import csv
import io
from typing import Any

from .resources import list_rows

#: Export reads the full workspace-scoped set (no client-facing pagination on
#: a download), but keep a hard ceiling so a pathological table can't exhaust
#: the worker.
EXPORT_ROW_LIMIT = 10_000_000


def resource_export_rows(
    slug: str,
    workspace_id: int | None,
    *,
    search: str = "",
) -> list[dict[str, Any]]:
    """Return every workspace-scoped row for one resource (read projection)."""
    return list_rows(slug, workspace_id, limit=EXPORT_ROW_LIMIT, offset=0, search=search)


def to_csv(rows: list[dict[str, Any]]) -> str:
    """Serialize export rows to CSV, deriving the header from the first row."""
    if not rows:
        return ""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for row in rows:
        writer.writerow({key: ("" if value is None else value) for key, value in row.items()})
    return buffer.getvalue()
