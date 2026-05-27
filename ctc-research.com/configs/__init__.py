"""Configs package shim for ctc-research.com

This small shim makes `from configs.settings import *` succeed by
re-exporting the top-level `settings.py` in the container image.
"""

__all__ = ["settings"]
