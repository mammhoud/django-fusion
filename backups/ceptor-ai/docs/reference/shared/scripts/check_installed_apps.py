#!/usr/bin/env python3
"""
Check installed apps in Django projects.
"""

import os
import sys


def check_ctc_research():
    """Check installed apps in ctc-research.com."""
    print("=== ctc-research.com ===")

    # Add project to path
    sys.path.insert(0, os.path.join(os.getcwd(), 'ctc-research.com'))

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.conf')

    try:
        import django
        django.setup()
        from django.conf import settings

        print(f"INSTALLED_APPS ({len(settings.INSTALLED_APPS)} total):")
        for app in settings.INSTALLED_APPS:
            print(f"  - {app}")

        # Check for handlers vs accounts
        print("\nChecking for app renames:")
        if 'apps.handlers' in settings.INSTALLED_APPS:
            print("  - handlers: FOUND (not renamed)")
        elif 'apps.accounts' in settings.INSTALLED_APPS:
            print("  - accounts: FOUND (renamed)")
        else:
            print("  - Neither handlers nor accounts found")

        if 'apps.pages' in settings.INSTALLED_APPS:
            print("  - pages: FOUND (not renamed)")
        elif 'apps.content' in settings.INSTALLED_APPS:
            print("  - content: FOUND (renamed)")
        else:
            print("  - Neither pages nor content found")

        if 'apps.LMS' in settings.INSTALLED_APPS or 'apps.lms' in settings.INSTALLED_APPS:
            lms_app = 'apps.LMS' if 'apps.LMS' in settings.INSTALLED_APPS else 'apps.lms'
            print(f"  - {lms_app}: FOUND")
        else:
            print("  - LMS/lms: NOT FOUND")

    except Exception as e:
        print(f"Error: {e}")

def check_structa_cloud():
    """Check installed apps in structa.cloud."""
    print("\n=== structa.cloud ===")

    # Add project to path
    sys.path.insert(0, os.path.join(os.getcwd(), 'structa.cloud'))

    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.conf')

    try:
        import django
        django.setup()
        from django.conf import settings

        print(f"INSTALLED_APPS ({len(settings.INSTALLED_APPS)} total):")
        for app in settings.INSTALLED_APPS:
            print(f"  - {app}")

        # Check for handlers vs accounts
        print("\nChecking for app renames:")
        if 'apps.handlers' in settings.INSTALLED_APPS:
            print("  - handlers: FOUND (not renamed)")
        elif 'apps.accounts' in settings.INSTALLED_APPS:
            print("  - accounts: FOUND (renamed)")
        else:
            print("  - Neither handlers nor accounts found")

        if 'apps.pages' in settings.INSTALLED_APPS:
            print("  - pages: FOUND (not renamed)")
        elif 'apps.content' in settings.INSTALLED_APPS:
            print("  - content: FOUND (renamed)")
        else:
            print("  - Neither pages nor content found")

        if 'apps.LMS' in settings.INSTALLED_APPS or 'apps.alliance' in settings.INSTALLED_APPS:
            lms_app = 'apps.LMS' if 'apps.LMS' in settings.INSTALLED_APPS else 'apps.alliance'
            print(f"  - {lms_app}: FOUND")
        else:
            print("  - LMS/alliance: NOT FOUND")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_ctc_research()
    check_structa_cloud()
