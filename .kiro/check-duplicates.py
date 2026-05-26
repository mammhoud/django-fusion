#!/usr/bin/env python3
"""
Script to check for duplicate or similar spec names across categories.
Helps maintain organization and avoid duplicates.
"""

import os
import re
from collections import defaultdict

def get_all_specs(base_path="."):
    """Get all specs organized by category."""
    specs_by_category = {}
    all_specs = []

    for category in os.listdir(base_path):
        category_path = os.path.join(base_path, category)
        if os.path.isdir(category_path) and category not in [".", ".."]:
            specs = []
            for item in os.listdir(category_path):
                item_path = os.path.join(category_path, item)
                if os.path.isdir(item_path) and item not in [".", ".."]:
                    specs.append(item)
                    all_specs.append((category, item))
            specs_by_category[category] = specs

    return specs_by_category, all_specs

def find_similar_names(specs_by_category):
    """Find potentially similar spec names."""
    word_frequency = defaultdict(int)
    all_words = []

    for category, specs in specs_by_category.items():
        for spec in specs:
            # Split by hyphens and underscores
            words = re.split(r'[-_]', spec.lower())
            for word in words:
                if word and len(word) > 2:  # Ignore short words
                    word_frequency[word] += 1
                    all_words.append((category, spec, word))

    # Find words that appear in multiple specs
    common_words = {word: count for word, count in word_frequency.items() if count > 1}

    # Group specs by common words
    similar_groups = defaultdict(list)
    for category, spec, word in all_words:
        if word in common_words:
            similar_groups[word].append((category, spec))

    return similar_groups

def suggest_category(spec_name):
    """Suggest a category based on spec name keywords."""
    spec_lower = spec_name.lower()

    category_keywords = {
        'auth': ['auth', 'login', 'logout', 'register', 'password', 'user', 'permission'],
        'docs': ['doc', 'documentation', 'readme', 'guide', 'manual', 'wiki'],
        'integration': ['integration', 'connect', 'api', 'sync', 'bridge', 'adapter'],
        'fixes': ['fix', 'bug', 'error', 'issue', 'problem', 'crash', 'broken'],
        'modernization': ['modern', 'update', 'upgrade', 'refactor', 'improve', 'optimize'],
        'features': ['feature', 'new', 'add', 'implement', 'create', 'build']
    }

    suggestions = []
    for category, keywords in category_keywords.items():
        for keyword in keywords:
            if keyword in spec_lower:
                suggestions.append(category)
                break

    return list(set(suggestings)) if suggestions else ['features']

def main():
    base_path = "."
    specs_by_category, all_specs = get_all_specs(base_path)

    print("=" * 60)
    print("SPEC ORGANIZATION CHECK")
    print("=" * 60)

    print("\n📁 Current Organization:")
    for category, specs in sorted(specs_by_category.items()):
        print(f"\n  {category.upper()} ({len(specs)} specs):")
        for spec in sorted(specs):
            print(f"    • {spec}")

    print("\n" + "=" * 60)
    print("🔍 Similarity Check:")
    similar_groups = find_similar_names(specs_by_category)

    if similar_groups:
        print("Potential duplicates or similar specs found:")
        for word, specs in sorted(similar_groups.items()):
            if len(specs) > 1:
                print(f"\n  Word: '{word}' appears in:")
                for category, spec in specs:
                    print(f"    • {category}/{spec}")
    else:
        print("No obvious duplicates found.")

    print("\n" + "=" * 60)
    print("💡 Category Suggestions for New Specs:")
    print("Enter a spec name to get category suggestions")
    print("(Press Ctrl+C to exit)")

    while True:
        try:
            spec_name = input("\nSpec name (kebab-case): ").strip()
            if not spec_name:
                continue

            suggestions = suggest_category(spec_name)
            print(f"Suggested categories: {', '.join(suggestions)}")

            # Check if similar spec exists
            spec_lower = spec_name.lower()
            existing_similar = []
            for category, specs in specs_by_category.items():
                for spec in specs:
                    if spec_lower in spec.lower() or spec.lower() in spec_lower:
                        existing_similar.append((category, spec))

            if existing_similar:
                print(f"⚠️  Warning: Similar specs exist:")
                for category, spec in existing_similar:
                    print(f"    • {category}/{spec}")

        except KeyboardInterrupt:
            print("\n\nExiting. Keep your specs organized! 🗂️")
            break

if __name__ == "__main__":
    main()
