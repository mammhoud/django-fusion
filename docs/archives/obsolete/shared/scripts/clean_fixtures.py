#!/usr/bin/env python
"""Clean fixture files by removing fields that don't exist in current models."""
import json
from datetime import datetime
from datetime import timezone as tz
from pathlib import Path


def clean_fixtures():
    """Remove problematic fields from fixtures and add default values."""
    base_dir = Path(__file__).parent

    # Models that have created_at/updated_at fields (from DefaultBase)
    models_with_timestamps = [
        "handlers.organization",
    ]

    # Models that have is_active field
    models_with_is_active = [
        "handlers.organization",
    ]

    # Fields to remove from specific models
    fields_to_remove_specific = {
        "handlers.organization": [
            "first_published_at", "last_published_at", "search_description", "created_by", "updated_by"
        ],  # These fields were removed in migration 0004 (but live is still in DB)
    }

    # Fields to remove from ALL models (audit fields only)
    fields_to_remove_all = ["created_by", "updated_by", "created_at", "updated_at"]

    # Fields to remove if not in model
    fields_to_remove_if_not_in_model = {
        "is_active": models_with_is_active,  # Remove is_active from models not in this list
        "live": ["wagtailcore.page", "pages.aboutpage", "pages.contactpage", "pages.homepage", "pages.teampage", "lms.coursespage"],  # Only these models have live (NOT Organization)
    }

    # Default timestamp for fixtures
    default_timestamp = datetime.now(tz.utc).isoformat()

    # Load both fixture files
    files_to_clean = [
        base_dir / "ctc-research-data.json",
        base_dir / "wagtail_pages_dump.json",
    ]

    for fixture_file in files_to_clean:
        if not fixture_file.exists():
            print(f"⚠ File not found: {fixture_file}")
            continue

        with open(fixture_file) as f:
            data = json.load(f)

        removed_count = 0
        for item in data:
            model = item.get("model", "")
            fields = item.get("fields", {})

            # Remove fields from all models
            for field in fields_to_remove_all:
                if field in fields:
                    del fields[field]
                    removed_count += 1

            # Remove fields from models that don't have them
            for field, allowed_models in fields_to_remove_if_not_in_model.items():
                if field in fields and model not in allowed_models:
                    del fields[field]
                    removed_count += 1

            # Add default values for live field (all models that have it)
            if "live" in fields and fields["live"] is None:
                fields["live"] = True
            elif "live" not in fields and model in ["handlers.organization", "wagtailcore.page", "pages.aboutpage", "pages.contactpage", "pages.homepage", "pages.teampage", "lms.coursespage"]:
                # Add live field if missing for models that have it
                fields["live"] = True

            # For Organization, add live field even though it's not in the model
            # because the database table still has it
            if model == "handlers.organization" and "live" not in fields:
                fields["live"] = True

            # Add default values for is_active field (only specific models)
            if model in models_with_is_active:
                if "is_active" in fields and fields["is_active"] is None:
                    fields["is_active"] = True

            # Add default timestamps only to models that have them
            if model in models_with_timestamps:
                if "created_at" not in fields:
                    fields["created_at"] = default_timestamp
                if "updated_at" not in fields:
                    fields["updated_at"] = default_timestamp

            # Check if this model has specific fields to remove
            for model_key, fields_list in fields_to_remove_specific.items():
                if model == model_key:
                    for field in fields_list:
                        if field in fields:
                            del fields[field]
                            removed_count += 1

        # Write cleaned fixture
        with open(fixture_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✓ Cleaned {fixture_file.name}: removed {removed_count} problematic fields")


if __name__ == "__main__":
    clean_fixtures()
