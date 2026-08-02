"""Regression tests for the safe LMS fixture loader."""

from __future__ import annotations

import io
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings


User = get_user_model()


@override_settings(ROOT_URLCONF="tests.urls")
class LoadDataCommandTests(TestCase):
    """Ensure loader preview mode and user handling are safe."""

    def test_dry_run_preserves_existing_content_by_default(self):
        output = io.StringIO()

        call_command("load_data", dry_run=True, stdout=output)

        rendered = output.getvalue()
        assert "Dry-run: ✅" in rendered
        assert "Replace existing content: ❌" in rendered
        assert "✅ (preserved)" in rendered
        assert "DRY RUN — no data was loaded" in rendered

    @patch.dict("os.environ", {}, clear=True)
    @patch("apps.core.management.commands.load_data.call_command")
    def test_existing_user_is_preserved_without_superuser_password(
        self, mocked_call_command
    ):
        existing = User.objects.create_user(
            username="admin",
            email="existing@example.com",
            password="existing-password",
        )

        call_command("load_data", stdout=io.StringIO())

        existing.refresh_from_db()
        assert User.objects.filter(username="admin").count() == 1
        assert existing.email == "existing@example.com"
        assert mocked_call_command.call_args_list
        fixture_call = mocked_call_command.call_args_list[0]
        assert fixture_call.args[0] == "loaddata"
        assert fixture_call.kwargs == {"verbosity": 0}
        assert fixture_call.args[1].endswith("assets/fixtures/dump-data.json")
