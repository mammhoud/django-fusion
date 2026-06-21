"""
EmailCSVManager — read/write email lists with source tracking.
"""
import csv
from datetime import datetime, timezone
from pathlib import Path

FIELDNAMES = ["email", "source_spec", "source_file", "extracted_at"]


class EmailCSVManager:
    """Manage a CSV file of extracted emails with deduplication."""

    def __init__(self, csv_path: Path):
        self.csv_path = Path(csv_path)

    def read(self) -> list[dict]:
        if not self.csv_path.exists():
            return []
        with self.csv_path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def write(self, rows: list[dict]) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    def merge(self, new_rows: list[dict]) -> int:
        """Merge new_rows into existing CSV, deduplicating by email. Returns added count."""
        existing = {r["email"]: r for r in self.read()}
        added = 0
        ts = datetime.now(timezone.utc).isoformat()
        for row in new_rows:
            email = row.get("email", "").lower().strip()
            if email and email not in existing:
                existing[email] = {
                    "email": email,
                    "source_spec": row.get("source_spec", ""),
                    "source_file": row.get("source_file", ""),
                    "extracted_at": ts,
                }
                added += 1
        self.write(list(existing.values()))
        return added
