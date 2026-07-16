#!/usr/bin/env python
"""Merge two fixture files into one comprehensive fixture."""
import json
from pathlib import Path


def merge_fixtures():
    """Merge ctc-research-data.json and wagtail_pages_dump.json."""
    base_dir = Path(__file__).parent

    # Load both fixture files
    with open(base_dir / "ctc-research-data.json") as f:
        data1 = json.load(f)

    with open(base_dir / "wagtail_pages_dump.json") as f:
        data2 = json.load(f)

    # Merge into single array
    merged = data1 + data2

    # Write merged fixture
    output_file = base_dir / "ctc-research-complete-data.json"
    with open(output_file, "w") as f:
        json.dump(merged, f, indent=2)

    print(f"✓ Merged {len(data1)} items from ctc-research-data.json")
    print(f"✓ Merged {len(data2)} items from wagtail_pages_dump.json")
    print(f"✓ Total: {len(merged)} items")
    print(f"✓ Output: {output_file}")

    return output_file

if __name__ == "__main__":
    merge_fixtures()
