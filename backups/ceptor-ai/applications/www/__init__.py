"""Cross-site shared Django code.

This package holds HTTP/email helpers, redirect utilities, and other
behavior that is byte-identical (or trivially parameterizable) across
ctc-research, lms-demo, and VResume. Site-specific application trees
remain under ``applications/<site>/www/`` and plugins/.

Import from this package via the fully-qualified path
``applications.www.core.*`` to avoid being shadowed by the per-site
``www/`` package, which is added earlier on ``sys.path`` by each
site's ``settings.py``.
"""

from __future__ import annotations

__all__: list[str] = []
