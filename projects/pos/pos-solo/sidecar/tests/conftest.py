"""Pytest configuration for pos-full tests.

Registers the fixtures module so pytest can discover the `rust_db`
fixture without requiring explicit imports in test files."""

import os
import sys

# Ensure the sidecar directory is on sys.path for test module imports
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_THIS_DIR)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

pytest_plugins = ["tests.fixtures"]
