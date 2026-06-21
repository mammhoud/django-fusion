"""Static package usage inventory for Structa Cloud websites."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProjectPackageUse:
    """Describe how a website should use shared packages."""

    website: str
    package: str
    usage: str


_PROJECT_USES: tuple[ProjectPackageUse, ...] = (
    ProjectPackageUse(
        website="ctc-research",
        package="django-rseal",
        usage="Django/Wagtail models, blocks, middleware, snippets, and service adapters.",
    ),
    ProjectPackageUse(
        website="lms-demo",
        package="django-rseal",
        usage="Shared Django/Wagtail automation when enabled by installed apps and plugins.",
    ),
    ProjectPackageUse(
        website="VResume",
        package="django-rseal",
        usage="Accounts plugin models, blocks, snippets, privacy middleware, and profile forms.",
    ),
    ProjectPackageUse(
        website="all-sites",
        package="crafts-ai",
        usage="Framework-agnostic AI, MCP, prompts, and import migration planning.",
    ),
)


def project_package_uses() -> tuple[ProjectPackageUse, ...]:
    """Return package usage records for documentation and CLI output."""
    return _PROJECT_USES
