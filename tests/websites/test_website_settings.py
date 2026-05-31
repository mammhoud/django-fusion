"""Website configuration smoke tests."""

import json
from pathlib import Path

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


ROOT = Path(__file__).resolve().parents[2]
WEBSITES = ("ctc-research", "lms-demo")
PROJECTS = WEBSITES + ("VResume",)


class WebsiteLayoutTests(SimpleTestCase):
    def test_each_project_has_makefile_and_assets_makefile(self):
        for project in PROJECTS:
            with self.subTest(project=project):
                assert (ROOT / project / "Makefile").exists()
                assert (ROOT / project / "assets" / "Makefile").exists()

    def test_each_website_has_local_settings_and_workspace_config(self):
        assert (ROOT / "configs" / "settings" / "conf.py").exists()
        assert (ROOT / "configs" / "site.py").exists()
        for website in WEBSITES:
            with self.subTest(website=website):
                assert (ROOT / website / "settings.py").exists()

    def test_dummy_fixtures_are_split_by_app_and_model(self):
        for website in WEBSITES:
            fixture_root = ROOT / website / "assets" / "fixtures"
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
        workspace_cli = (ROOT / "assets" / "scripts" / "workspace.mjs").read_text()
        assert package["scripts"]["build"] == "node scripts/workspace.mjs build"
        assert "../webpack/main.config.js" in workspace_cli
        assert "node_modules" not in package["scripts"]["build"]

    def test_workspace_has_single_assets_package(self):
        package_files = sorted(path.relative_to(ROOT).as_posix() for path in ROOT.glob("*/package.json"))
        assert package_files == ["assets/package.json"]

    def test_assets_package_exposes_all_site_commands(self):
        package = json.loads((ROOT / "assets" / "package.json").read_text())
        scripts = package["scripts"]
        for key in ("build:assets", "build:ctc", "build:ctc-website", "build:structa", "build:vresume", "build:all", "collectstatic:all", "populate:all"):
            with self.subTest(script=key):
                assert key in scripts
                assert "scripts/workspace.mjs" in scripts[key]

    def test_project_makefiles_expose_main_asset_builds(self):
        for project in PROJECTS:
            with self.subTest(project=project):
                makefile = (ROOT / project / "Makefile").read_text()
                assert "build-assets" in makefile
                assert "main-assets" in makefile

    def test_webpack_exposes_base_alias_and_site_entries(self):
        webpack_common = (ROOT / "webpack" / "common.config.js").read_text()
        assert not (ROOT / "base").exists()
        assert (ROOT / "assets" / "static" / "js" / "base" / "utils" / "index.js").exists()
        assert "'@base'" in webpack_common
        for entry in ("ctc-app.js", "lms-app.js", "vresume-app.js"):
            assert entry in webpack_common

    def test_media_compose_uses_one_shared_media_server(self):
        compose = (ROOT / "compose" / "docker-compose.nginx.yml").read_text()
        assert "container_name: shared-media" in compose
        assert "container_name: ctc-media" not in compose
        assert "container_name: lms-media" not in compose
        assert "container_name: vresume-media" not in compose
        assert "../ctc-research/assets/media:/var/www/sites/ctc-research/media:ro" in compose
        assert "../lms-demo/assets/media:/var/www/sites/lms-demo/media:ro" in compose
        assert "../VResume/assets/media:/var/www/sites/vresume/media:ro" in compose


class SiteConfigTests(SimpleTestCase):
    def test_site_yaml_aliases_and_security_defaults(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("workspace_site_config", ROOT / "configs" / "site.py")
        site_module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(site_module)

        assert site_module._normalise_website("ctc") == "ctc-research"
        assert site_module.site_config("ctc")["module"] == "LMS"
        assert "ctc-research.com" in site_module.site_security_defaults("ctc")["ALLOWED_HOSTS"]

    def test_workspace_ports_are_unique_for_all_websites(self):
        compose = (ROOT / "compose" / "docker-compose.yml").read_text()
        expected_ports = {"ctc-research": "5070", "lms-demo": "5071", "vresume": "5072"}
        for site, port in expected_ports.items():
            with self.subTest(site=site):
                assert f"PORT: {port}" in compose
        assert len(set(expected_ports.values())) == len(expected_ports)

    def test_postgres_bootstrap_sql_includes_all_site_databases(self):
        sql = (ROOT / "compose" / "postgres" / "init.d" / "00-create-databases.sql").read_text()
        for database in ("db_ctc", "db_structa", "vresume"):
            with self.subTest(database=database):
                assert database in sql


class AssetHealthTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF="tests.websites.urls")
    def test_asset_health_url_reverses(self):
        assert reverse("assets-health") == "/assets/health/"
