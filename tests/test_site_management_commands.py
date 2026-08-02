"""Regression tests for reusable Fusion site management commands."""

from django.core.management.base import CommandError


def test_populate_content_parses_page_sections_and_translations():
    from django_fusion.management.commands.populate_content import (
        _extract_field_trans,
        _parse_md_to_dict,
    )

    content = """## 1. Home PAGE (HomePage)
- **Title**:
  - **en**: Welcome
  - **fr**: Bienvenue

## 2. About PAGE (AboutPage)
- **Title**: About us
"""

    pages = _parse_md_to_dict(content)

    assert set(pages) == {"HomePage", "AboutPage"}
    assert _extract_field_trans(pages["HomePage"])["Title"] == {
        "en": "Welcome",
        "fr": "Bienvenue",
    }
    assert _extract_field_trans(pages["AboutPage"])["Title"] == "About us"


def test_populate_content_requires_site_model_configuration():
    from django_fusion.management.commands.populate_content import Command

    command = Command()

    try:
        command.get_model_map()
    except CommandError as exc:
        assert "No page models configured" in str(exc)
    else:
        raise AssertionError("Unconfigured populate_content command should fail clearly")


def test_populate_courses_requires_site_model_configuration():
    from django_fusion.management.commands.populate_courses import Command

    command = Command()

    try:
        command._model("")
    except CommandError as exc:
        assert "requires site model configuration" in str(exc)
    else:
        raise AssertionError("Unconfigured populate_courses command should fail clearly")


def test_shared_commands_are_importable_and_have_command_classes():
    from django_fusion.management.commands import (
        populate_content,
        populate_courses,
        populate_homepage,
        send_bulk_emails,
        verify_content,
    )

    for module in (
        send_bulk_emails,
        verify_content,
        populate_content,
        populate_courses,
        populate_homepage,
    ):
        assert module.Command.help
