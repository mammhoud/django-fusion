#!/usr/bin/env python3
"""
Core site management logic for the multi‑site Django monorepo.

Provides:
  - Site resolution (--site flag, env vars, aliases)
  - Environment setup for Django and Docker
  - Utility commands: deploy, logs, push, test, make, etc.
  - Local and container checks using __main__.py
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# ----------------------------------------------------------------------
#  Configuration
# ----------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
ROOT_COMPOSE = REPO_ROOT / "docker-compose.yml"

SITES = {
    "ctc-research": {
        "path": "ctc-research",
        "project_path": "ctc-research",
        "service": "ctc-research-website",
        "port": 5070,
        "db_name": "db_ctc",
    },
    "lms-demo": {
        "path": "lms-demo",
        "project_path": "lms-demo",
        "service": "lms-demo-website",
        "port": 5071,
        "db_name": "db_structa",
    },
    "vresume": {
        "path": "VResume",
        "project_path": "VResume",
        "service": "vresume-website",
        "port": 5072,
        "db_name": "vresume",
    },
}

SITE_ALIASES = {
    "ctc": "ctc-research",
    "ctc-research": "ctc-research",
    "ctc-research.com": "ctc-research",
    "ctc-website": "ctc-research",
    "structa": "lms-demo",
    "structa.cloud": "lms-demo",
    "core": "lms-demo",
    "lms": "lms-demo",
    "lms-demo": "lms-demo",
    "resume": "vresume",
    "vresume": "vresume",
    "vresume.structa.cloud": "vresume",
    "VResume": "vresume",
}

LIBS = {
    "django-osoul": REPO_ROOT / "libs" / "django-osoul",
    "crafts-ai": REPO_ROOT / "libs" / "crafts-ai",
}

SKIPPED_MAKE_TARGETS = {
    "deploy",
    "docker-clean",
    "docker-clean-all",
    "docker-deploy",
    "docker-deploy-full",
    "docker-down",
    "docker-prune-containers",
    "docker-prune-data",
    "docker-redeploy",
    "docker-rebuild",
    "docker-restart-all",
    "docker-start-all",
    "docker-stop-all",
    "docker-up",
    "redeploy",
    "rebuild",
}


# ----------------------------------------------------------------------
#  Core class
# ----------------------------------------------------------------------
class SiteCLI:
    """Main controller for site‑aware operations."""

    def __init__(self, site: Optional[str] = None) -> None:
        """
        Initialize with an optional site name.
        If not provided, it will be resolved later.
        """
        self._site: Optional[str] = site
        self._site_config: Optional[Dict] = None

    @property
    def site(self) -> str:
        """Resolve and return the canonical site name."""
        if self._site is None:
            self._site = self.resolve_site()
        return self._site

    @property
    def config(self) -> Dict:
        """Return the configuration dict for the current site."""
        if self._site_config is None:
            self._site_config = SITES[self.site]
        return self._site_config

    # ------------------------------------------------------------------
    #  Resolution and environment
    # ------------------------------------------------------------------
    @classmethod
    def resolve_site(cls, site_arg: Optional[str] = None) -> str:
        """Resolve site from CLI argument, env vars, or default."""
        requested = (
            site_arg
            or os.environ.get("DJANGO_SITE")
            or os.environ.get("DJANGO_WEBSITE")
            or os.environ.get("WEBSITE")
            or os.environ.get("SITE")
            or "ctc-research"
        )
        resolved = SITE_ALIASES.get(requested.lower(), requested)
        if resolved not in SITES:
            choices = ", ".join(sorted(set(SITES) | set(SITE_ALIASES)))
            raise SystemExit(f"Unknown site '{requested}'. Choose from: {choices}")
        return resolved

    def site_env(self) -> Dict[str, str]:
        """Return a complete environment dict for the current site."""
        cfg = self.config
        env = os.environ.copy()
        env.update(
            {
                "DJANGO_SITE": self.site,
                "DJANGO_WEBSITE": self.site,
                "WEBSITE": self.site,
                "WEBSITE_NAME": self.site,
                "PROJECT_PATH": cfg["project_path"],
                "DJANGO_WEBSITE_DIR": str(REPO_ROOT / cfg["path"]),
                "WEBSITE_DIR": str(REPO_ROOT / cfg["path"]),
                "DB_NAME": env.get("DB_NAME", cfg["db_name"]),
                "DJANGO_SETTINGS_MODULE": "settings",
                "ALLOWED_HOSTS": "*",
            }
        )
        env.pop("DJANGO_SECRET_KEY", None)  # read from file in production
        return env

    def configure_django(self) -> None:
        """Set up sys.path and environment so Django can run for this site."""
        cfg = self.config
        site_dir = REPO_ROOT / cfg["path"]
        if not site_dir.exists():
            raise SystemExit(f"Site directory not found: {site_dir}")

        for path in (site_dir / "www", site_dir, REPO_ROOT):
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)

        os.environ.update(self.site_env())
        print(f"Using site '{self.site}' (site path: {site_dir})", file=sys.stderr)

    # ------------------------------------------------------------------
    #  Helpers (run, pop site arg)
    # ------------------------------------------------------------------
    @staticmethod
    def _run(
        cmd: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """Run a command, print it to stderr."""
        print(f"+ {cmd}", file=sys.stderr)
        return subprocess.run(
            cmd, cwd=str(cwd or REPO_ROOT), env=env, check=check
        )

    @staticmethod
    def pop_site_arg(argv: List[str]) -> Optional[str]:
        """Remove --site argument from argv and return its value."""
        for idx, arg in enumerate(argv[1:], start=1):
            if arg.startswith("--site="):
                value = arg.split("=", 1)[1]
                del argv[idx]
                return value
            if arg == "--site" and idx + 1 < len(argv):
                value = argv[idx + 1]
                del argv[idx : idx + 2]
                return value
        return None

    # ------------------------------------------------------------------
    #  Site‑specific checks
    # ------------------------------------------------------------------
    def local_check(self) -> bool:
        """Run `python <site>/__main__.py check` locally."""
        main_py = REPO_ROOT / self.config["path"] / "__main__.py"
        if not main_py.exists():
            print(f"⚠️  No __main__.py found at {main_py}, skipping local check")
            return True

        venv_python = REPO_ROOT / ".venv" / "bin" / "python"
        python = str(venv_python) if venv_python.exists() else sys.executable
        site_dir = REPO_ROOT / self.config["path"]
        env = self.site_env()

        print(f"\n🔍 Running local Django check via {self.site}/__main__.py ...")
        result = subprocess.run(
            [python, str(main_py), "check"],
            cwd=str(site_dir),
            env=env,
            capture_output=False,
        )
        if result.returncode != 0:
            print(f"❌ Local check FAILED for {self.site}")
            return False
        print(f"✅ Local check PASSED for {self.site}")
        return True

    def container_check(self) -> bool:
        """Run `manage.py check` inside the built container."""
        image = self.config["service"]
        env = self.site_env()

        print(f"\n🔍 Running container Django check on service '{image}' ...")
        cmd = [
            "docker",
            "compose",
            "-f",
            str(ROOT_COMPOSE),
            "run",
            "--rm",
            "-e",
            f"DJANGO_SETTINGS_MODULE={env['DJANGO_SETTINGS_MODULE']}",
            "-e",
            "RUNNING_ENV=docker",
            "-e",
            "SERVER_ENV=production",
            "-e",
            "DB_HOST=postgres",
            "-e",
            f"DB_NAME={env['DB_NAME']}",
            "-e",
            "REDIS_URL=redis://redis:6379/0",
            "-e",
            f"ALLOWED_HOSTS={env['ALLOWED_HOSTS']}",
            image,
            "python",
            "manage.py",
            "--site",
            self.site,
            "check",
        ]
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"❌ Container check FAILED for {self.site}")
            return False
        print(f"✅ Container check PASSED for {self.site}")
        return True

    # ------------------------------------------------------------------
    #  Utility commands
    # ------------------------------------------------------------------
    def sites(self, args: List[str]) -> int:
        """List all sites with their paths, services, and aliases."""
        parser = argparse.ArgumentParser(prog="sites")
        parser.parse_args(args)
        for name, cfg in SITES.items():
            aliases = sorted(
                alias for alias, target in SITE_ALIASES.items()
                if target == name and alias != name
            )
            print(
                f"{name:13} path={cfg['path']:12} service={cfg['service']:22} "
                f"port={cfg['port']} aliases={', '.join(aliases)}"
            )
        return 0

    def make(self, args: List[str]) -> int:
        """Run a make target for the current site."""
        parser = argparse.ArgumentParser(prog="make")
        parser.add_argument("target", nargs="?", default="help")
        parser.add_argument("make_args", nargs=argparse.REMAINDER)
        parsed = parser.parse_args(args)
        cmd = ["make", parsed.target, f"WEBSITE={self.site}", *parsed.make_args]
        return self._run(cmd, env=self.site_env(), check=False).returncode

    def make_check(self, args: List[str]) -> int:
        """Dry‑run all make targets (or only safe ones) to validate them."""
        parser = argparse.ArgumentParser(prog="make-check")
        parser.add_argument("--all", action="store_true", help="Include destructive targets")
        parsed = parser.parse_args(args)

        # Get list of targets
        result = subprocess.run(
            ["make", "show-targets"],
            cwd=str(REPO_ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            raise SystemExit(result.stdout)
        targets = [line.strip() for line in result.stdout.splitlines() if line.strip()]

        failures = []
        for target in targets:
            if not parsed.all and target in SKIPPED_MAKE_TARGETS:
                continue
            result = subprocess.run(
                ["make", "--dry-run", target, f"WEBSITE={self.site}"],
                cwd=str(REPO_ROOT),
                env=self.site_env(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            if result.returncode != 0:
                failures.append(f"{target}: {result.stdout.strip()}")

        compose_result = self._run(
            ["docker", "compose", "-f", str(ROOT_COMPOSE), "config", "--quiet"],
            check=False,
        )
        if compose_result.returncode != 0:
            failures.append("docker compose config failed")

        if failures:
            print("\nMake command validation failed:", file=sys.stderr)
            for failure in failures:
                print(f"- {failure}", file=sys.stderr)
            return 1
        print("Make command dry-run validation and compose config completed without errors.")
        return 0

    def check_sites(self, args: List[str]) -> int:
        """Run Django system check on one or more sites."""
        parser = argparse.ArgumentParser(prog="check-sites")
        parser.add_argument("sites", nargs="*", default=list(SITES))
        parsed = parser.parse_args(args)
        failed = []
        for site_name in parsed.sites:
            site = self.resolve_site(site_name)
            cli = SiteCLI(site)
            cli.configure_django()
            result = self._run(
                [sys.executable, str(REPO_ROOT / "manage.py"), "check"],
                env=cli.site_env(),
                check=False,
            )
            if result.returncode != 0:
                failed.append(site)
        if failed:
            print(f"Failed site checks: {', '.join(failed)}", file=sys.stderr)
            return 1
        return 0

    def deploy(self, args: List[str]) -> int:
        """Build, check, and deploy the current site."""
        parser = argparse.ArgumentParser(prog="deploy")
        parser.add_argument("--no-cache", action="store_true")
        parser.add_argument("--skip-local-check", action="store_true")
        parser.add_argument("--skip-container-check", action="store_true")
        parsed = parser.parse_args(args)
        cfg = self.config

        if not parsed.skip_local_check:
            if not self.local_check():
                print("\n💥 Aborting deploy — local check failed.", file=sys.stderr)
                return 1

        build_cmd = ["docker", "compose", "-f", str(ROOT_COMPOSE), "build"]
        if parsed.no_cache:
            build_cmd.append("--no-cache")
        build_cmd.append(cfg["service"])
        print(f"\n🏗️  Building {self.site} ...")
        result = self._run(build_cmd, check=False)
        if result.returncode != 0:
            return result.returncode

        if not parsed.skip_container_check:
            if not self.container_check():
                print("\n💥 Aborting deploy — container check failed.", file=sys.stderr)
                return 1

        print(f"\n🚀 Deploying {self.site} ...")
        result = self._run(
            ["docker", "compose", "-f", str(ROOT_COMPOSE), "up", "-d", "--build", cfg["service"]],
            check=False,
        )
        if result.returncode == 0:
            print(f"\n✅ {self.site} deployed. Health: http://localhost:{cfg['port']}/health/")
        return result.returncode

    def logs(self, args: List[str]) -> int:
        """Show container logs for the current site."""
        parser = argparse.ArgumentParser(prog="logs")
        parser.add_argument("--tail", default="100")
        parser.add_argument("--service", help="Specific service name (optional)")
        parsed = parser.parse_args(args)
        cfg = self.config
        cmd = ["docker", "compose", "-f", str(ROOT_COMPOSE), "logs", f"--tail={parsed.tail}"]
        if parsed.service:
            cmd.append(parsed.service)
        else:
            cmd.append(cfg["service"])
        return self._run(cmd, check=False).returncode

    def down(self, args: List[str]) -> int:
        """Stop and remove containers for the current site (or all if no site set)."""
        parser = argparse.ArgumentParser(prog="down")
        parser.add_argument("--all", action="store_true", help="Stop all sites (ignores current site)")
        parsed = parser.parse_args(args)
        if parsed.all:
            cmd = ["docker", "compose", "-f", str(ROOT_COMPOSE), "down", "--remove-orphans"]
        else:
            cmd = [
                "docker",
                "compose",
                "-f",
                str(ROOT_COMPOSE),
                "down",
                "--remove-orphans",
                self.config["service"],
            ]
        return self._run(cmd, check=False).returncode

    def ps(self, args: List[str]) -> int:
        """Show status of website containers."""
        parser = argparse.ArgumentParser(prog="ps")
        parser.parse_args(args)
        filters = [f"--filter=name={cfg['service']}" for cfg in SITES.values()]
        cmd = ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"] + filters
        return self._run(cmd, check=False).returncode

    def build_assets(self, args: List[str]) -> int:
        """Build static assets (webpack + collectstatic) for a site."""
        parser = argparse.ArgumentParser(prog="build-assets")
        parser.add_argument("--production", action="store_true", default=True)
        parser.add_argument("--development", action="store_true")
        parser.add_argument("--clean", action="store_true")
        parsed = parser.parse_args(args)

        production = parsed.production if not parsed.development else False
        site_dir = REPO_ROOT / self.config["path"]
        manage_py = site_dir / "manage.py"
        if not manage_py.exists():
            print(f"⚠️  No manage.py found at {site_dir}, skipping")
            return 1

        print(f"\n🔨 Building assets for {self.site}...")
        venv_python = site_dir / ".venv" / "bin" / "python"
        python = str(venv_python) if venv_python.exists() else sys.executable

        cmd = [python, str(manage_py), "build_assets"]
        if production:
            cmd.append("--production")
        else:
            cmd.append("--development")
        if parsed.clean:
            cmd.append("--clean")
        cmd.append("--no-input")

        result = subprocess.run(cmd, cwd=str(site_dir), capture_output=False)
        if result.returncode != 0:
            print(f"❌ Asset build failed for {self.site}")
            return 1
        print(f"✅ Assets built for {self.site}")
        return 0

    def test(self, args: List[str]) -> int:
        """Run tests against running containers."""
        parser = argparse.ArgumentParser(prog="test")
        parser.add_argument("--live", action="store_true", help="Use live domains")
        parsed = parser.parse_args(args)

        script = REPO_ROOT / "tests" / "scripts" / "run_container_tests.sh"
        env = self.site_env()
        if parsed.live:
            env["USE_LIVE_DOMAINS"] = "1"

        # Container-level tests
        print(f"\n🧪 Running container tests for: {self.site}")
        result = self._run(["bash", str(script), self.site], env=env, check=False)
        if result.returncode != 0:
            return result.returncode

        # HTTP integration tests
        print("\n🌐 Running HTTP integration tests ...")
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_sites.py",
            "-v",
            "--tb=short",
            "--no-header",
        ]
        result = subprocess.run(pytest_cmd, cwd=str(REPO_ROOT), env=env, check=False)
        if result.returncode != 0:
            print("❌ HTTP tests failed", file=sys.stderr)
            return result.returncode
        print("✅ All tests passed")
        return 0

    def _update_lock_shas(self, pushed: Dict[str, str]) -> None:
        """Update commit SHAs in all uv.lock files for pushed libs."""
        lock_files = list(REPO_ROOT.glob("*/uv.lock"))
        if not lock_files:
            return

        repo_map = {
            "django-osoul": "django-osoul",
            "crafts-ai": "crafts-ai",
        }

        for lock_path in lock_files:
            content = lock_path.read_text()
            original = content

            for lib_name, new_sha in pushed.items():
                repo = repo_map.get(lib_name)
                if not repo:
                    continue
                pattern = rf'(git = "https://github\.com/mammhoud/{re.escape(repo)}\?branch=generic#)[0-9a-f]{{40}}'
                content = re.sub(pattern, rf'\g<1>{new_sha}', content)

            if content != original:
                lock_path.write_text(content)
                print(f"  📝 Updated {lock_path.relative_to(REPO_ROOT)}")

    def push(self, args: List[str]) -> int:
        """Commit and push local lib changes to GitHub, update uv.lock SHAs."""
        parser = argparse.ArgumentParser(prog="push")
        parser.add_argument("--lib", default="all", help="Library name or 'all'")
        parser.add_argument("--message", default="", help="Commit message")
        parser.add_argument("--branch", default="generic", help="Target branch")
        parsed = parser.parse_args(args)

        if parsed.lib != "all" and parsed.lib not in LIBS:
            print(f"❌ Unknown lib '{parsed.lib}'. Choose: {', '.join(LIBS)} or 'all'", file=sys.stderr)
            return 1

        targets = {parsed.lib: LIBS[parsed.lib]} if parsed.lib != "all" else LIBS
        pushed: Dict[str, str] = {}

        for name, path in targets.items():
            print(f"\n📦 Processing {name} at {path} ...")

            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(path),
                capture_output=True,
                text=True,
                check=False,
            )
            if not status.stdout.strip():
                print(f"  ✓ No changes in {name}, skipping.")
                continue

            subprocess.run(["git", "add", "-u"], cwd=str(path), check=True)
            subprocess.run(["git", "add", "src/"], cwd=str(path), check=False)

            commit_msg = parsed.message or f"chore({name}): sync local changes to {parsed.branch}"
            staged = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=str(path))
            if staged.returncode == 0:
                print(f"  ✓ Nothing staged in {name}, skipping commit.")
                continue

            subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(path), check=True)
            print(f"  🚀 Pushing {name} → origin/{parsed.branch} ...")
            subprocess.run(["git", "push", "origin", parsed.branch], cwd=str(path), check=True)

            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(path),
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
            pushed[name] = sha
            print(f"  ✅ {name} pushed at {sha[:12]}")

        if not pushed:
            print("\n✓ Nothing to push.")
            return 0

        self._update_lock_shas(pushed)
        print(f"\n✅ Pushed {len(pushed)} lib(s). Lock files updated.")
        print("   Run `docker compose build --no-cache` to pick up the changes.")
        return 0

    # ------------------------------------------------------------------
    #  Command validation
    # ------------------------------------------------------------------
    def validate_commands(self, args: List[str]) -> int:
        """Validate all make commands and check for errors."""
        parser = argparse.ArgumentParser(prog="validate-commands")
        parser.add_argument("--site", help="Validate for specific site")
        parser.add_argument("--all", action="store_true", help="Validate all sites")
        parser.add_argument("--verbose", action="store_true", help="Show detailed output")
        parsed = parser.parse_args(args)

        failed = []
        passed = []

        # Determine which sites to validate
        if parsed.all:
            sites_to_check = list(SITES.keys())
        elif parsed.site:
            sites_to_check = [parsed.site]
        else:
            sites_to_check = ["ctc-research"]

        for site_name in sites_to_check:
            try:
                site = self.resolve_site(site_name)
                cli = SiteCLI(site)
                env = cli.site_env()

                # Get all make targets
                result = subprocess.run(
                    ["make", "show-targets"],
                    cwd=str(REPO_ROOT),
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )

                if result.returncode != 0:
                    failed.append(f"{site_name}: Failed to list targets")
                    continue

                targets = [line.strip() for line in result.stdout.splitlines() if line.strip()]

                site_passed = 0
                site_failed = 0

                for target in targets:
                    result = subprocess.run(
                        ["make", "--dry-run", target, f"WEBSITE={site}"],
                        cwd=str(REPO_ROOT),
                        env=env,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        check=False,
                    )
                    if result.returncode == 0:
                        site_passed += 1
                        if parsed.verbose:
                            print(f"  ✅ {target}")
                    else:
                        site_failed += 1
                        failed.append(f"{site_name}/{target}: {result.stdout.strip()}")
                        if parsed.verbose:
                            print(f"  ❌ {target}: {result.stdout.strip()}")

                passed.append(f"{site_name}: {site_passed} passed, {site_failed} failed")
                if parsed.verbose:
                    print(f"\n{site_name}: {site_passed} passed, {site_failed} failed")

            except Exception as e:
                failed.append(f"{site_name}: {str(e)}")

        print("\n" + "=" * 60)
        print("COMMAND VALIDATION SUMMARY")
        print("=" * 60)

        if passed:
            print("\nSites Passed:")
            for p in passed:
                print(f"  {p}")

        if failed:
            print("\nFailures:")
            for f in failed:
                print(f"  {f}")
            return 1

        print("\n✅ All commands validated successfully!")
        return 0

    # ------------------------------------------------------------------
    #  Django command runner
    # ------------------------------------------------------------------
    def run_django_command(self, argv: List[str]) -> None:
        """Configure environment and execute a Django management command."""
        self.configure_django()
        try:
            from django.core.management import execute_from_command_line
        except ImportError as exc:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable?"
            ) from exc
        execute_from_command_line(argv)


# ----------------------------------------------------------------------
#  Command line interface for direct use (optional)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Allow running site_cli.py as a script for testing
    cli = SiteCLI()
    print(f"Current site: {cli.site}")
