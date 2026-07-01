"""Project and workspace inventory utilities.

Scans the monorepo to discover how each site uses the shared packages.

Usage::

    from ceptor_ai.tools.inventory import ProjectPackageUse, project_package_uses
"""

from .projects import ProjectPackageUse, project_package_uses

__all__ = ["ProjectPackageUse", "project_package_uses"]
