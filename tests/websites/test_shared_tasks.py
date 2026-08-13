"""Shared task project smoke tests."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_shared_task_modules_import_without_celery_installed():
    from configs.tools.worker.celery import app

    assert app.main == "structa_shared_tasks"


def test_website_task_modules_reexport_shared_tasks():
    import importlib.util

    try:
        import dramatiq  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("dramatiq is not installed in this environment")

    task_file = (
        ROOT / "projects" / "precis" / "backend" / "apps" / "pages" / "accounts" / "management" / "services" / "email" / "tasks.py"
    )
    assert task_file.exists(), f"Expected task file at {task_file}"
    spec = importlib.util.spec_from_file_location("ctc_email_tasks", task_file)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    from configs.tools.worker.email import send_email_task

    assert module.send_email_task is send_email_task


def test_shared_tasks_compose_file_documents_worker_and_beat():
    compose_file = ROOT / "applications" / "compose" / "docker-compose.tasks.yml"
    content = compose_file.read_text()
    assert "shared-worker" in content
    assert "python lms-fusion/manage.py rundramatiq" in content
    assert "shared-scheduler" in content
    assert "celery -A configs.tools.worker.celery:app beat" in content
