"""pytest plugin — make ``ceptor_ai`` importable from inside django-fusion's test tree.

Adds ``<monorepo-root>/libs/ceptor-ai/src`` to ``sys.path`` so the renamed
``tests/django_grep/test_ceptor_ai/test_ceptor_ai.py`` can run
``from ceptor_ai.<module> import ...`` without installing the package.

Scoped intentionally to this single subpackage. Extending django-fusion's
parent ``pyproject.toml`` ``pythonpath`` would leak a cross-library
dependency into every unrelated test under django-fusion.
"""
from __future__ import annotations

import sys
from pathlib import Path

# conftest.py lives at: applications/libs/django-fusion/tests/django_grep/test_ceptor_ai/conftest.py
# parents[0]=test_ceptor_ai/  [1]=django_grep/  [2]=tests/  [3]=django-fusion/  [4]=libs/
_SRC = Path(__file__).resolve().parents[4] / "ceptor-ai" / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
