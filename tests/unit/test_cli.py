"""Unit tests for cli.py — website aliases, env helpers, lock-SHA updater."""

import os
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the CLI module from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import cli  # noqa: E402

# ---------------------------------------------------------------------------
# _resolve
# ---------------------------------------------------------------------------

class TestResolve:
    def test_canonical_name_passes_through(self):
        assert cli._resolve("lms-demo") == "lms-demo"
        assert cli._resolve("ctc-research") == "ctc-research"
        assert cli._resolve("vresume") == "vresume"

    @pytest.mark.parametrize(
        "alias,expected",
        [
            ("ctc", "ctc-research"),
            ("ctc-website", "ctc-research"),
            ("ctc-research.com", "ctc-research"),
            ("structa", "lms-demo"),
            ("structa.cloud", "lms-demo"),
            ("lms", "lms-demo"),
            ("core", "lms-demo"),
            ("VResume", "vresume"),
            ("resume", "vresume"),
            ("vresume.structa.cloud", "vresume"),
        ],
    )
    def test_alias_resolves(self, alias, expected):
        assert cli._resolve(alias) == expected

    def test_unknown_website_exits(self):
        with pytest.raises(SystemExit) as exc_info:
            cli._resolve("nonexistent-site")
        assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# _website_env
# ---------------------------------------------------------------------------

class TestWebsiteEnv:
    def test_ctc_research_env(self):
        env = cli._website_env("ctc-research")
        assert env["DJANGO_SETTINGS_MODULE"] == "configs.settings"
        assert env["RUNNING_ENV"] == "docker"
        assert env["SERVER_ENV"] == "production"
        assert env["DB_NAME"] == "db_ctc"
        assert env["ALLOWED_HOSTS"] == "*"
        assert "DJANGO_SECRET_KEY" not in env

    def test_lms_demo_env(self):
        env = cli._website_env("lms-demo")
        assert env["DB_NAME"] == "db_structa"

    def test_vresume_env(self):
        env = cli._website_env("vresume")
        assert env["DB_NAME"] == "vresume"

    def test_unknown_website_gets_default_db(self):
        env = cli._website_env("unknown")
        assert env["DB_NAME"] == "db_ctc"

    def test_existing_env_vars_preserved(self):
        with patch.dict(os.environ, {"DB_HOST": "custom-host", "REDIS_URL": "redis://custom:6379"}):
            env = cli._website_env("lms-demo")
            assert env["DB_HOST"] == "custom-host"
            assert env["REDIS_URL"] == "redis://custom:6379"

    def test_django_secret_key_removed(self):
        with patch.dict(os.environ, {"DJANGO_SECRET_KEY": "secret123"}):
            env = cli._website_env("lms-demo")
            assert "DJANGO_SECRET_KEY" not in env


# ---------------------------------------------------------------------------
# WEBSITE_ALIASES / WEBSITES constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_all_aliases_resolve_to_known_websites(self):
        for alias, target in cli.WEBSITE_ALIASES.items():
            assert target in cli.WEBSITES, f"Alias '{alias}' → '{target}' not in WEBSITES"

    def test_websites_have_required_keys(self):
        for name, cfg in cli.WEBSITES.items():
            assert "compose" in cfg, f"{name} missing 'compose'"
            assert "port" in cfg, f"{name} missing 'port'"
            assert "container" in cfg, f"{name} missing 'container'"

    def test_website_ports_unique(self):
        ports = [cfg["port"] for cfg in cli.WEBSITES.values()]
        assert len(ports) == len(set(ports)), "Duplicate ports found"


# ---------------------------------------------------------------------------
# _local_check
# ---------------------------------------------------------------------------

