"""
🎯 Unified Django CLI — check + deploy + push libs
Usage:
  python cli.py check lms-demo
  python cli.py deploy lms-demo
  python cli.py deploy ctc-research
  python cli.py push                        # commit & push all libs to generic
  python cli.py push --lib django-osoul     # push a single lib
  python -m websites check lms-demo
  python -m websites deploy ctc-research
"""

import os
import subprocess
import sys
from pathlib import Path

import fire

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent  # root of the monorepo

WEBSITES = {
    "lms-demo": {
        "compose": SCRIPT_DIR / "lms-demo" / "docker-compose.yml",
        "port": 5071,
        "container": "structa-website",
    },
    "ctc-research": {
        "compose": SCRIPT_DIR / "ctc-research" / "docker-compose.yml",
        "port": 5070,
        "container": "ctc-website",
    },
}

# Internal libs that live under libs/ and are pushed to GitHub
LIBS = {
    "django-osoul": WORKSPACE_ROOT / "libs" / "django-osoul",
    "django-rseal": WORKSPACE_ROOT / "libs" / "django-rseal",
    "django-grep":  WORKSPACE_ROOT / "libs" / "django-grep",
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _run(cmd: list[str], cwd=None, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or SCRIPT_DIR, check=check,
                          capture_output=False)


def _website_env(website: str) -> dict:
    """Minimal env vars needed to run manage.py check without a real DB."""
    env = os.environ.copy()
    env.update({
        "DJANGO_SETTINGS_MODULE": "configs.settings",
        "RUNNING_ENV": "docker",
        "SERVER_ENV": "production",
        "DB_HOST": env.get("DB_HOST", "postgres"),
        "DB_NAME": env.get("DB_NAME", f"db_{'structa' if 'structa' in website else 'ctc'}"),
        "REDIS_URL": env.get("REDIS_URL", "redis://redis:6379/3"),
        "ALLOWED_HOSTS": "*",
    })
    # Remove DJANGO_SECRET_KEY — production.py reads from secret.key.txt
    env.pop("DJANGO_SECRET_KEY", None)
    return env


def _resolve(website: str) -> str:
    if website not in WEBSITES:
        print(f"❌ Unknown website '{website}'. Choose: {', '.join(WEBSITES)}")
        sys.exit(1)
    return website


# ─────────────────────────────────────────────
# Per-website __main__.py check (local)
# ─────────────────────────────────────────────

def _local_check(website: str) -> bool:
    """
    Run `python <website>/__main__.py check` locally.
    Uses the website's .venv if present, otherwise system python.
    Returns True if checks pass.
    """
    main_py = SCRIPT_DIR / website / "__main__.py"
    if not main_py.exists():
        print(f"⚠️  No __main__.py found at {main_py}, skipping local check")
        return True

    # Prefer the workspace .venv python which has all deps installed
    venv_python = SCRIPT_DIR / ".venv" / "bin" / "python"
    python = str(venv_python) if venv_python.exists() else sys.executable

    print(f"\n🔍 Running local Django check via {website}/__main__.py ...")
    site_dir = SCRIPT_DIR / website
    env = _website_env(website)

    result = subprocess.run(
        [python, str(main_py), "check"],
        cwd=str(site_dir),
        env=env,
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"❌ Local check FAILED for {website}")
        return False
    print(f"✅ Local check PASSED for {website}")
    return True


# ─────────────────────────────────────────────
# Container check (after build)
# ─────────────────────────────────────────────

def _container_check(website: str) -> bool:
    """Run manage.py check inside the built container image."""
    cfg = WEBSITES[website]
    image = cfg["container"]
    env = _website_env(website)

    print(f"\n🔍 Running container Django check on image '{image}' ...")
    cmd = [
        "docker", "run", "--rm",
        *[f"-e{k}={v}" for k, v in {
            "DJANGO_SETTINGS_MODULE": env["DJANGO_SETTINGS_MODULE"],
            "RUNNING_ENV": env["RUNNING_ENV"],
            "SERVER_ENV": env["SERVER_ENV"],
            "DB_HOST": env["DB_HOST"],
            "DB_NAME": env["DB_NAME"],
            "REDIS_URL": env["REDIS_URL"],
            "ALLOWED_HOSTS": env["ALLOWED_HOSTS"],
        }.items()],
        image,
        "python", "manage.py", "check",
    ]
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"❌ Container check FAILED for {website}")
        return False
    print(f"✅ Container check PASSED for {website}")
    return True


# ─────────────────────────────────────────────
# CLI Commands
# ─────────────────────────────────────────────

