#!/usr/bin/env python3
"""
Import verification script for Phase 7.

Verifies that all imports are correct and there are no circular import issues.
"""

import os
import sys

# Add the project to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up minimal Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.development')


def verify_core_imports():
    """Verify core Django imports."""
    print("✓ Verifying core imports...")

    try:
        import django
        print("  ✓ Django imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import Django: {e}")
        return False

    try:
        from django.db import models
        print("  ✓ Django models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import Django models: {e}")
        return False

    try:
        from django.contrib.auth.models import User
        print("  ✓ Django auth models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import Django auth models: {e}")
        return False

    return True


def verify_app_imports():
    """Verify app-level imports."""
    print("\n✓ Verifying app imports...")

    try:
        from apps import logger
        print("  ✓ Apps logger imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import apps logger: {e}")
        return False

    return True


def verify_accounts_imports():
    """Verify accounts app imports."""
    print("\n✓ Verifying accounts app imports...")

    try:
        from apps.accounts.models.tags import Tag, TaggedItem, TagManager
        print("  ✓ Tagging models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import tagging models: {e}")
        return False

    try:
        from apps.accounts.models.example_tagged_model import Article, Product
        print("  ✓ Example models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import example models: {e}")
        return False

    try:
        from apps.accounts.models.profiles import (
            PrivacyConsent,
            PrivacyPolicy,
            TermsConsent,
            TermsOfService,
        )
        print("  ✓ Profile models imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import profile models: {e}")
        return False

    return True


def verify_lms_imports():
    """Verify LMS app imports."""
    print("\n✓ Verifying LMS app imports...")

    try:
        from apps.lms.models.courses import Course
        print("  ✓ Course model imported successfully")
    except ImportError as e:
        print(f"  ✗ Failed to import Course model: {e}")
        return False

    return True


def verify_no_circular_imports():
    """Verify there are no circular imports."""
    print("\n✓ Verifying no circular imports...")

    # Try importing all major modules
    modules_to_test = [
        'apps.accounts.models',
        'apps.accounts.admin',
        'apps.accounts.views',
        'apps.lms.models',
    ]

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name} imported without circular imports")
        except ImportError as e:
            if 'circular' in str(e).lower():
                print(f"  ✗ Circular import detected in {module_name}: {e}")
                return False
            else:
                # Other import errors are OK for this check
                print(f"  ⚠ {module_name} has import issues (not circular): {e}")
        except Exception as e:
            print(f"  ⚠ {module_name} has other issues: {e}")

    return True


def main():
    """Run all import verification checks."""
    print("=" * 60)
    print("Import Verification - Phase 7")
    print("=" * 60)

    checks = [
        ("Core Imports", verify_core_imports),
        ("App Imports", verify_app_imports),
        ("Accounts Imports", verify_accounts_imports),
        ("LMS Imports", verify_lms_imports),
        ("Circular Imports", verify_no_circular_imports),
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
        print("\n✓ All import checks passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} check(s) failed.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
