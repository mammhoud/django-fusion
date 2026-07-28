"""Shared task project smoke tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_shared_task_modules_import_without_celery_installed():
    from tasks.celery import app
    from tasks.content import get_users_count
    from tasks.email import send_bulk_email_task, send_email_raw, send_email_task

    assert app.main == "structa_shared_tasks"
    assert callable(get_users_count)
    assert callable(send_email_task)
    assert callable(send_bulk_email_task)
    assert callable(send_email_raw)


def test_website_task_modules_reexport_shared_tasks():
    import importlib.util

    task_file = (
        ROOT / "ctc-research" / "plugins" / "accounts" / "services" / "email" / "tasks.py"
    )
    spec = importlib.util.spec_from_file_location("ctc_email_tasks", task_file)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    from tasks.email import send_email_task

    assert module.send_email_task is send_email_task


def test_shared_tasks_compose_file_documents_worker_and_beat():
    compose_file = ROOT / "compose" / "docker-compose.tasks.yml"
    content = compose_file.read_text()
    assert "shared-tasks-worker" in content
    assert "celery -A tasks.celery:app worker" in content
    assert "shared-tasks-beat" in content
    assert "celery -A tasks.celery:app beat" in content
