"""Unit tests for tasks/django_rseal.py — constant definitions."""

from tasks.django_rseal import DJANGO_RSEAL_TASK_MODULES


class TestDjangoRsealConstants:
    def test_task_modules_is_list(self):
        assert isinstance(DJANGO_RSEAL_TASK_MODULES, list)

    def test_task_modules_non_empty(self):
        assert len(DJANGO_RSEAL_TASK_MODULES) > 0

    def test_all_entries_are_dotted_paths(self):
        for module_path in DJANGO_RSEAL_TASK_MODULES:
            assert "." in module_path, f"Expected dotted path, got: {module_path}"
            assert module_path.startswith("django_rseal.")
