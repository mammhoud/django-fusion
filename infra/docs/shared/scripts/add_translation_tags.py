#!/usr/bin/env python3
"""
Add Django translation tags to template files for Phase 2.8.
Wraps hardcoded text with {% trans %} or {% blocktrans %} tags.
"""

import re
from pathlib import Path
from typing import List, Tuple

TARGET_BASE = Path("structa.cloud")
TEMPLATE_DIR = TARGET_BASE / "apps/templates"

# Patterns to match hardcoded text in templates
# This is a simplified approach - production would need more sophisticated parsing

def add_translation_tags_to_file(file_path: Path) -> Tuple[bool, int]:
    """Add translation tags to a template file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        tags_added = 0

        # Pattern 1: Simple text in tags like <h1>Welcome</h1>
        # Match text between tags that isn't already translated
        pattern1 = r'(<[^>]+>)([^<{%][^<]*?)(<\/[^>]+>)'

        def replace_simple_text(match):
            nonlocal tags_added
            opening = match.group(1)
            text = match.group(2).strip()
            closing = match.group(3)

            # Skip if already has translation tags or is empty
            if not text or '{%' in text or '{{' in text or text.startswith('trans'):
                return match.group(0)

            # Skip very short text (single words often don't need translation)
            if len(text) < 3:
                return match.group(0)

            tags_added += 1
            return f'{opening}{{% trans "{text}" %}}{closing}'

        # Apply pattern 1 carefully (only to specific tags)
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span', 'label', 'button', 'a']:
            pattern = rf'(<{tag}[^>]*>)([^<{{%][^<]*?)(<\/{tag}>)'
            content = re.sub(pattern, replace_simple_text, content, flags=re.IGNORECASE)

        # Pattern 2: Text in attributes (title, placeholder, alt, etc.)
        # This is more complex and risky, so we'll be conservative

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, tags_added

        return False, 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, 0


def process_templates():
    """Process all template files."""
    if not TEMPLATE_DIR.exists():
        print(f"Template directory not found: {TEMPLATE_DIR}")
        return

    total_files = 0
    total_tags = 0

    for template_file in TEMPLATE_DIR.rglob("*.html"):
        success, tags = add_translation_tags_to_file(template_file)
        if success:
            total_files += 1
            total_tags += tags
            print(f"✅ {template_file.relative_to(TARGET_BASE)}: {tags} tags added")

    print(f"\nTotal files updated: {total_files}")
    print(f"Total translation tags added: {total_tags}")


if __name__ == "__main__":
    print("Adding translation tags to templates...")
    process_templates()
