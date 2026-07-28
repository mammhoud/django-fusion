"""
verify_deployment management command
======================================
Verify deployment health: Docker container status, network connectivity,
port exposure, environment variables, Traefik routing config, dependency
services, and container health check.

Usage:
    uv run python manage.py verify_deployment
    uv run python manage.py verify_deployment --container fusion-cms-core
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand
from django_fusion.site.management.commands.base import BaseCommand

# ---------------------------------------------------------------------------
# ANSI colour helpers
# ---------------------------------------------------------------------------

_GREEN = "\033[0;32m"
_RED = "\033[0;31m"
_YELLOW = "\033[1;33m"
_RESET = "\033[0m"


def _pass(msg: str) -> str:
    return f"{_GREEN}✓{_RESET} {msg}"


def _fail(msg: str) -> str:
    return f"{_RED}✗{_RESET} {msg}"


def _warn(msg: str) -> str:
    return f"{_YELLOW}!{_RESET} {msg}"


# ---------------------------------------------------------------------------
# Container name auto-detection
# ---------------------------------------------------------------------------

_CONTAINER_MAP: dict[str, str] = {
    "docker": "core",
    "demo": "fusion-cms-core",
    "production": "fusion-cms-core",
    "local": "core",
}

_DEFAULT_CONTAINER = "fusion-cms-core"


def _detect_container() -> str:
    """Return the container name inferred from ``RUNNING_ENV``."""
    running_env = os.environ.get("RUNNING_ENV", "").lower()
    return _CONTAINER_MAP.get(running_env, _DEFAULT_CONTAINER)


# ---------------------------------------------------------------------------
# Low-level Docker helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> tuple[int, str, str]:
    """Run *cmd* and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return 1, "", "docker: command not found"
    except subprocess.TimeoutExpired:
        return 1, "", "command timed out"


def _docker_available() -> bool:
    rc, _, _ = _run(["docker", "info"])
    return rc == 0


def _container_running(name: str) -> bool:
    rc, out, _ = _run(["docker", "ps", "--filter", f"name={name}", "--format", "{{.Names}}"])
    return rc == 0 and name in out


def _container_exists(name: str) -> bool:
    rc, out, _ = _run(["docker", "ps", "-a", "--filter", f"name={name}", "--format", "{{.Names}}"])
    return rc == 0 and name in out


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def _check_compose_config(project_root: Path) -> tuple[bool, str]:
    """Check 1 — Docker Compose config validity."""
    compose_file = project_root / "docker-compose.yml"
    if not compose_file.exists():
        return False, f"docker-compose.yml not found at {compose_file}"

    rc, _, err = _run(["docker", "compose", "-f", str(compose_file), "config"])
    if rc == 0:
        return True, "Docker Compose file is valid"
    return False, f"Docker Compose config invalid: {err or 'unknown error'}"


def _check_container_status(container: str) -> tuple[bool | None, str]:
    """
    Check 2 — Container running status.

    Returns ``(True, msg)`` if running, ``(None, msg)`` if exists-but-stopped
    (warn), ``(False, msg)`` if absent.
    """
    if _container_running(container):
        rc, status, _ = _run(
            ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Status}}"]
        )
        return True, f"Container is running: {status}"

    if _container_exists(container):
        rc, status, _ = _run(
            ["docker", "ps", "-a", "--filter", f"name={container}", "--format", "{{.Status}}"]
        )
        return None, f"Container exists but not running: {status}"

    return False, "Container does not exist"


def _check_network(container: str) -> list[tuple[bool | None, str]]:
    """Check 3 — traefik-net network existence and container membership."""
    results: list[tuple[bool | None, str]] = []

    rc, _, _ = _run(["docker", "network", "inspect", "traefik-net"])
    if rc != 0:
        results.append((False, "traefik-net network does not exist"))
        return results

    results.append((True, "traefik-net network exists"))

    # Check container is connected
    rc2, out2, _ = _run(["docker", "inspect", container])
    if rc2 == 0 and "traefik-net" in out2:
        results.append((True, "Container is connected to traefik-net"))
    else:
        results.append((None, "Container not connected to traefik-net (or not running)"))

    return results


