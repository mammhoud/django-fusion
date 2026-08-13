"""Unit tests for www/worker/modules.py — constant definitions."""

from configs.tools.worker.modules import TASK_MODULES


class TestBaseModulesConstants:
    def test_task_modules_is_list(self):
        assert isinstance(TASK_MODULES, list)

    def test_task_modules_non_empty(self):
        assert len(TASK_MODULES) > 0

    def test_all_entries_are_dotted_paths(self):
        for module_path in TASK_MODULES:
            assert "." in module_path, f"Expected dotted path, got: {module_path}"
            assert module_path.startswith("ceptor_ai.")
