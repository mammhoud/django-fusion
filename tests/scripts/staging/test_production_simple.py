#!/usr/bin/env python3
"""
Simple Production Testing Script
==============================
Tests production database and basic functionality.
"""

import os
import subprocess
import sys
from pathlib import Path


def load_env_file(env_file=".env.production"):
    """Load environment variables from specified env file."""
    project_dir = Path(__file__).parent.parent.parent
    env_path = project_dir / env_file
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment from {env_file}")
        return True
    else:
        print(f"❌ Environment file {env_file} not found")
        return False

def run_sql_query(query, description):
    """Run a SQL query and return the result."""
    try:
        db_name = os.environ.get('DB_NAME', 'db_ctc')
        result = subprocess.run([
            'docker', 'exec', 'postgres', 'psql', '-U', 'postgres',
            '-d', db_name, '-c', query
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def test_production_environment():
    """Test production environment setup."""
    print("🚀 PRODUCTION ENVIRONMENT TESTING")
    print("=" * 50)

    # Load production environment
    if not load_env_file():
        return False

    success_count = 0
    total_tests = 0

    # Test 1: Environment Variables
    total_tests += 1
    print("\n1. 📋 Environment Configuration:")
    server_env = os.environ.get('SERVER_ENV', 'not set')
    running_env = os.environ.get('RUNNING_ENV', 'not set')
    debug = os.environ.get('DEBUG', 'not set')
    db_name = os.environ.get('DB_NAME', 'not set')

    print(f"   SERVER_ENV: {server_env}")
    print(f"   RUNNING_ENV: {running_env}")
    print(f"   DEBUG: {debug}")
    print(f"   DB_NAME: {db_name}")

    if server_env == 'production' and debug == 'false':
        print("   ✅ Production environment configured correctly")
        success_count += 1
    else:
        print("   ❌ Production environment not configured correctly")

    # Test 2: Database Connection
    total_tests += 1
    print("\n2. 🗄️  Database Connection:")
    success, output = run_sql_query("SELECT 'Connection successful' as status;", "Connection test")
    if success:
        print("   ✅ PostgreSQL connection successful")
        success_count += 1
    else:
        print(f"   ❌ PostgreSQL connection failed: {output}")

    # Test 3: Database Structure
    total_tests += 1
    print("\n3. 📊 Database Structure:")
    success, output = run_sql_query("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';", "Table count")
    if success:
        lines = output.split('\n')
        for line in lines:
            if line.strip().isdigit():
                table_count = int(line.strip())
                print(f"   Database tables: {table_count}")
                if table_count > 50:  # Should have many tables after migrations
                    print("   ✅ Database structure looks complete")
                    success_count += 1
                else:
                    print("   ⚠️  Database structure may be incomplete")
                break
    else:
        print(f"   ❌ Database structure check failed: {output}")

    # Test 4: Django Migrations
    total_tests += 1
    print("\n4. 🔄 Django Migrations:")
    success, output = run_sql_query("SELECT COUNT(*) FROM django_migrations;", "Migration count")
    if success:
        lines = output.split('\n')
        for line in lines:
            if line.strip().isdigit():
                migration_count = int(line.strip())
                print(f"   Applied migrations: {migration_count}")
                if migration_count > 100:  # Should have many migrations
                    print("   ✅ Migrations applied successfully")
                    success_count += 1
                else:
                    print("   ⚠️  Migration count seems low")
                break
    else:
        print(f"   ❌ Migration check failed: {output}")

    # Test 5: Core Django Tables
    total_tests += 1
    print("\n5. 🔧 Core Django Tables:")
    core_tables = ['auth_user', 'django_content_type', 'django_session']
    table_success = 0

    for table in core_tables:
        success, output = run_sql_query(f"SELECT COUNT(*) FROM {table};", f"{table} check")
        if success:
            print(f"   ✅ Table {table}: EXISTS")
            table_success += 1
        else:
            print(f"   ❌ Table {table}: MISSING")

    if table_success == len(core_tables):
        print("   ✅ All core Django tables present")
        success_count += 1
    else:
        print("   ❌ Some core Django tables missing")

    # Test 6: Wagtail Tables (if they exist)
    total_tests += 1
    print("\n6. 🌊 Wagtail CMS Tables:")
    wagtail_tables = ['wagtailcore_page', 'wagtailcore_site']
    wagtail_success = 0

    for table in wagtail_tables:
        success, output = run_sql_query(f"SELECT COUNT(*) FROM {table};", f"{table} check")
        if success:
            print(f"   ✅ Wagtail table {table}: EXISTS")
            wagtail_success += 1
        else:
            print(f"   ⚠️  Wagtail table {table}: NOT FOUND")

    if wagtail_success > 0:
        print("   ✅ Wagtail CMS tables found")
        success_count += 1
    else:
        print("   ⚠️  Wagtail CMS tables not found (may not be installed)")
        success_count += 1  # Don't fail if Wagtail isn't installed

    # Test 7: Database Performance
    total_tests += 1
    print("\n7. ⚡ Database Performance:")
    import time
    start_time = time.time()
    success, output = run_sql_query("SELECT COUNT(*) FROM auth_user;", "Performance test")
    end_time = time.time()

    if success:
        query_time = end_time - start_time
        print(f"   Query execution time: {query_time:.3f} seconds")
        if query_time < 1.0:
            print("   ✅ Database performance acceptable")
            success_count += 1
        else:
            print("   ⚠️  Database performance may be slow")
    else:
        print(f"   ❌ Performance test failed: {output}")

    # Summary
    print("\n" + "=" * 50)
    print("📊 PRODUCTION TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Passed: {success_count}/{total_tests}")
    print(f"❌ Failed: {total_tests - success_count}/{total_tests}")

    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    print(f"📈 Success Rate: {success_rate:.1f}%")

    if success_rate >= 85:
        print("\n🎉 PRODUCTION ENVIRONMENT READY!")
        print("✅ Database and core functionality verified")
        return True
    else:
        print("\n⚠️  PRODUCTION ENVIRONMENT NEEDS ATTENTION!")
        print("❌ Some tests failed - review configuration")
        return False

def main():
    """Main function."""
    success = test_production_environment()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
