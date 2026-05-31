"""Website configuration smoke tests."""

import json
from pathlib import Path

from django.test import SimpleTestCase, override_settings
from django.urls import reverse


ROOT = Path(__file__).resolve().parents[2]
WEBSITE_DIRS = {"ctc-research": "ctc-research", "lms-demo": "lms-demo", "vresume": "VResume"}
WEBSITES = tuple(WEBSITE_DIRS)
PROJECTS = tuple(WEBSITE_DIRS.values())


class WebsiteLayoutTests(SimpleTestCase):
    def test_each_project_has_makefile_and_assets_makefile(self):
        for project in PROJECTS:
            with self.subTest(project=project):
                assert (ROOT / project / "Makefile").exists()
                assert (ROOT / project / "assets" / "Makefile").exists()

    def test_each_website_has_local_settings_and_workspace_config(self):
        assert (ROOT / "configs" / "settings" / "conf.py").exists()
        assert (ROOT / "configs" / "site.py").exists()
        for website, directory in WEBSITE_DIRS.items():
            with self.subTest(website=website):
                assert (ROOT / directory / "settings.py").exists()

    def test_dummy_fixtures_are_split_by_app_and_model(self):
        for website, directory in WEBSITE_DIRS.items():
            fixture_root = ROOT / directory / "assets" / "fixtures"
            for relative in (
                "auth/user_dummy.json",
                "auth/group_dummy.json",
                "sites/site_dummy.json",
            ):
                with self.subTest(website=website, fixture=relative):
                    assert (fixture_root / relative).exists()


class RegistrationIntegrationTests(SimpleTestCase):
    def test_registration_compat_modules_exist_for_auth_login_invite_flows(self):
        for project in ("ctc-research", "lms-demo"):
            registration_root = ROOT / project / "plugins" / "accounts" / "registration"
            with self.subTest(project=project):
                assert (registration_root / "tokens.py").exists()
                assert (registration_root / "forms.py").exists()
                assert (registration_root / "views.py").exists()
                assert "RegistrationTokenGenerator" in (registration_root / "tokens.py").read_text()
                assert "PasswordCreationForm" in (registration_root / "forms.py").read_text()
                assert "assign_default_group" in (registration_root / "views.py").read_text()

    def test_registration_views_use_parent_account_modules(self):
        for project in ("ctc-research", "lms-demo"):
            source = (ROOT / project / "plugins" / "accounts" / "views" / "registration.py").read_text()
            with self.subTest(project=project):
                assert "from ..tokens import registration_token_generator" in source
                assert "from ..forms.registration import PasswordCreationForm, RegistrationForm" in source
                assert "from .tokens import" not in source
                assert "from .forms.registration import" not in source

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
        assert (ROOT / "VResume" / "assets" / "static" / "js" / "lib" / "dom.js").read_text().strip() == "// Shared DOM helpers live in the workspace assets package.\nexport { DOM, DOM as default } from 'shared/js/utility/dom.js';"
        assert (ROOT / "VResume" / "assets" / "static" / "js" / "lib" / "url.js").read_text().strip() == "// Shared URL tracking mixin lives in the workspace assets package.\nexport { URLTrackerMixin } from 'shared/js/utility/url.js';"
        assert "'@base'" in webpack_common
        for entry in ("ctc-app.js", "lms-app.js", "vresume-app.js"):
            assert entry in webpack_common

    def test_media_compose_uses_one_shared_media_server(self):
        compose = (ROOT / "compose" / "docker-compose.nginx.yml").read_text()
        nginx_conf = (ROOT / "compose" / "media" / "nginx.conf").read_text()
        assert "container_name: shared-media" in compose
        assert "container_name: ctc-media" not in compose
        assert "container_name: lms-media" not in compose
        assert "container_name: vresume-media" not in compose
        assert "../assets/media:/var/www/media:ro" in compose
        assert "assets/media:/var/www/sites" not in compose
        assert "location /media/" in nginx_conf
        assert "alias /var/www/media/;" in nginx_conf
        assert "location /sites/" in nginx_conf

    def test_compose_files_are_canonicalized(self):
        duplicate_compose_files = [
            ROOT / "ctc-research" / "docker-compose.yml",
            ROOT / "lms-demo" / "docker-compose.yml",
            ROOT / "lms-demo" / "docker-compose.proxy.yml",
            ROOT / "lms-demo" / "docker-compose.warehouse.yml",
        ]
        for path in duplicate_compose_files:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                assert not path.exists()
        assert (ROOT / "docker-compose.yml").exists()
        assert (ROOT / "compose" / "docker-compose.yml").exists()
        assert (ROOT / "compose" / "docker-compose.nginx.yml").exists()

    def test_assets_tooling_uses_local_webpack_cli_without_npx_prompt(self):
        workspace_cli = (ROOT / "assets" / "scripts" / "workspace.mjs").read_text()
        assets_makefile = (ROOT / "assets" / "Makefile").read_text()
        dockerfile = (ROOT / "compose" / "django" / "Dockerfile").read_text()
        assert "node_modules', '.bin'" in workspace_cli
        assert "Missing local webpack CLI" in workspace_cli
        assert "npx" not in workspace_cli
        assert "npm exec --no --" in assets_makefile
        assert "ci --include=dev" in assets_makefile
        assert "npm ci --include=dev" in dockerfile


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

    def test_populate_script_supports_all_sites_and_vresume_images(self):
        script = (ROOT / "tests" / "scripts" / "populate_site_data.py").read_text()
        assert 'if value == "all" or value.lower() == "all"' in script
        assert 'def selected_sites(site: str) -> list[str]:' in script
        assert 'if args.images or selected == "vresume"' in script

    def test_entrypoint_uses_safe_fixture_and_runtime_defaults(self):
        entrypoint = (ROOT / "compose" / "django" / "entrypoint").read_text()
        loader = (ROOT / "tests" / "scripts" / "load_dumped_data.py").read_text()
        populator = (ROOT / "tests" / "scripts" / "populate_site_data.py").read_text()
        assert 'LOAD_DUMP_ARGS+=("--force" "--include-dumps")' in entrypoint
        assert 'help setup_wagtail_home' in entrypoint
        assert 'setup_wagtail_home command is not installed' in entrypoint
        assert '${STRICT_ASSETS:-false}' in entrypoint
        assert '${STRICT_PAGE_CONTENT:-false}' in entrypoint
        assert 'parser.add_argument("--include-dumps"' in loader
        assert 'if include_dumps:' in loader
        assert 'directory / "auth" / "group_dummy.json"' in loader
        assert 'sorted(directory.rglob("*.json"))' not in loader
        assert 'parser.add_argument("--include-dumps"' in populator
        assert 'base / "dump-data.json"' in populator

    def test_setup_wagtail_home_is_idempotent_without_page_fixtures(self):
        for project in ("ctc-research", "lms-demo"):
            command = (ROOT / project / "www" / "core" / "management" / "commands" / "setup_wagtail_home.py").read_text()
            with self.subTest(project=project):
                assert "setup_wagtail_home skipped" in command
                assert 'Page.objects.filter(live=True, depth=2).order_by("path").first()' in command
                assert "CommandError" not in command


class AssetHealthTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF="tests.websites.urls")
    def test_asset_health_url_reverses(self):
        assert reverse("assets-health") == "/assets/health/"
