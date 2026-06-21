"""
Pytest configuration for django-osoul tests.
"""
import os
import sys
from pathlib import Path

# Add tests directory to path so fake_accounts can be found
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

# Add django-osoul src to path so the package can be imported
src_path = tests_dir.parent / "src"
sys.path.insert(0, str(src_path))

# Configure Django settings before importing Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django

django.setup()
