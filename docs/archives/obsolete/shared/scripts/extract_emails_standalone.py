#!/usr/bin/env python3
"""
Standalone email extraction script - no Django required.
Extracts emails from markdown files in spec directories.
"""
import csv
import re
from datetime import datetime, timezone
from pathlib import Path

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

def extract_from_file(path: Path) -> list[str]:
    """Return deduplicated emails found in a single file."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return list(dict.fromkeys(EMAIL_RE.findall(text)))

def extract_from_directory(directory: Path, extensions=(".md", ".txt", ".rst")):
    """Yield dicts with keys: email, source_file, source_spec."""
    for ext in extensions:
        for filepath in sorted(directory.rglob(f"*{ext}")):
            parts = filepath.parts
            source_spec = ""
            try:
                if len(parts) >= 2:
                    source_spec = parts[-2]
            except (IndexError, AttributeError):
                source_spec = ""

            for email in extract_from_file(filepath):
                yield {
                    "email": email.lower(),
                    "source_file": str(filepath),
                    "source_spec": source_spec
                }

def read_csv(csv_path: Path) -> list[dict]:
    """Read existing CSV file."""
    if not csv_path.exists():
        return []
    with csv_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(csv_path: Path, rows: list[dict]):
    """Write rows to CSV file."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["email", "source_spec", "source_file", "extracted_at"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

def merge_emails(csv_path: Path, new_rows: list[dict]) -> int:
    """Merge new_rows into existing CSV, deduplicating by email."""
    existing = {r["email"]: r for r in read_csv(csv_path)}
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

    write_csv(csv_path, list(existing.values()))
    return added

if __name__ == "__main__":
    scan_dir = Path(".kiro/specs-organized")
    output = Path(".kiro/specs/email-list.csv")

    print(f"Scanning: {scan_dir}")
    print("Extracting emails from files...")

    rows = list(extract_from_directory(scan_dir))
    print(f"Found {len(rows)} email occurrences")

    print("Merging emails into CSV...")
    added = merge_emails(output, rows)

    print(f"✓ Added {added} new unique emails → {output}")
    print(f"✓ Total unique emails in CSV: {len(read_csv(output))}")
