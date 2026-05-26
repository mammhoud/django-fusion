#!/usr/bin/env python3
"""
🎯 Django Management Command Runner
====================================
Unified manage.py that works with both websites.
Usage: python com.py <command> [options]
       WEBSITE=ctc-research.com python com.py <command>
"""

import os
import sys
from pathlib import Path

# Get website from environment
WEBSITE = os.environ.get("WEBSITE", "structa.cloud")

# Set up paths

SCRIPT_DIR = Path(__file__).resolve().parent
WEBSITE_DIR = SCRIPT_DIR / WEBSITE
WWW_DIR = WEBSITE_DIR / "www"

# Add website www to Python path
sys.path.insert(0, str(WWW_DIR))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")

# Run Django management command
if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    # Pass through all arguments except the script name
    execute_from_command_line(sys.argv)