class TestLocalCheck:
    def test_missing_main_py_returns_true(self, tmp_path):
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            assert cli._local_check("nonexistent") is True

    @patch("cli.subprocess.run")
    def test_successful_check(self, mock_run, tmp_path):
        site_dir = tmp_path / "test-site"
        site_dir.mkdir()
        (site_dir / "__main__.py").write_text("pass")
        mock_run.return_value = MagicMock(returncode=0)
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            assert cli._local_check("test-site") is True

    @patch("cli.subprocess.run")
    def test_failed_check(self, mock_run, tmp_path):
        site_dir = tmp_path / "test-site"
        site_dir.mkdir()
        (site_dir / "__main__.py").write_text("pass")
        mock_run.return_value = MagicMock(returncode=1)
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            assert cli._local_check("test-site") is False


# ---------------------------------------------------------------------------
# _container_check
# ---------------------------------------------------------------------------

class TestContainerCheck:
    @patch("cli.subprocess.run")
    def test_successful_container_check(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert cli._container_check("lms-demo") is True

    @patch("cli.subprocess.run")
    def test_failed_container_check(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1)
        assert cli._container_check("lms-demo") is False


# ---------------------------------------------------------------------------
# CLI class methods
# ---------------------------------------------------------------------------

class TestCLIMethods:
    @patch("cli._local_check", return_value=True)
    def test_check_exits_zero_on_success(self, mock_check):
        c = cli.CLI()
        with pytest.raises(SystemExit) as exc_info:
            c.check("lms-demo")
        assert exc_info.value.code == 0

    @patch("cli._local_check", return_value=False)
    def test_check_exits_one_on_failure(self, mock_check):
        c = cli.CLI()
        with pytest.raises(SystemExit) as exc_info:
            c.check("lms-demo")
        assert exc_info.value.code == 1

    @patch("cli._run")
    @patch("cli.subprocess.run")
    @patch("cli._local_check", return_value=True)
    @patch("cli._container_check", return_value=True)
    def test_deploy_happy_path(self, mock_cc, mock_lc, mock_subrun, mock_run):
        c = cli.CLI()
        c.deploy("lms-demo")
        assert mock_run.call_count >= 1

    @patch("cli._local_check", return_value=False)
    def test_deploy_aborts_on_local_check_failure(self, mock_lc):
        c = cli.CLI()
        with pytest.raises(SystemExit):
            c.deploy("lms-demo")

    @patch("cli._run")
    @patch("cli._container_check", return_value=False)
    @patch("cli._local_check", return_value=True)
    def test_deploy_aborts_on_container_check_failure(self, mock_lc, mock_cc, mock_run):
        c = cli.CLI()
        with pytest.raises(SystemExit):
            c.deploy("lms-demo")

    @patch("cli._run")
    def test_logs_command(self, mock_run):
        c = cli.CLI()
        c.logs("lms-demo", tail=10)
        mock_run.assert_called_once()
        args = mock_run.call_args
        assert "--tail=10" in args[0][0]

    @patch("cli._run")
    def test_logs_with_service(self, mock_run):
        c = cli.CLI()
        c.logs("lms-demo", service="web")
        args = mock_run.call_args[0][0]
        assert "web" in args

    @patch("cli._run")
    def test_down_command(self, mock_run):
        c = cli.CLI()
        c.down("lms-demo")
        args = mock_run.call_args[0][0]
        assert "down" in args
        assert "--remove-orphans" in args

    @patch("cli._run")
    def test_ps_command(self, mock_run):
        c = cli.CLI()
        c.ps()
        mock_run.assert_called_once()


# ---------------------------------------------------------------------------
# _update_lock_shas
# ---------------------------------------------------------------------------

class TestUpdateLockShas:
    def test_updates_sha_in_lock_file(self, tmp_path):
        lock_content = textwrap.dedent("""\
            [[package]]
            name = "django-osoul"
            source = { git = "https://github.com/mammhoud/django-osoul?branch=generic#aaaa" }
        """)
        # The regex expects 40-char hex SHAs
        old_sha = "a" * 40
        new_sha = "b" * 40
        lock_content = lock_content.replace("aaaa", old_sha)

        site_dir = tmp_path / "test-site"
        site_dir.mkdir()
        lock_file = site_dir / "uv.lock"
        lock_file.write_text(lock_content)

        c = cli.CLI()
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c._update_lock_shas({"django-osoul": new_sha})

        result = lock_file.read_text()
        assert new_sha in result
        assert old_sha not in result

    def test_no_lock_files_is_noop(self, tmp_path):
        c = cli.CLI()
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c._update_lock_shas({"django-osoul": "b" * 40})

    def test_unknown_lib_ignored(self, tmp_path):
        lock_content = "some content"
        site_dir = tmp_path / "test-site"
        site_dir.mkdir()
        lock_file = site_dir / "uv.lock"
        lock_file.write_text(lock_content)

        c = cli.CLI()
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c._update_lock_shas({"unknown-lib": "b" * 40})

        assert lock_file.read_text() == lock_content


# ---------------------------------------------------------------------------
# build_assets
# ---------------------------------------------------------------------------

class TestBuildAssets:
    @patch("cli.subprocess.run")
    def test_build_assets_skips_missing_manage_py(self, mock_run, tmp_path, capsys):
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c = cli.CLI()
            c.build_assets(website="lms-demo")
        mock_run.assert_not_called()

    @patch("cli.subprocess.run")
    def test_build_assets_runs_for_site_with_manage_py(self, mock_run, tmp_path):
        site_dir = tmp_path / "lms-demo"
        site_dir.mkdir()
        (site_dir / "manage.py").write_text("pass")
        mock_run.return_value = MagicMock(returncode=0)
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c = cli.CLI()
            c.build_assets(website="lms-demo")
        assert mock_run.call_count == 1

    @patch("cli.subprocess.run")
    def test_build_assets_exits_on_failure(self, mock_run, tmp_path):
        site_dir = tmp_path / "lms-demo"
        site_dir.mkdir()
        (site_dir / "manage.py").write_text("pass")
        mock_run.return_value = MagicMock(returncode=1)
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c = cli.CLI()
            with pytest.raises(SystemExit):
                c.build_assets(website="lms-demo")

    @patch("cli.subprocess.run")
    def test_build_assets_development_mode(self, mock_run, tmp_path):
        site_dir = tmp_path / "lms-demo"
        site_dir.mkdir()
        (site_dir / "manage.py").write_text("pass")
        mock_run.return_value = MagicMock(returncode=0)
        with patch.object(cli, "SCRIPT_DIR", tmp_path):
            c = cli.CLI()
            c.build_assets(website="lms-demo", production=False)
        cmd = mock_run.call_args[0][0]
        assert "--development" in cmd


# ---------------------------------------------------------------------------
# push
# ---------------------------------------------------------------------------

class TestPush:
    def test_push_unknown_lib_exits(self):
        c = cli.CLI()
        with pytest.raises((SystemExit, KeyError)):
            c.push(lib="nonexistent-lib")

    @patch("cli.subprocess.run")
    def test_push_no_changes_skips(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        c = cli.CLI()
        with patch.object(c, "_update_lock_shas"):
            c.push(lib="django-osoul")

    @patch("cli.subprocess.run")
    def test_push_with_changes(self, mock_run):
        def side_effect(cmd, **kwargs):
            result = MagicMock()
            if cmd == ["git", "status", "--porcelain"]:
                result.stdout = " M src/file.py"
                result.returncode = 0
            elif cmd == ["git", "diff", "--cached", "--quiet"]:
                result.returncode = 1  # staged changes exist
            elif cmd == ["git", "rev-parse", "HEAD"]:
                result.stdout = "a" * 40
                result.returncode = 0
            else:
                result.returncode = 0
                result.stdout = ""
            return result

        mock_run.side_effect = side_effect
        c = cli.CLI()
        with patch.object(c, "_update_lock_shas"):
            c.push(lib="django-osoul", message="test commit")


# ---------------------------------------------------------------------------
# main entrypoint
# ---------------------------------------------------------------------------

class TestMain:
    @patch("cli.fire.Fire")
    def test_main_calls_fire(self, mock_fire):
        cli.main()
        mock_fire.assert_called_once_with(cli.CLI)
