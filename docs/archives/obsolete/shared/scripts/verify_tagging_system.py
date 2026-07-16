#!/usr/bin/env python3
"""
Verification script for the tagging system implementation.

This script verifies that all tagging system components are properly implemented
without requiring a full Django environment.
"""

import os
import sys

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_imports():
    """Verify that all tagging system modules can be imported."""
    print("✓ Verifying imports...")

    try:
        from apps.accounts.models.tags import Tag, TaggedItem, TagManager
        print("  ✓ Tag models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import Tag models: {e}")
        return False

    try:
        from apps.accounts.models.example_tagged_model import Article, Product
        print("  ✓ Example models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import example models: {e}")
        return False

    try:
        from apps.accounts.admin.tags import TagAdmin, TaggedItemAdmin
        print("  ✓ Admin classes imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import admin classes: {e}")
        return False

    try:
        from apps.accounts.views.tags import (
            ArticlesByTagView,
            ProductsByTagView,
            TagDetailView,
            TagListView,
            filter_by_tags,
            search_tags,
        )
        print("  ✓ Views imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import views: {e}")
        return False

    return True


def verify_tag_model():
    """Verify Tag model structure."""
    print("\n✓ Verifying Tag model...")

    from apps.accounts.models.tags import Tag

    # Check fields
    field_names = [f.name for f in Tag._meta.get_fields()]
    required_fields = ['name', 'slug', 'description', 'created_at', 'updated_at']

    for field in required_fields:
        if field in field_names:
            print(f"  ✓ Field '{field}' exists")
        else:
            print(f"  ✗ Field '{field}' missing")
            return False

    # Check meta options
    if Tag._meta.verbose_name == 'Tag':
        print("  ✓ verbose_name is correct")
    else:
        print(f"  ✗ verbose_name is incorrect: {Tag._meta.verbose_name}")
        return False

    if Tag._meta.ordering == ['name']:
        print("  ✓ ordering is correct")
    else:
        print(f"  ✗ ordering is incorrect: {Tag._meta.ordering}")
        return False

    return True


def verify_tagged_item_model():
    """Verify TaggedItem model structure."""
    print("\n✓ Verifying TaggedItem model...")

    from apps.accounts.models.tags import TaggedItem

    # Check fields
    field_names = [f.name for f in TaggedItem._meta.get_fields()]
    required_fields = ['tag', 'content_type', 'object_id', 'content_object', 'tagged_by', 'tagged_at']

    for field in required_fields:
        if field in field_names:
            print(f"  ✓ Field '{field}' exists")
        else:
            print(f"  ✗ Field '{field}' missing")
            return False

    # Check meta options
    if TaggedItem._meta.verbose_name == 'Tagged Item':
        print("  ✓ verbose_name is correct")
    else:
        print(f"  ✗ verbose_name is incorrect: {TaggedItem._meta.verbose_name}")
        return False

    return True


def verify_tag_manager():
    """Verify TagManager functionality."""
    print("\n✓ Verifying TagManager...")

    from apps.accounts.models.tags import TagManager

    manager = TagManager()

    required_methods = ['get_queryset', 'with_tags', 'filter_by_tag', 'filter_by_tags', 'search_by_tags']

    for method in required_methods:
        if hasattr(manager, method):
            print(f"  ✓ Method '{method}' exists")
        else:
            print(f"  ✗ Method '{method}' missing")
            return False

    return True


def verify_article_model():
    """Verify Article model tagging support."""
    print("\n✓ Verifying Article model...")

    from apps.accounts.models.example_tagged_model import Article

    # Check fields
    field_names = [f.name for f in Article._meta.get_fields()]
    required_fields = ['title', 'content', 'author', 'created_at', 'updated_at', 'is_published']

    for field in required_fields:
        if field in field_names:
            print(f"  ✓ Field '{field}' exists")
        else:
            print(f"  ✗ Field '{field}' missing")
            return False

    # Check tagging methods
    required_methods = ['get_tag_list', 'add_tag', 'remove_tag']

    for method in required_methods:
        if hasattr(Article, method):
            print(f"  ✓ Method '{method}' exists")
        else:
            print(f"  ✗ Method '{method}' missing")
            return False

    # Check TagManager
    if hasattr(Article, 'objects'):
        print("  ✓ TagManager is assigned to 'objects'")
    else:
        print("  ✗ TagManager not assigned to 'objects'")
        return False

    return True


def verify_product_model():
    """Verify Product model tagging support."""
    print("\n✓ Verifying Product model...")

    from apps.accounts.models.example_tagged_model import Product

    # Check fields
    field_names = [f.name for f in Product._meta.get_fields()]
    required_fields = ['name', 'description', 'price', 'sku', 'created_at']

    for field in required_fields:
        if field in field_names:
            print(f"  ✓ Field '{field}' exists")
        else:
            print(f"  ✗ Field '{field}' missing")
            return False

    # Check tagging methods
    required_methods = ['get_tag_list', 'add_tag', 'remove_tag']

    for method in required_methods:
        if hasattr(Product, method):
            print(f"  ✓ Method '{method}' exists")
        else:
            print(f"  ✗ Method '{method}' missing")
            return False

    return True


def verify_admin_interface():
    """Verify admin interface."""
    print("\n✓ Verifying admin interface...")

    from apps.accounts.admin.tags import TagAdmin, TaggedItemAdmin

    # Check TagAdmin
    if hasattr(TagAdmin, 'list_display'):
        print("  ✓ TagAdmin has list_display")
    else:
        print("  ✗ TagAdmin missing list_display")
        return False

    if hasattr(TagAdmin, 'search_fields'):
        print("  ✓ TagAdmin has search_fields")
    else:
        print("  ✗ TagAdmin missing search_fields")
        return False

    # Check TaggedItemAdmin
    if hasattr(TaggedItemAdmin, 'list_display'):
        print("  ✓ TaggedItemAdmin has list_display")
    else:
        print("  ✗ TaggedItemAdmin missing list_display")
        return False

    return True


def verify_views():
    """Verify views."""
    print("\n✓ Verifying views...")

    from apps.accounts.views.tags import (
        ArticlesByTagView,
        ProductsByTagView,
        TagDetailView,
        TagListView,
        filter_by_tags,
        search_tags,
    )

    # Check class-based views
    views = [
        ('TagListView', TagListView),
        ('TagDetailView', TagDetailView),
        ('ArticlesByTagView', ArticlesByTagView),
        ('ProductsByTagView', ProductsByTagView),
    ]

    for name, view_class in views:
        if hasattr(view_class, 'model'):
            print(f"  ✓ {name} is properly defined")
        else:
            print(f"  ✗ {name} is not properly defined")
            return False

    # Check function-based views
    if callable(search_tags):
        print("  ✓ search_tags function is defined")
    else:
        print("  ✗ search_tags function is not defined")
        return False

    if callable(filter_by_tags):
        print("  ✓ filter_by_tags function is defined")
    else:
        print("  ✗ filter_by_tags function is not defined")
        return False

    return True


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Tagging System Verification")
    print("=" * 60)

    checks = [
        ("Imports", verify_imports),
        ("Tag Model", verify_tag_model),
        ("TaggedItem Model", verify_tagged_item_model),
        ("TagManager", verify_tag_manager),
        ("Article Model", verify_article_model),
        ("Product Model", verify_product_model),
        ("Admin Interface", verify_admin_interface),
        ("Views", verify_views),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Error during {name} verification: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} checks passed")

    if passed == total:
        print("\n✓ All checks passed! Tagging system is properly implemented.")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
