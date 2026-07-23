"""Backward-compatible re-export of the Unpoly request wrapper.

The implementation now lives in ``django_fusion.comp.fragment.plugins.unpoly``.
New code should import from there.
"""

from django_fusion.comp.fragment.plugins.unpoly import (  # noqa: F401
    Cache,
    Layer,
    Unpoly,
    header_to_opt,
    opt_to_header,
    opt_to_param,
    param_to_opt,
)

__all__ = [
    "Cache",
    "Layer",
    "Unpoly",
    "header_to_opt",
    "opt_to_header",
    "opt_to_param",
    "param_to_opt",
]
