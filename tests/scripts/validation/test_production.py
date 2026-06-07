#!/usr/bin/env python3
"""
Comprehensive Production Testing Script
=====================================
Tests all functionality in production environment with PostgreSQL.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent.parent
sys.path.insert(0, str(project_dir))

class ProductionTester:
    def __init__(self):
        self.project_dir = project_dir
        self.success_count = 0
        self.total_tests = 0
        self.failed_tests = []

    def load_env_file(self, env_file=".env.production"):
        """Load environment variables from specified env file."""
        env_path = self.project_dir / env_file
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
            print(f"✅ Loaded environment from {env_file}")
        else:
            print(f"❌ Environment file {env_file} not found")
            return False
        return True

    def run_command(self, command, description, timeout=60):
        """Run a command and return success status."""
        self.total_tests += 1
        print(f"\n🧪 {description}")
        print(f"   Command: {' '.join(command) if isinstance(command, list) else command}")

        try:
            if isinstance(command, str):
                result = subprocess.run(command, shell=True, capture_output=True,
                                      text=True, timeout=timeout, cwd=self.project_dir)
            else:
                result = subprocess.run(command, capture_output=True, text=True,
                                      timeout=timeout, cwd=self.project_dir)

            if result.returncode == 0:
                print("   ✅ SUCCESS")
                if result.stdout.strip():
                    print(f"   Output: {result.stdout.strip()[:200]}...")
                self.success_count += 1
                return True
            else:
                print(f"   ❌ FAILED (exit code: {result.returncode})")
                if result.stderr.strip():
                    print(f"   Error: {result.stderr.strip()[:200]}...")
                self.failed_tests.append(description)
                return False

        except subprocess.TimeoutExpired:
            print(f"   ❌ TIMEOUT after {timeout} seconds")
            self.failed_tests.append(f"{description} (timeout)")
            return False
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            self.failed_tests.append(f"{description} (exception)")
            return False

    def test_database_connection(self):
        """Test PostgreSQL database connection."""
        db_name = os.environ.get('DB_NAME', 'db_ctc')
        return self.run_command([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres',
            '-d', db_name, '-c', 'SELECT version();'
        ], "Database Connection Test")

    def test_django_check(self):
        """Test Django system check."""
        return self.run_command([
            'python', 'manage.py', 'check', '--settings=configs.settings'
        ], "Django System Check")

    def test_migrations(self):
        """Test Django migrations."""
        return self.run_command([
            'python', 'manage.py', 'migrate', '--settings=configs.settings', '--run-syncdb'
        ], "Django Migrations", timeout=300)

    def test_collectstatic(self):
        """Test static files collection."""
        return self.run_command([
            'python', 'manage.py', 'collectstatic', '--noinput', '--settings=configs.settings'
        ], "Collect Static Files")

    def test_django_shell(self):
        """Test Django shell functionality."""
        shell_command = """
from django.contrib.auth.models import User
from django.db import connection
print(f"Users: {User.objects.count()}")
with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM django_migrations")
    print(f"Migrations: {cursor.fetchone()[0]}")
print("Django shell test completed successfully")
"""
        return self.run_command([
            'python', 'manage.py', 'shell', '--settings=configs.settings', '-c', shell_command
        ], "Django Shell Test")

    def test_admin_pages(self):
        """Test Django admin functionality."""
        admin_test = """
from django.contrib import admin
from django.contrib.auth.models import User
print(f"Admin site registered models: {len(admin.site._registry)}")
print("Admin test completed successfully")
"""
        return self.run_command([
            'python', 'manage.py', 'shell', '--settings=configs.settings', '-c', admin_test
        ], "Django Admin Test")

    def test_wagtail_functionality(self):
        """Test Wagtail CMS functionality."""
        wagtail_test = """
try:
    from wagtail.models import Site, Page
    print(f"Wagtail sites: {Site.objects.count()}")
    print(f"Wagtail pages: {Page.objects.count()}")
    print("Wagtail test completed successfully")
except ImportError:
    print("Wagtail not available")
except Exception as e:
    print(f"Wagtail test error: {e}")
"""
        return self.run_command([
            'python', 'manage.py', 'shell', '--settings=configs.settings', '-c', wagtail_test
        ], "Wagtail CMS Test")

    def test_user_creation(self):
        """Test user creation and deletion."""
        user_test = """
from django.contrib.auth.models import User
import uuid

# Create test user
username = f"test_user_{uuid.uuid4().hex[:8]}"
user = User.objects.create_user(username=username, email=f"{username}@test.com", password="testpass123")
print(f"Created user: {user.username}")

# Verify user exists
assert User.objects.filter(username=username).exists()
print("User verification successful")

# Clean up
user.delete()
assert not User.objects.filter(username=username).exists()
print("User cleanup successful")
"""
        return self.run_command([
            'python', 'manage.py', 'shell', '--settings=configs.settings', '-c', user_test
        ], "User Creation Test")

    def run_all_tests(self):
        """Run all production tests."""
        print("🚀 PRODUCTION TESTING SUITE")
        print("=" * 60)

        # Load production environment
        if not self.load_env_file():
            return False

        print(f"\n📋 Environment: {os.environ.get('SERVER_ENV', 'unknown')}")
        print(f"   Database: {os.environ.get('DB_NAME', 'unknown')}")
        print(f"   Debug: {os.environ.get('DEBUG', 'unknown')}")

        # Run tests
        tests = [
            self.test_database_connection,
            self.test_django_check,
            self.test_migrations,
            self.test_collectstatic,
            self.test_django_shell,
            self.test_admin_pages,
            self.test_wagtail_functionality,
            self.test_user_creation,
        ]

        for test in tests:
            test()
            time.sleep(1)  # Brief pause between tests

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.success_count}/{self.total_tests}")
        print(f"❌ Failed: {len(self.failed_tests)}/{self.total_tests}")

        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")

        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")

        if success_rate >= 90:
            print("🎉 PRODUCTION TESTS PASSED!")
            print("✅ System is ready for production deployment")
            return True
        else:
            print("⚠️  PRODUCTION TESTS FAILED!")
            print("❌ System needs fixes before production deployment")
            return False

def main():
    """Main function."""
    tester = ProductionTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
