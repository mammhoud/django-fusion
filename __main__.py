#!/usr/bin/env python3
"""
🎯 Website CLI Entry Point
==========================
Imports settings from this website's www/configs/settings
"""

import sys
from pathlib import Path

# Add www to path for settings import
SCRIPT_DIR = Path(__file__).resolve().parent
WWW_DIR = SCRIPT_DIR / "www"
sys.path.insert(0, str(WWW_DIR))

# Set Django settings
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")

# Import and run CLI from unified location
if __name__ == "__main__":
    import fire
    from websites.cli import MainCLI
    fire.Fire(MainCLI)
