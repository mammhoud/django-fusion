"""Shared Dramatiq task project smoke tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_django_fusion_task_registry_supports_project_paths():
    from django_fusion.tasks.registry import TaskRegistry

    registry = TaskRegistry()
    assert hasattr(registry, "autodiscover")
    assert registry._import_project_path("projects/precis/landi/backend") is not None


def test_shared_tasks_compose_uses_dramatiq_and_excludes_lms():
    compose_file = ROOT / "applications" / "docker-compose.tasks.yml"
    content = compose_file.read_text()

    assert "shared-worker" in content
    assert "shared-scheduler" in content
    assert "python manage.py rundramatiq" in content
    assert "django_fusion.tasks.scheduler" in content
    assert "FUSION_TASK_PROJECT_PATHS" in content
    assert "precis-lms/manage.py" not in content
    assert "celery -A" not in content
    assert "--queues shared,email,content,system,crm,marketing,finance,default" in content
    assert "temporalio" not in content
    assert "celery" not in content.lower()


def test_temporal_campaign_worker_is_migrated_to_dramatiq_plugins():
    worker = ROOT / "projects" / "precis" / "backend" / "plugins" / "workers" / "campaign_tasks.py"
    command = ROOT / "projects" / "precis" / "backend" / "apps" / "core" / "management" / "commands" / "run_campaign_worker.py"
    temporal_package = ROOT / "projects" / "precis" / "backend" / "apps" / "domain" / "workflows" / "temporal"

    assert worker.exists()
    assert "from django_fusion.tasks import task" in worker.read_text()
    assert "temporalio" not in worker.read_text()
    assert not command.exists()
    assert not temporal_package.exists()


def test_full_project_make_targets_exclude_lms_from_aggregates():
    makefile = (ROOT / "projects" / "Makefile").read_text()

    assert "check WEBSITE=precis-main" in makefile
    assert "check WEBSITE=loop-crm" in makefile
    assert "Building lms" not in makefile
    assert "for website in precis-main loop-crm" in makefile
