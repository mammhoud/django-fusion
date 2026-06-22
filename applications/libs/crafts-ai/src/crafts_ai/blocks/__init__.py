"""Compatibility package for legacy ``crafts_ai.blocks`` imports.

The Wagtail block implementations live in ``crafts_ai.content.blocks``.  This
package keeps older website imports working while exposing the same package path
for nested modules such as ``crafts_ai.blocks.media.gallery``.
"""

from __future__ import annotations

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "content" / "blocks")]
