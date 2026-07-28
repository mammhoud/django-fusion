"""Run the CRM site with: python -m crm"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

import django
django.setup()

from django.core.management import execute_from_command_line

execute_from_command_line(sys.argv)
