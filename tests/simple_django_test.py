#!/usr/bin/env python3
"""
Simple Django Test Script
Tests basic Django functionality inside the container
"""

import os
import sys

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, '/app')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.db import connection
from django.db.utils import OperationalError


def test_database_connection():
    """Test database connection."""
    try:
        connection.ensure_connection()
        print("✅ Database connection successful")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_django_tables():
    """Check if core Django tables exist."""
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType

    try:
        # Try to count users
        user_count = User.objects.count()
        print(f"✅ User table: {user_count} users")

        # Try to count content types
        content_type_count = ContentType.objects.count()
        print(f"✅ ContentType table: {content_type_count} records")

        return True
    except Exception as e:
        print(f"❌ Django tables check failed: {e}")
        return False

def test_migrations():
    """Check if migrations are applied."""
    from django.db.migrations.loader import MigrationLoader

    try:
        loader = MigrationLoader(connection)
        applied = loader.applied_migrations
        print(f"✅ Migrations: {len(applied)} applied")
        return True
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

def test_environment():
    """Check environment variables."""
    from django.conf import settings

    print(f"✅ DEBUG mode: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS[:3]}...")
    print(f"✅ Database engine: {settings.DATABASES['default']['ENGINE']}")

    return not settings.DEBUG  # DEBUG should be False in production

def main():
    """Run all tests."""
    print("🚀 Django Container Test")
    print("=" * 50)

    tests_passed = 0
    total_tests = 4

    # Test 1: Database connection
    if test_database_connection():
        tests_passed += 1

    # Test 2: Django tables
    if test_django_tables():
        tests_passed += 1

    # Test 3: Migrations
    if test_migrations():
        tests_passed += 1

    # Test 4: Environment
    if test_environment():
        tests_passed += 1

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Passed: {tests_passed}/{total_tests}")
    print(f"❌ Failed: {total_tests - tests_passed}/{total_tests}")

    success_rate = (tests_passed / total_tests) * 100
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if success_rate >= 75:
        print("\n🎉 Container Django environment is healthy!")
        return 0
    else:
        print("\n⚠️  Container Django environment has issues!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
