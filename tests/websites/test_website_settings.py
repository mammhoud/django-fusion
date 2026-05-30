"""Website configuration smoke tests."""

import json
from pathlib import Path

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


ROOT = Path(__file__).resolve().parents[2]
WEBSITES = ("ctc-research.com", "structa.cloud")


class WebsiteLayoutTests(SimpleTestCase):
    def test_each_website_has_local_and_wrapper_settings(self):
        for website in WEBSITES:
            with self.subTest(website=website):
                assert (ROOT / website / "settings.py").exists()
                assert (ROOT / website / "configs" / "settings.py").exists()
                assert (ROOT / "websites" / website / "settings.py").exists()
                assert (ROOT / "websites" / website / "configs" / "settings.py").exists()

    def test_dummy_fixtures_are_split_by_app_and_model(self):
        for website in WEBSITES:
            fixture_root = ROOT / "websites" / website / "assets" / "fixtures"
            for relative in (
                "auth/user_dummy.json",
                "auth/group_dummy.json",
                "sites/site_dummy.json",
            ):
                with self.subTest(website=website, fixture=relative):
                    assert (fixture_root / relative).exists()


class FrontendBuildLayoutTests(SimpleTestCase):
    def test_shared_assets_package_owns_node_modules_and_webpack_config(self):
        package = json.loads((ROOT / "assets" / "package.json").read_text())
        assert "../webpack/main.config.js" in package["scripts"]["build"]
        assert "node_modules" not in package["scripts"]["build"]

    def test_website_packages_delegate_to_base_assets_package(self):
        for website in WEBSITES:
            with self.subTest(website=website):
                package = json.loads((ROOT / website / "package.json").read_text())
                assert "npm --prefix ../assets run build" in package["scripts"]["build"]


class SiteConfigTests(SimpleTestCase):
    def test_site_yaml_aliases_and_security_defaults(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("workspace_site_config", ROOT / "configs" / "site.py")
        site_module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(site_module)

        assert site_module._normalise_website("ctc") == "ctc-research.com"
        assert site_module.site_config("ctc")["module"] == "LMS"
        assert "ctc-research.com" in site_module.site_security_defaults("ctc")["ALLOWED_HOSTS"]


class AssetHealthTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF="tests.websites.urls")
    def test_asset_health_url_reverses(self):
        assert reverse("assets-health") == "/assets/health/"
