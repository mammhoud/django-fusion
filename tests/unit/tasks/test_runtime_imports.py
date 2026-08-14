"""Tests for shared Dramatiq worker bootstrap imports."""

import os
import subprocess
import sys
from pathlib import Path


def test_runtime_configures_ctc_research_settings():
    repo_root = Path(__file__).resolve().parents[3]
    code = """
from plugins.workers.runtime import configure_django_for_website
selected = configure_django_for_website('ctc-research')
from django.conf import settings
print(selected)
print(settings.STATIC_ROOT)
"""
    env = os.environ.copy()
    env.pop("DJANGO_SETTINGS_MODULE", None)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "ctc-research" in result.stdout
    assert "ctc-research/assets/staticfiles" in result.stdout


def test_task_imports_are_available():
    from plugins.workers import TASK_MODULES

    assert "plugins.workers.email_tasks" in TASK_MODULES
