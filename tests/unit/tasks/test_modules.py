"""Unit tests for the shared worker module registry."""

from plugins.workers.modules import TASK_MODULES


class TestBaseModulesConstants:
    def test_task_modules_is_list(self):
        assert isinstance(TASK_MODULES, tuple)

    def test_task_modules_contains_shared_actors(self):
        assert "plugins.workers.shared_email" in TASK_MODULES
        assert "plugins.workers.shared_content" in TASK_MODULES

    def test_all_entries_are_dotted_paths(self):
        for module_path in TASK_MODULES:
            assert "." in module_path
