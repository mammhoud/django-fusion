"""Tests for HTMX notification headers used by auth form handlers."""

import importlib.util
import json
from pathlib import Path

from django.http import HttpResponse


def test_trigger_notification_sets_htmx_header():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "ctc-research"
        / "plugins"
        / "accounts"
        / "services"
        / "notifications.py"
    )
    spec = importlib.util.spec_from_file_location("ctc_notifications", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    response = module.trigger_notification(
        HttpResponse("ok"), "Password set. You are signed in.", "success"
    )

    payload = json.loads(response["HX-Trigger"])
    assert payload == {
        "showNotification": {
            "message": "Password set. You are signed in.",
            "type": "success",
        }
    }