def _check_port_exposure(container: str) -> tuple[bool | None, str]:
    """Check 4 — Port exposure."""
    if not _container_running(container):
        return None, "Port exposure unknown (container not running)"

    rc, ports, _ = _run(
        ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Ports}}"]
    )
    if rc == 0 and ports:
        return True, f"Port exposure configured: {ports}"
    return None, "No ports exposed (container may not be running)"


def _check_env_vars(container: str) -> list[tuple[bool | None, str]]:
    """Check 5 — Environment variables PORT, DEBUG, DB_NAME."""
    if not _container_running(container):
        return [(None, "Container not running, cannot check environment")]

    results: list[tuple[bool | None, str]] = []

    rc, env_out, _ = _run(["docker", "exec", container, "env"])
    if rc != 0:
        return [(None, "Could not read container environment")]

    env: dict[str, str] = {}
    for line in env_out.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()

    # PORT
    port_val = env.get("PORT", "")
    if port_val:
        results.append((True, f"PORT={port_val}"))
    else:
        results.append((None, "PORT not set in container environment"))

    # DEBUG
    debug_val = env.get("DEBUG", "")
    if debug_val:
        results.append((True, f"DEBUG={debug_val}"))
    else:
        results.append((None, "DEBUG not set in container environment"))

    # DB_NAME
    db_name_val = env.get("DB_NAME", "")
    if db_name_val:
        results.append((True, f"DB_NAME={db_name_val}"))
    else:
        results.append((None, "DB_NAME not set in container environment"))

    return results


def _check_traefik_config() -> list[tuple[bool | None, str]]:
    """Check 6 — Traefik routing config file."""
    # Try common locations relative to the repo root
    candidates = [
        Path("/root/site/compose/traefik/dynamic/fusion-cms.yml"),
        Path("/root/site/compose/traefik/dynamic/fusion-cms-core.yml"),
        Path("/root/site/compose/traefik/dynamic/fusion-cms-main.yml"),
    ]

    # Also search relative to this file's repo root
    repo_root = Path(__file__).resolve().parents[6]  # workspace root
    for name in ("fusion-cms.yml", "fusion-cms-core.yml", "fusion-cms-main.yml"):
        candidates.append(repo_root / "compose" / "traefik" / "dynamic" / name)

    traefik_file: Path | None = None
    for candidate in candidates:
        if candidate.exists():
            traefik_file = candidate
            break

    if traefik_file is None:
        return [(False, "Traefik routing config file not found")]

    results: list[tuple[bool | None, str]] = [(True, f"Traefik config file exists: {traefik_file.name}")]

    content = traefik_file.read_text(encoding="utf-8")

    # Check for a fusion-cms.com domain
    if "fusion-cms.com" in content:
        results.append((True, "Domain configured: fusion-cms.com"))
    else:
        results.append((None, "fusion-cms.com domain not found in Traefik config"))

    return results


def _check_dependencies() -> list[tuple[bool, str]]:
    """Check 7 — Dependency services: postgres, redis, traefik."""
    services = [
        ("postgres", "PostgreSQL"),
        ("redis", "Redis"),
        ("traefik", "Traefik"),
    ]
    results: list[tuple[bool, str]] = []
    for filter_name, display_name in services:
        rc, out, _ = _run(["docker", "ps", "--filter", f"name={filter_name}", "--format", "{{.Names}}"])
        if rc == 0 and filter_name in out.lower():
            results.append((True, f"{display_name} is running"))
        else:
            results.append((False, f"{display_name} is not running"))
    return results


def _check_health(container: str) -> tuple[bool | None, str]:
    """Check 8 — Container health check status."""
    if not _container_running(container):
        return None, "Container not running, cannot check health"

    rc, health, _ = _run(
        ["docker", "inspect", container, "--format", "{{.State.Health.Status}}"]
    )
    if rc != 0:
        return None, "Could not inspect container health"

    health = health.strip()
    if health == "healthy":
        return True, "Container is healthy"
    if health == "starting":
        return None, "Container health check is starting"
    if health == "unhealthy":
        return False, "Container is unhealthy"
    return None, f"Health check not configured or unavailable ({health or 'no healthcheck'})"


# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Verify deployment: container status, network, ports, env vars, "
        "Traefik routing, dependency services, and container health."
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--container",
            default=None,
            help=(
                "Container name to inspect "
                "(default: auto-detected from RUNNING_ENV env var)"
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:  # noqa: C901
        container = options["container"] or _detect_container()

        self.stdout.write(
            "\n======================================================"
        )
        self.stdout.write("Fusion CMS Deployment Verification")
        self.stdout.write(
            "======================================================\n"
        )
        self.stdout.write(f"Container target: {container}\n")

        if not _docker_available():
            self.stderr.write(
                _fail("Docker is not available or not running. Cannot perform checks.")
            )
            sys.exit(1)

        any_failure = False

        # ------------------------------------------------------------------
        # 1. Docker Compose config
        # ------------------------------------------------------------------
        self.stdout.write("1. Checking Docker Compose Configuration...")
        project_root = Path(__file__).resolve().parents[4]  # fusion-cms.com/
        ok, msg = _check_compose_config(project_root)
        if ok:
            self.stdout.write(_pass(msg))
        else:
            self.stdout.write(_fail(msg))
            any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 2. Container status
        # ------------------------------------------------------------------
        self.stdout.write("2. Checking Container Status...")
        status, msg = _check_container_status(container)
        if status is True:
            self.stdout.write(_pass(msg))
        elif status is None:
            self.stdout.write(_warn(msg))
        else:
            self.stdout.write(_fail(msg))
            any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 3. Network
        # ------------------------------------------------------------------
        self.stdout.write("3. Checking Network Configuration...")
        for ok, msg in _check_network(container):
            if ok is True:
                self.stdout.write(_pass(msg))
            elif ok is None:
                self.stdout.write(_warn(msg))
            else:
                self.stdout.write(_fail(msg))
                any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 4. Port exposure
        # ------------------------------------------------------------------
        self.stdout.write("4. Checking Port Configuration...")
        ok, msg = _check_port_exposure(container)
        if ok is True:
            self.stdout.write(_pass(msg))
        elif ok is None:
            self.stdout.write(_warn(msg))
        else:
            self.stdout.write(_fail(msg))
            any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 5. Environment variables
        # ------------------------------------------------------------------
        self.stdout.write("5. Checking Environment Variables...")
        for ok, msg in _check_env_vars(container):
            if ok is True:
                self.stdout.write(_pass(msg))
            elif ok is None:
                self.stdout.write(_warn(msg))
            else:
                self.stdout.write(_fail(msg))
                any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 6. Traefik routing config
        # ------------------------------------------------------------------
        self.stdout.write("6. Checking Traefik Routing Configuration...")
        for ok, msg in _check_traefik_config():
            if ok is True:
                self.stdout.write(_pass(msg))
            elif ok is None:
                self.stdout.write(_warn(msg))
            else:
                self.stdout.write(_fail(msg))
                any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 7. Dependency services
        # ------------------------------------------------------------------
        self.stdout.write("7. Checking Service Dependencies...")
        for ok, msg in _check_dependencies():
            if ok:
                self.stdout.write(_pass(msg))
            else:
                self.stdout.write(_fail(msg))
                any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # 8. Container health
        # ------------------------------------------------------------------
        self.stdout.write("8. Checking Container Health...")
        ok, msg = _check_health(container)
        if ok is True:
            self.stdout.write(_pass(msg))
        elif ok is None:
            self.stdout.write(_warn(msg))
        else:
            self.stdout.write(_fail(msg))
            any_failure = True
        self.stdout.write("")

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        self.stdout.write(
            "======================================================"
        )
        self.stdout.write("Summary")
        self.stdout.write(
            "======================================================\n"
        )
        self.stdout.write(f"Container : {container}")
        self.stdout.write("Project   : fusion-cms.com/core")
        self.stdout.write("Domain    : https://fusion-cms.com\n")

        if any_failure:
            self.stderr.write(
                _fail("One or more checks FAILED. Review the output above.")
            )
            sys.exit(1)
        else:
            self.stdout.write(
                _pass("All checks passed.")
            )
