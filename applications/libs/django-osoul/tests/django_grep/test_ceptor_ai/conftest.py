"""pytest plugin — make ``ceptor_ai`` importable from inside django-osoul's test tree.

Adds ``<monorepo-root>/libs/ceptor-ai/src`` to ``sys.path`` so the renamed
``tests/django_grep/test_ceptor_ai/test_ceptor_ai.py`` can run
``from ceptor_ai.<module> import ...`` without installing the package.

Scoped intentionally to this single subpackage. Extending django-osoul's
parent ``pyproject.toml`` ``pythonpath`` would leak a cross-library
dependency into every unrelated test under django-osoul.
"""
from __future__ import annotations

import sys
from pathlib import Path

# conftest.py lives at: applications/libs/django-osoul/tests/django_grep/test_ceptor_ai/conftest.py
# parents[0]=test_ceptor_ai/  [1]=django_grep/  [2]=tests/  [3]=django-osoul/  [4]=libs/
_SRC = Path(__file__).resolve().parents[4] / "ceptor-ai" / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
