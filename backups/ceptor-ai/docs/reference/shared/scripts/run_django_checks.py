#!/usr/bin/env python3
"""
Django system checks for Phase 7.

Runs Django's built-in system checks to verify the project configuration.
"""

import os
import sys

import django
from django.core.management import call_command

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.development')

try:
    django.setup()
except Exception as e:
    print(f"Error setting up Django: {e}")
    print("\nNote: Full Django setup may not be available in this environment.")
    print("This is expected if dependencies are not fully installed.")
    sys.exit(1)


def run_system_checks():
    """Run Django system checks."""
    print("=" * 60)
    print("Django System Checks - Phase 7")
    print("=" * 60)

    try:
        print("\nRunning Django system checks...")
        call_command('check', verbosity=2)
        print("\n✓ All Django system checks passed!")
        return 0
    except SystemExit as e:
        if e.code == 0:
            print("\n✓ All Django system checks passed!")
            return 0
        else:
            print(f"\n✗ Django system checks failed with code {e.code}")
            return 1
    except Exception as e:
        print(f"\n✗ Error running Django system checks: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(run_system_checks())
