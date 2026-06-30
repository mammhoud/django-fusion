"""Compatibility package for legacy ``ceptor_ai.blocks`` imports.

The Wagtail block implementations live in ``ceptor_ai.content.blocks``.  This
package keeps older website imports working while exposing the same package path
for nested modules such as ``ceptor_ai.blocks.media.gallery``.
"""

from __future__ import annotations

from pathlib import Path

__path__ = [str(Path(__file__).resolve().parent.parent / "content" / "blocks")]
