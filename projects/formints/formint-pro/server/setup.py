"""
Minimal setup.py shim for setuptools build.

Ensures server directory is importable so that
[tool.setuptools.dynamic] can resolve version from __about__.__version__.
"""

import sys
from pathlib import Path

# Add server dir to sys.path so local imports work during build
_SERVER = Path(__file__).resolve().parent
if str(_SERVER) not in sys.path:
    sys.path.insert(0, str(_SERVER))

from setuptools import setup  # noqa: E402

setup()