class CLI:
    """
    Websites CLI — check, deploy, push libs.

    Examples:
      python cli.py check lms-demo
      python cli.py deploy lms-demo
      python cli.py deploy ctc-research --skip-local-check
      python cli.py push                        # commit & push all libs
      python cli.py push --lib django-osoul     # push a single lib
      python cli.py logs lms-demo
      python cli.py down lms-demo
    """

    def check(self, website: str):
        """
        Run Django system checks locally via <website>/__main__.py.

        Args:
            website: 'lms-demo' or 'ctc-research'
        """
        _resolve(website)
        ok = _local_check(website)
        sys.exit(0 if ok else 1)

    def deploy(self, website: str, skip_local_check: bool = False,
               skip_container_check: bool = False, no_cache: bool = False):
        """
        Build, check, and deploy a website.

        Steps:
          1. Local check via <website>/__main__.py check  (skippable)
          2. docker compose build [--no-cache]
          3. Container check via docker run manage.py check  (skippable)
          4. docker compose up -d

        Args:
            website:              'lms-demo' or 'ctc-research'
            skip_local_check:     Skip step 1
            skip_container_check: Skip step 3
            no_cache:             Pass --no-cache to docker build
        """
        _resolve(website)
        cfg = WEBSITES[website]
        compose = str(cfg["compose"])

        # ── Step 1: local check ──────────────────────────────────────────
        if not skip_local_check:
            if not _local_check(website):
                print("\n💥 Aborting deploy — local check failed.")
                sys.exit(1)

        # ── Step 2: build ────────────────────────────────────────────────
        build_cmd = ["docker", "compose", "-f", compose, "build"]
        if no_cache:
            build_cmd.append("--no-cache")
        print(f"\n🏗️  Building {website} ...")
        _run(build_cmd)

        # ── Step 3: container check ──────────────────────────────────────
        if not skip_container_check:
            if not _container_check(website):
                print("\n💥 Aborting deploy — container check failed.")
                sys.exit(1)

        # ── Step 4: up ───────────────────────────────────────────────────
        print(f"\n🚀 Deploying {website} ...")
        _run(["docker", "compose", "-f", compose, "up", "-d"])
        print(f"\n✅ {website} deployed. Health: http://localhost:{cfg['port']}/health/")

    def logs(self, website: str, tail: int = 30, service: str = None):
        """
        Show container logs.

        Args:
            website: 'lms-demo' or 'ctc-research'
            tail:    Number of lines (default 30)
            service: Specific service name (optional)
        """
        _resolve(website)
        cfg = WEBSITES[website]
        cmd = ["docker", "compose", "-f", str(cfg["compose"]), "logs", f"--tail={tail}"]
        if service:
            cmd.append(service)
        _run(cmd, check=False)

    def down(self, website: str):
        """
        Stop and remove containers for a website.

        Args:
            website: 'lms-demo' or 'ctc-research'
        """
        _resolve(website)
        cfg = WEBSITES[website]
        _run(["docker", "compose", "-f", str(cfg["compose"]), "down"])

    def ps(self):
        """Show status of all website containers."""
        _run(["docker", "ps", "--format",
              "table {{.Names}}\t{{.Status}}\t{{.Ports}}",
              "--filter", "name=structa-website",
              "--filter", "name=ctc-website"], check=False)

    def build_assets(self, website: str = "all", production: bool = True, clean: bool = False):
        """
        Build static assets for a website.

        Runs webpack bundling and Django collectstatic.

        Args:
            website:     'lms-demo', 'ctc-research', or 'all'
            production:  Run production build (default True)
            clean:       Clean bundles directory before building
        """
        if website != "all":
            _resolve(website)

        targets = [website] if website != "all" else WEBSITES.keys()

        for site in targets:
            site_dir = SCRIPT_DIR / site
            manage_py = site_dir / "manage.py"

            if not manage_py.exists():
                print(f"⚠️  No manage.py found at {site_dir}, skipping")
                continue

            print(f"\n🔨 Building assets for {site}...")

            # Build the command
            venv_python = site_dir / ".venv" / "bin" / "python"
            python = str(venv_python) if venv_python.exists() else sys.executable

            cmd = [
                python,
                str(manage_py),
                "build_assets",
            ]

            if production:
                cmd.append("--production")
            else:
                cmd.append("--development")

            if clean:
                cmd.append("--clean")

            cmd.append("--no-input")

            result = subprocess.run(cmd, cwd=str(site_dir), capture_output=False)
            if result.returncode != 0:
                print(f"❌ Asset build failed for {site}")
                sys.exit(1)

            print(f"✅ Assets built for {site}")

    def test(self, website: str = "all", live: bool = False):
        """
        Run tests against running containers.

        Steps:
          1. Container tests via tests/scripts/run_container_tests.sh
          2. HTTP integration tests via pytest tests/test_sites.py

        Args:
            website: 'lms-demo', 'ctc-research', or 'all'
            live:    Use live domains (core.lms-demo / www.ctc-research)
        """
        if website != "all":
            _resolve(website)

        script = SCRIPT_DIR / "tests" / "scripts" / "run_container_tests.sh"
        env = os.environ.copy()
        if live:
            env["USE_LIVE_DOMAINS"] = "1"

        # Container-level tests
        print(f"\n🧪 Running container tests for: {website}")
        _run(["bash", str(script), website], cwd=str(SCRIPT_DIR))

        # HTTP integration tests
        print("\n🌐 Running HTTP integration tests ...")
        pytest_cmd = [
            sys.executable, "-m", "pytest",
            "tests/test_sites.py", "-v", "--tb=short", "--no-header",
        ]
        result = subprocess.run(pytest_cmd, cwd=str(SCRIPT_DIR), env=env)
        if result.returncode != 0:
            print("❌ HTTP tests failed")
            sys.exit(result.returncode)
        print("✅ All tests passed")


    def push(self, lib: str = "all", message: str = "", branch: str = "generic"):
        """
        Commit and push local lib changes to their GitHub branch.

        Stages all modified tracked files in each lib, commits with an
        auto-generated message (or the one you provide), then pushes to
        the target branch.  After pushing, updates the commit SHAs in
        websites/ctc-research/uv.lock so the next Docker build picks
        up the new versions.

        Args:
            lib:     'django-osoul', 'django-rseal', 'django-grep', or 'all'
            message: Commit message (auto-generated if omitted)
            branch:  Target branch (default: 'generic')

        Examples:
            python cli.py push
            python cli.py push --lib django-osoul --message "fix: add WagtailPageMixin"
            python cli.py push --lib django-rseal
        """
        targets = (
            {lib: LIBS[lib]} if lib != "all" else LIBS
        )

        if lib != "all" and lib not in LIBS:
            print(f"❌ Unknown lib '{lib}'. Choose: {', '.join(LIBS)} or 'all'")
            sys.exit(1)

        pushed: dict[str, str] = {}

        for name, path in targets.items():
            print(f"\n📦 Processing {name} at {path} ...")

            # Check for any changes (tracked modified + untracked new files)
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(path), capture_output=True, text=True
            )
            if not status.stdout.strip():
                print(f"  ✓ No changes in {name}, skipping.")
                continue

            # Stage all tracked modifications (not untracked)
            subprocess.run(["git", "add", "-u"], cwd=str(path), check=True)

            # Also stage any new files under src/
            subprocess.run(
                ["git", "add", "src/"],
                cwd=str(path), check=False  # non-fatal if src/ doesn't exist
            )

            # Build commit message
            commit_msg = message or f"chore({name}): sync local changes to {branch}"

            # Commit (skip if nothing staged)
            staged = subprocess.run(
                ["git", "diff", "--cached", "--quiet"],
                cwd=str(path)
            )
            if staged.returncode == 0:
                print(f"  ✓ Nothing staged in {name}, skipping commit.")
                continue

            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=str(path), check=True
            )

            # Push
            print(f"  🚀 Pushing {name} → origin/{branch} ...")
            subprocess.run(
                ["git", "push", "origin", branch],
                cwd=str(path), check=True
            )

            # Capture new SHA
            sha = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(path), capture_output=True, text=True
            ).stdout.strip()
            pushed[name] = sha
            print(f"  ✅ {name} pushed at {sha[:12]}")

        if not pushed:
            print("\n✓ Nothing to push.")
            return

        # Update uv.lock files with new SHAs
        self._update_lock_shas(pushed)
        print(f"\n✅ Pushed {len(pushed)} lib(s). Lock files updated.")
        print("   Run `docker compose build --no-cache` to pick up the changes.")

    def _update_lock_shas(self, pushed: dict[str, str]):
        """Update commit SHAs in all uv.lock files for pushed libs."""
        lock_files = list(SCRIPT_DIR.glob("*/uv.lock"))
        if not lock_files:
            return

        # Map lib name → GitHub repo slug (as it appears in the lock file)
        repo_map = {
            "django-osoul": "django-osoul",
            "django-rseal": "django-rseal",
            "django-grep":  "django-grep",
        }

        for lock_path in lock_files:
            content = lock_path.read_text()
            original = content

            for lib_name, new_sha in pushed.items():
                repo = repo_map.get(lib_name)
                if not repo:
                    continue
                # Replace any existing 40-char SHA for this repo
                import re
                pattern = (
                    rf'(git = "https://github\.com/mammhoud/{re.escape(repo)}'
                    rf'\?branch=generic#)[0-9a-f]{{40}}'
                )
                content = re.sub(pattern, rf'\g<1>{new_sha}', content)

            if content != original:
                lock_path.write_text(content)
                print(f"  📝 Updated {lock_path.relative_to(SCRIPT_DIR)}")


def main():
    fire.Fire(CLI)


if __name__ == "__main__":
    main()
