"""Unit tests for tasks/runtime.py — import_first and configure_django_for_website."""

import importlib
import importlib.util
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from www.worker.runtime import configure_django_for_website, import_first


def _make_findable_module(name, attrs=None):
    """Create a module with a proper __spec__ so find_spec works."""
    mod = types.ModuleType(name)
    mod.__spec__ = importlib.machinery.ModuleSpec(name, None)
    for k, v in (attrs or {}).items():
        setattr(mod, k, v)
    return mod


# ---------------------------------------------------------------------------
# import_first
# ---------------------------------------------------------------------------

class TestImportFirst:
    def test_returns_first_available_attr(self):
        mod = _make_findable_module("_fake_mod", {"MyClass": type("MyClass", (), {})})
        with patch.dict(sys.modules, {"_fake_mod": mod}):
            result = import_first(["_fake_mod.MyClass"])
        assert result is mod.MyClass

    def test_skips_missing_module(self):
        mod = _make_findable_module("_real_mod", {"Thing": "found"})
        with patch.dict(sys.modules, {"_real_mod": mod}):
            result = import_first([
                "_nonexistent_mod.Foo",
                "_real_mod.Thing",
            ])
        assert result == "found"

    def test_raises_import_error_when_all_missing(self):
        with pytest.raises(ImportError, match="No import path available"):
            import_first(["_no_such_a.Foo", "_no_such_b.Bar"])

    def test_skips_module_with_missing_attr(self):
        mod = _make_findable_module("_has_no_attr")
        with patch.dict(sys.modules, {"_has_no_attr": mod}):
            with pytest.raises(ImportError):
                import_first(["_has_no_attr.Missing"])

    def test_first_module_has_attr_second_skipped(self):
        mod_a = _make_findable_module("_mod_a", {"X": "first"})
        mod_b = _make_findable_module("_mod_b", {"X": "second"})
        with patch.dict(sys.modules, {"_mod_a": mod_a, "_mod_b": mod_b}):
            result = import_first(["_mod_a.X", "_mod_b.X"])
        assert result == "first"

    def test_empty_list_raises(self):
        with pytest.raises(ImportError, match="No import path available"):
            import_first([])


# ---------------------------------------------------------------------------
# configure_django_for_website
# ---------------------------------------------------------------------------

class TestConfigureDjangoForWebsite:
    @patch("www.worker.runtime.importlib.import_module")
    def test_configures_for_explicit_website(self, mock_import):
        mock_site = MagicMock()
        mock_site.active_website_name.return_value = "lms-demo"
        mock_site.site_dir_for.return_value = "/path/to/lms-demo"
        mock_site.WORKSPACE_DIR = "/path/to/workspace"

        mock_django = MagicMock()
        mock_apps = MagicMock()
        mock_apps.apps.ready = True

        def import_side_effect(name):
            if name == "configs.site":
                return mock_site
            if name == "django":
                return mock_django
            if name == "django.apps":
                return mock_apps
            raise ImportError(name)

        mock_import.side_effect = import_side_effect

        result = configure_django_for_website("lms-demo")
        assert result == "lms-demo"
        mock_site.active_website_name.assert_called_once()
        mock_site.configure_site_environment.assert_called_once_with("lms-demo")

    @patch.dict("os.environ", {}, clear=False)
    @patch("www.worker.runtime.importlib.import_module")
    def test_falls_back_to_default_website(self, mock_import):
        mock_site = MagicMock()
        mock_site.active_website_name.return_value = "ctc-research.com"
        mock_site.site_dir_for.return_value = "/path"
        mock_site.WORKSPACE_DIR = "/workspace"

        mock_django = MagicMock()
        mock_apps = MagicMock()
        mock_apps.apps.ready = True

        def import_side_effect(name):
            if name == "configs.site":
                return mock_site
            if name == "django":
                return mock_django
            if name == "django.apps":
                return mock_apps
            raise ImportError(name)

        mock_import.side_effect = import_side_effect

        # Remove env vars that would override the default
        for var in ("DJANGO_SITE", "DJANGO_WEBSITE", "WEBSITE"):
            import os
            os.environ.pop(var, None)

        result = configure_django_for_website(None)
        # Should use "ctc-research.com" as the default argument
        mock_site.active_website_name.assert_called_once()
