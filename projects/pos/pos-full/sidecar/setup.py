"""
Minimal setup.py shim for setuptools build.

Ensures shared/ (at projects/pos/shared/) is importable so that
[tool.setuptools.dynamic] can resolve version from shared.__about__.__version__.

Without this, setuptools can't find the shared module because it lives
outside the sidecar directory.
"""

import sys
from pathlib import Path

# Add projects/pos/ to sys.path so `import shared` works during build
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # pos/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from setuptools import setup  # noqa: E402

setup()
