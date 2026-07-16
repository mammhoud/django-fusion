#!/usr/bin/env python3
"""
Test if we can run Django commands.
"""

import os
import sys

# Add ctc-research.com to path
sys.path.insert(0, os.path.join(os.getcwd(), 'ctc-research.com'))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings.development')

try:
    import django
    django.setup()
    print("✓ Django setup successful")

    from io import StringIO

    from django.core.management import call_command

    # Try to run showmigrations
    out = StringIO()
    call_command('showmigrations', stdout=out)
    output = out.getvalue()

    print("✓ Django command execution successful")
    print("\nFirst 500 chars of showmigrations output:")
    print(output[:500])

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
