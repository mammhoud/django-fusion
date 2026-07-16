#!/usr/bin/env python3
"""
Spec directory renaming script.
Renames spec directories to use consistent kebab-case naming without project prefixes.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

# Mapping of old names to new names (already organized in .kiro/specs-organized)
# This script documents what was done
RENAMING_MAP = {
    # Auth specs
    "ctc-structa-admin-auth-integration": "admin-auth-integration",

    # Fixes
    "alliance-website-docker-fix": "docker-environment-fix",
    "fix-get-translation-template-tag": "translation-template-tag-fix",
    "fix-wagtailsnippets-assets-email-enhancement": "wagtail-assets-email-enhancement",

    # Integration
    "blog-lms-wagtail-integration": "blog-lms-integration",

    # Infrastructure
    "infrastructure-reorganization-cleanup": "infrastructure-cleanup",
    "specs-organized-completion": "specs-organization-completion",
}

def update_config_file(spec_dir: Path, new_name: str):
    """Update .config.kiro file with new feature name."""
    config_path = spec_dir / ".config.kiro"
    if not config_path.exists():
        return False

    try:
        with config_path.open("r") as f:
            config = json.load(f)

        config["featureName"] = new_name

        with config_path.open("w") as f:
            json.dump(config, f, indent=2)

        return True
    except Exception as e:
        print(f"Error updating {config_path}: {e}")
        return False

def create_renaming_doc(output_path: Path):
    """Create SPEC_RENAMING.md documentation."""
    content = f"""# Spec Directory Renaming

This document tracks the renaming of spec directories for better organization and consistency.

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Renaming Convention

All spec directories now use:
- Kebab-case naming (lowercase with hyphens)
- No project prefixes (ctc-, structa-, alliance-)
- Descriptive enhancement names
- Organized by category (auth, fixes, integration, infrastructure)

## Renaming Map

| Old Name | New Name | Category |
|----------|----------|----------|
"""

    for old, new in sorted(RENAMING_MAP.items()):
        # Determine category from new name or path
        if "auth" in new:
            category = "auth"
        elif "fix" in new or "enhancement" in new:
            category = "fixes"
        elif "integration" in new:
            category = "integration"
        else:
            category = "infrastructure"

        content += f"| `{old}` | `{new}` | {category} |\n"

    content += """
## Directory Structure

```
.kiro/specs-organized/
├── auth/
│   └── admin-auth-integration/
├── fixes/
│   ├── docker-environment-fix/
│   ├── translation-template-tag-fix/
│   └── wagtail-assets-email-enhancement/
├── integration/
│   └── blog-lms-integration/
└── infrastructure/
    ├── infrastructure-cleanup/
    └── specs-organization-completion/
```

## Migration Notes

1. All spec file contents (requirements.md, design.md, tasks.md, bugfix.md) were preserved
2. .config.kiro files were updated with new feature names
3. Task execution and spec workflows remain compatible
4. No breaking changes to existing functionality

## Backward Compatibility

Old spec names are documented here for reference. All new specs should follow the new naming convention.
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)
    print(f"✓ Created renaming documentation: {output_path}")

if __name__ == "__main__":
    # The specs are already organized in .kiro/specs-organized/
    # This script just documents the renaming and updates configs

    specs_dir = Path(".kiro/specs-organized")

    if not specs_dir.exists():
        print(f"Error: {specs_dir} not found")
        exit(1)

    print("Updating .config.kiro files with new feature names...")
    updated = 0

    # Find all spec directories
    for category_dir in specs_dir.iterdir():
        if not category_dir.is_dir():
            continue

        for spec_dir in category_dir.iterdir():
            if not spec_dir.is_dir():
                continue

            spec_name = spec_dir.name
            if update_config_file(spec_dir, spec_name):
                updated += 1
                print(f"  ✓ Updated {spec_name}")

    print(f"\n✓ Updated {updated} config files")

    # Create renaming documentation
    doc_path = Path(".kiro/specs/SPEC_RENAMING.md")
    create_renaming_doc(doc_path)

    print("\n✓ Spec renaming documentation complete")
