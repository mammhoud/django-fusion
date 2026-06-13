#!/usr/bin/env python
"""Remove Organization objects from fixture to avoid schema mismatch."""
import json
from pathlib import Path


def remove_organizations():
    """Remove Organization objects from the merged fixture."""
    base_dir = Path(__file__).parent

    fixture_file = base_dir / "ctc-research-complete-data.json"

    with open(fixture_file) as f:
        data = json.load(f)

    # Filter out Organization objects
    filtered_data = [item for item in data if item.get("model") != "accounts.organization"]

    # Write filtered fixture
    with open(fixture_file, "w") as f:
        json.dump(filtered_data, f, indent=2)

    removed_count = len(data) - len(filtered_data)
    print(f"✓ Removed {removed_count} Organization objects from fixture")
    print(f"✓ Remaining objects: {len(filtered_data)}")


if __name__ == "__main__":
    remove_organizations()
