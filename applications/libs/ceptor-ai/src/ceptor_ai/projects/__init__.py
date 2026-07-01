"""Compatibility shim — ``ceptor_ai.projects`` is now ``ceptor_ai.tools.inventory``.

Import from the canonical path instead::

    from ceptor_ai.tools.inventory import ProjectPackageUse, project_package_uses
"""
from __future__ import annotations
from ceptor_ai.tools.inventory import ProjectPackageUse, project_package_uses  # noqa: F401
from ceptor_ai.tools.inventory.projects import project_package_uses  # noqa: F401

__all__ = ["ProjectPackageUse", "project_package_uses"]
