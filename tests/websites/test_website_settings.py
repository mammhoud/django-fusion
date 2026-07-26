"""Website configuration smoke tests."""

import json
from pathlib import Path

import pytest
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


# tests/websites/ -> tests/ -> workspace root; canonical site files live under projects/.
REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = REPO_ROOT / "projects"
# Shared compose/proxy orchestration lives under applications/ in this monorepo.
COMPOSE_ROOT = REPO_ROOT / "applications" / "compose"
# Docker image build files live under projects/compose/.
CORE_COMPOSE_ROOT = ROOT / "compose"
PROXY_ROOT = REPO_ROOT / "applications" / "proxy"
# Sites were restructured: old core/{ctc-research,lms} → projects/lms/cms/,
# old core/VResume → projects/cms/portfolio/.
WEBSITE_DIRS = {"ctc-research": "lms/cms", "lms": "lms/cms", "vresume": "cms/portfolio"}
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
                    assert (fixture_root / relative).exists(), (
                        f"Missing fixture at {fixture_root / relative}"
                    )


class RegistrationIntegrationTests(SimpleTestCase):
    def test_registration_compat_modules_exist_for_auth_login_invite_flows(self):
        # ctc-research keeps registration helpers under plugins/accounts/{tokens,forms/registration,views/registration}
        # lms keeps them under plugins/accounts/registration/{tokens,forms,views}
        registration_roots = {
            "ctc-research": ROOT / "lms" / "cms" / "plugins" / "accounts",
            "lms": ROOT / "lms" / "cms" / "plugins" / "accounts",
        }
        forms_paths = {
            "ctc-research": registration_roots["ctc-research"] / "forms" / "registration.py",
            "lms": registration_roots["lms"] / "forms" / "registration.py",
        }
        views_paths = {
            "ctc-research": registration_roots["ctc-research"] / "views" / "registration.py",
            "lms": registration_roots["lms"] / "views" / "registration.py",
        }
        for project in ("ctc-research", "lms"):
            registration_root = registration_roots[project]
            with self.subTest(project=project):
                assert (registration_root / "tokens.py").exists()
                assert forms_paths[project].exists()
                assert views_paths[project].exists()
                assert "RegistrationTokenGenerator" in (registration_root / "tokens.py").read_text()
                assert "PasswordCreationForm" in forms_paths[project].read_text()
                assert "assign_default_group" in views_paths[project].read_text()

    def test_registration_views_use_parent_account_modules(self):
        for project in ("ctc-research", "lms"):
            source = (ROOT / "lms" / "cms" / "plugins" / "accounts" / "views" / "registration.py").read_text()
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
        assert (ROOT / "cms" / "portfolio" / "assets" / "static" / "js" / "lib" / "dom.js").read_text().strip() == "// Shared DOM helpers live in the workspace assets package.\nexport { DOM, DOM as default } from 'shared/js/utility/dom.js';"
        assert (ROOT / "cms" / "portfolio" / "assets" / "static" / "js" / "lib" / "url.js").read_text().strip() == "// Shared URL tracking mixin lives in the workspace assets package.\nexport { URLTrackerMixin } from 'shared/js/utility/url.js';"
        assert "'@base'" in webpack_common
        for entry in ("ctc-app.js", "lms-app.js", "vresume-app.js"):
            assert entry in webpack_common

    def test_media_compose_uses_one_shared_media_server(self):
        compose = (PROXY_ROOT / "docker-compose.nginx.yml").read_text()
        nginx_conf = (PROXY_ROOT / "nginx" / "default.conf").read_text()
        assert "container_name: shared-media" in compose
        assert "container_name: ctc-media" not in compose
        assert "container_name: lms-media" not in compose
        assert "container_name: vresume-media" not in compose
        assert "/var/www/media" in compose
        assert "location /media/" in nginx_conf
        assert "location /sites/" in nginx_conf

    def test_compose_files_are_canonicalized(self):
        # Per-site compose files now live under projects/<site>/; legacy duplicate
        # files at the old root locations should not exist.
        duplicate_compose_files = [
            REPO_ROOT / "ctc-research" / "docker-compose.yml",
            REPO_ROOT / "lms" / "docker-compose.yml",
            REPO_ROOT / "lms" / "docker-compose.proxy.yml",
            REPO_ROOT / "lms" / "docker-compose.warehouse.yml",
        ]
        for path in duplicate_compose_files:
            with self.subTest(path=path.relative_to(REPO_ROOT).as_posix()):
                assert not path.exists()
        # Root orchestration + shared task/proxy compose files
        assert (REPO_ROOT / "docker-compose.yml").exists()
        assert (COMPOSE_ROOT / "docker-compose.applications.yml").exists()
        assert (COMPOSE_ROOT / "docker-compose.tasks.yml").exists()
        assert (PROXY_ROOT / "docker-compose.nginx.yml").exists()

    def test_assets_tooling_uses_local_webpack_cli_without_npx_prompt(self):
        workspace_cli = (ROOT / "assets" / "scripts" / "workspace.mjs").read_text()
        assets_makefile = (ROOT / "assets" / "Makefile").read_text()
        dockerfile = (CORE_COMPOSE_ROOT / "Dockerfile").read_text()
        entrypoint = (CORE_COMPOSE_ROOT / "entrypoint").read_text()
        assert "node_modules', '.bin'" in workspace_cli
        assert "Missing local webpack CLI" in workspace_cli
        assert "npx" not in workspace_cli
        assert "npm exec --no --" in assets_makefile
        assert "ci --include=dev" in assets_makefile
        # The Dockerfile installs dependencies with npm ci --include=dev during the
        # asset-builder stage, which is expected; it does not run the workspace CLI.
        assert ".docker-image-data" not in dockerfile
        assert "BUILD_ASSETS_ON_START" in entrypoint
        assert "Skipping webpack build" in entrypoint

    def test_root_makefile_uses_canonical_compose_without_staged_image_data(self):
        makefile = (REPO_ROOT / "Makefile").read_text()
        compose_makefile = (COMPOSE_ROOT / "Makefile").read_text()
        runner = (REPO_ROOT / "tests" / "run_containers.sh").read_text()
        assert "COMPOSE_FILE" in makefile
        assert "WORKSPACE_ROOT" in makefile
        assert "deploy" in makefile
        assert "build-app" in makefile
        assert "prepare-image-data" not in makefile
        assert "clean-image-data" not in makefile
        assert ".docker-image-data" not in makefile
        assert ".docker-image-data" not in compose_makefile
        assert 'COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"' in runner
        assert 'SERVICE="ctc-research-website"' in runner

    def test_root_makefile_exposes_shared_build_targets_and_log_dirs(self):
        makefile = (ROOT / "Makefile").read_text()
        assert "docker-build-ctc" in makefile
        assert "docker-build-lms" in makefile
        assert "docker-build-vresume" in makefile
        assert "docker-build-shared-media" in makefile
        assert "docker-build-all" in makefile
        assert "LOG_BUILD_DIR" in makefile
        assert "LOG_DEPLOY_DIR" in makefile
        assert "logs/build" in makefile
        assert "logs/deploy" in makefile


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
        # Ports are declared per-site under projects/<site>/docker-compose.yml.
        # ctc-research and lms now share projects/lms/cms/docker-compose.yml,
        # so deduplicate by compose file path and verify unique ports.
        expected_ports = {"ctc-research": "5070", "lms": "5070", "vresume": "5072"}
        seen_compose = set()
        seen_ports = set()
        for site, port in expected_ports.items():
            compose_path = ROOT / WEBSITE_DIRS[site] / "docker-compose.yml"
            if compose_path in seen_compose:
                continue
            seen_compose.add(compose_path)
            assert port not in seen_ports, f"Duplicate port {port} across unique sites"
            seen_ports.add(port)
            with self.subTest(site=site, compose=compose_path.relative_to(ROOT).as_posix()):
                compose = compose_path.read_text()
                assert f'PORT: "{port}"' in compose

    def test_django_compose_mounts_specific_website_sources(self):
        # Per-site compose files live under projects/<site>/docker-compose.yml.
        # ctc-research and lms share the same compose file; deduplicate by
        # checking each unique file only once.
        _mount_dirs = {"ctc-research": "ctc-research", "vresume": "VResume"}
        _seen = set()
        for site, directory in WEBSITE_DIRS.items():
            compose_path = ROOT / directory / "docker-compose.yml"
            if compose_path in _seen:
                continue
            _seen.add(compose_path)
            with self.subTest(site=site, compose=compose_path.relative_to(ROOT).as_posix()):
                compose = compose_path.read_text()
                assert "../:/app:z" not in compose
                assert f"../{_mount_dirs[site]}:/app/{_mount_dirs[site]}:z" in compose
                assert "../assets:/app/assets:z" in compose

    def test_populate_script_uses_site_specific_fixture_directories(self):
        script = (REPO_ROOT / "tests" / "scripts" / "populate_site_data.py").read_text()
        assert 'for base in [site_dir / "assets" / "fixtures", root / "assets" / "fixtures"]:' in script

    def test_postgres_bootstrap_sql_includes_all_site_databases(self):
        # Legacy bootstrap SQL moved during monorepo restructuring; verify the
        # same databases are declared in the canonical databases compose file.
        compose = (REPO_ROOT / "applications" / "databases" / "docker-compose.yml").read_text()
        for database in ("db_ctc", "db_structa", "vresume"):
            with self.subTest(database=database):
                assert database in compose

    def test_populate_script_supports_all_sites_and_vresume_images(self):
        script = (REPO_ROOT / "tests" / "scripts" / "populate_site_data.py").read_text()
        assert 'if value == "all" or value.lower() == "all"' in script
        assert 'def selected_sites(site: str) -> list[str]:' in script
        assert 'if args.images or selected == "vresume"' in script

    def test_entrypoint_uses_safe_fixture_and_runtime_defaults(self):
        entrypoint = (CORE_COMPOSE_ROOT / "entrypoint").read_text()
        loader = (REPO_ROOT / "tests" / "scripts" / "load_dumped_data.py").read_text()
        populator = (REPO_ROOT / "tests" / "scripts" / "populate_site_data.py").read_text()
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
        # setup_wagtail_home is now handled by the shared entrypoint; per-site
        # management commands for it are no longer required.
        pytest.skip("setup_wagtail_home management command removed during monorepo restructuring")


class AssetHealthTests(SimpleTestCase):
    @override_settings(ROOT_URLCONF="tests.websites.urls")
    def test_asset_health_url_reverses(self):
        assert reverse("assets-health") == "/assets/health/"
