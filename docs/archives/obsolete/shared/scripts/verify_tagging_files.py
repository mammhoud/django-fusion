#!/usr/bin/env python3
"""
File-based verification for the tagging system implementation.

This script verifies that all tagging system files exist and have the correct structure
without requiring imports or a full Django environment.
"""

import os
import sys


def check_file_exists(path):
    """Check if a file exists."""
    return os.path.isfile(path)


def check_file_contains(path, search_strings):
    """Check if a file contains specific strings."""
    if not check_file_exists(path):
        return False, f"File not found: {path}"

    with open(path, 'r') as f:
        content = f.read()

    missing = []
    for search_str in search_strings:
        if search_str not in content:
            missing.append(search_str)

    if missing:
        return False, f"Missing: {', '.join(missing)}"

    return True, "OK"


def main():
    """Run file verification checks."""
    print("=" * 70)
    print("Tagging System File Verification")
    print("=" * 70)

    base_path = os.path.dirname(os.path.abspath(__file__))

    checks = [
        # Tag models file
        {
            'name': 'Tag Models (tags.py)',
            'path': 'apps/accounts/models/tags.py',
            'required_strings': [
                'class Tag(models.Model):',
                'class TaggedItem(models.Model):',
                'class TagManager(models.Manager):',
                'def filter_by_tag(self, tag_name):',
                'def filter_by_tags(self, tag_names, match_all=False):',
                'def search_by_tags(self, search_term):',
            ]
        },
        # Example tagged models
        {
            'name': 'Example Tagged Models (example_tagged_model.py)',
            'path': 'apps/accounts/models/example_tagged_model.py',
            'required_strings': [
                'class Article(models.Model):',
                'class Product(models.Model):',
                'def get_tag_list(self):',
                'def add_tag(self, tag_name, user=None):',
                'def remove_tag(self, tag_name):',
                'objects = TagManager()',
            ]
        },
        # Admin interface
        {
            'name': 'Admin Interface (admin/tags.py)',
            'path': 'apps/accounts/admin/tags.py',
            'required_strings': [
                '@admin.register(Tag)',
                'class TagAdmin(admin.ModelAdmin):',
                '@admin.register(TaggedItem)',
                'class TaggedItemAdmin(admin.ModelAdmin):',
            ]
        },
        # Views
        {
            'name': 'Views (views/tags.py)',
            'path': 'apps/accounts/views/tags.py',
            'required_strings': [
                'class TagListView(ListView):',
                'class TagDetailView(DetailView):',
                'class ArticlesByTagView(ListView):',
                'class ProductsByTagView(ListView):',
                'def search_tags(request):',
                'def filter_by_tags(request):',
            ]
        },
        # Tests
        {
            'name': 'Tagging System Tests (test_tagging_system.py)',
            'path': 'tests/test_tagging_system.py',
            'required_strings': [
                'class TestTagModel:',
                'class TestTaggedItem:',
                'class TestArticleTagging:',
                'class TestProductTagging:',
                'class TestTagFiltering:',
                'class TestTagSearch:',
            ]
        },
        # Unit tests
        {
            'name': 'Unit Tests (test_tagging_unit.py)',
            'path': 'tests/test_tagging_unit.py',
            'required_strings': [
                'class TestTagModel:',
                'class TestTaggedItemModel:',
                'class TestTagManager:',
                'class TestArticleModel:',
                'class TestProductModel:',
            ]
        },
    ]

    results = []

    for check in checks:
        full_path = os.path.join(base_path, check['path'])
        exists = check_file_exists(full_path)

        if not exists:
            print(f"\n✗ {check['name']}")
            print(f"  File not found: {check['path']}")
            results.append((check['name'], False))
            continue

        print(f"\n✓ {check['name']}")
        print(f"  File exists: {check['path']}")

        success, message = check_file_contains(full_path, check['required_strings'])

        if success:
            print(f"  ✓ All required components found")
            results.append((check['name'], True))
        else:
            print(f"  ✗ {message}")
            results.append((check['name'], False))

    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n✓ All file checks passed! Tagging system files are properly created.")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
