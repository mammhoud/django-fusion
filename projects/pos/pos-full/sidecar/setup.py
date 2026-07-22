"""
Minimal setup.py shim for setuptools build.

Ensures sidecar directory is importable so that
[tool.setuptools.dynamic] can resolve version from __about__.__version__.
"""

import sys
from pathlib import Path

# Add sidecar dir to sys.path so local imports work during build
_SIDECAR = Path(__file__).resolve().parent
if str(_SIDECAR) not in sys.path:
    sys.path.insert(0, str(_SIDECAR))

from setuptools import setup  # noqa: E402

setup()
