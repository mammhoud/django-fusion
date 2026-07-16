#!/usr/bin/env python3
"""
CTC Research — Asset Pipeline Verification Script

Audits the ctc-research.com frontend asset pipeline for consistency across:
  - Django templates (bundle tag usage)
  - Django settings (STATIC_ROOT, MEDIA_ROOT, STATIC_URL, MEDIA_URL)
  - Webpack configuration (output paths, publicPath, entry points)
  - Nginx shared-media server (locations and volume mounts)
  - Traefik routing (static/media path prefixes and media subdomain)

Usage:
    python applications/scripts/verify_ctc_assets.py
    python applications/scripts/verify_ctc_assets.py --strict
    python applications/scripts/verify_ctc_assets.py --site ctc-research

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT
PROXY = ROOT.parent / "proxy"
CTC = CORE / "ctc-research"


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


def log_ok(msg: str) -> None:
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_warn(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def log_err(msg: str) -> None:
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def log_info(msg: str) -> None:
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.RESET}")


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------
def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def find_files(pattern: str, root: Path) -> Iterable[Path]:
    return root.rglob(pattern)


def grep(pattern: str, text: str) -> list[re.Match]:
    return list(re.finditer(pattern, text))


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
class CheckResult:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def check_templates(site: str) -> CheckResult:
    """Ensure CTC templates only use known render_bundle chunks."""
    result = CheckResult()
    allowed_bundles = {"static", "main", "app", "theme"}
    templates_dir = CTC / "assets" / "templates"

    if not templates_dir.exists():
        result.add_warning(f"No templates dir found at {templates_dir}")
        return result

    for path in find_files("*.html", templates_dir):
        text = read_text(path)
        for match in re.finditer(r"{%\s*render_bundle\s+['\"]([^'\"]+)['\"]", text):
            bundle = match.group(1)
            if bundle not in allowed_bundles:
                result.add_error(
                    f"{path}: unknown render_bundle chunk '{bundle}'. Allowed: {allowed_bundles}"
                )

    return result


def check_django_settings(site: str) -> CheckResult:
    """Verify Django static/media settings point to expected directories."""
    result = CheckResult()
    assets_py = CORE / "configs" / "base" / "assets.py"
    text = read_text(assets_py)

    expected_patterns = [
        (r'MEDIA_URL\s*=\s*settings\.get\("MEDIA_URL",\s*"/media/"\)', "MEDIA_URL default"),
        (r'STATIC_URL\s*=\s*settings\.get\("STATIC_URL",\s*"/static/"\)', "STATIC_URL default"),
        (r'STATIC_ROOT\s*=\s*str\(settings\.get\("STATIC_ROOT",\s*ASSETS_DIR\s*\/\s*"staticfiles"\)\)', "STATIC_ROOT default"),
        (r'MEDIA_ROOT\s*=\s*str\(MEDIA_DIR\)', "MEDIA_ROOT default"),
    ]

    for pattern, label in expected_patterns:
        if not re.search(pattern, text):
            result.add_error(f"{assets_py}: missing or unexpected {label}")

    return result


def check_webpack_config(site: str) -> CheckResult:
    """Verify webpack output path and publicPath match Django BUNDLE_DIR_NAME."""
    result = CheckResult()
    webpack_main = CORE / "webpack" / "main.config.js"
    text = read_text(webpack_main)

    if f'"{site}"' not in text and f"'{site}'" not in text:
        result.add_error(f"{webpack_main}: site '{site}' not referenced in SITE_DIR_MAP or SITE_ENTRIES")

    # publicPath is built from a template literal: `/static/bundles/${siteDir === 'VResume' ? 'vresume' : siteDir}/`
    if re.search(r"publicPath:\s*[`'][^`']*static/bundles/\$\{[^}]+\}[/`']", text):
        log_ok("webpack publicPath uses dynamic site-based bundle folder")
    else:
        result.add_error(f"{webpack_main}: publicPath does not reference a dynamic /static/bundles/<site>/ path")

    # outputDir is built conditionally and points to <site>/assets/bundles/<site>
    if re.search(r"path\.resolve\(workspaceRoot,\s*[^,]+,\s*['\"]assets['\"],\s*['\"]bundles['\"],\s*[^)]+\)", text):
        log_ok("webpack output path resolves to <site>/assets/bundles/<site>")
    else:
        result.add_error(f"{webpack_main}: output path does not resolve to <site>/assets/bundles/<site>")

    return result


def check_nginx_config(site: str) -> CheckResult:
    """Verify Nginx locations and volume mounts for the site."""
    result = CheckResult()
    nginx_conf = PROXY / "nginx" / "default.conf"
    text = read_text(nginx_conf)

    required_locations = [
        f"/static/bundles/{site}/",
        f"/sites/{site}/static/",
        f"/media/{site}/",
    ]

    for loc in required_locations:
        if f"location {loc}" not in text:
            result.add_error(f"{nginx_conf}: missing location {loc}")

    compose = PROXY / "docker-compose.nginx.yml"
    compose_text = read_text(compose)

    required_mounts = [
        f"../core/{site}/assets/staticfiles:/var/www/sites/{site}/static:ro",
        f"../core/{site}/assets/media:/var/www/media/{site}:ro",
    ]

    for mount in required_mounts:
        if mount not in compose_text:
            result.add_error(f"{compose}: missing volume mount '{mount}'")

    return result


def check_traefik_routing(site: str) -> CheckResult:
    """Verify Traefik routes static/media paths to shared-media."""
    result = CheckResult()
    traefik_file = PROXY / "traefik" / "dynamic" / f"{site}.yml"
    text = read_text(traefik_file)

    if "shared-media:80" not in text:
        result.add_error(f"{traefik_file}: static/media service does not route to shared-media:80")

    if "PathPrefix(`/static/`)" not in text or "PathPrefix(`/media/`)" not in text:
        result.add_error(f"{traefik_file}: missing /static/ or /media/ PathPrefix rules")

    media_servers = PROXY / "traefik" / "dynamic" / "media-servers.yml"
    media_text = read_text(media_servers)

    if f"Host(`media.{get_domain(site)}`)" not in media_text:
        result.add_error(f"{media_servers}: missing media.{get_domain(site)} router")

    return result


def check_bundles_json(site: str, strict: bool) -> CheckResult:
    """Optionally verify that bundles.json exists and is valid JSON."""
    result = CheckResult()
    bundles_json = CTC / "assets" / "bundles" / site / "bundles.json"

    if not bundles_json.exists():
        msg = f"{bundles_json} not found. Run: npm --prefix core/assets run build:{site_alias(site)}"
        if strict:
            result.add_error(msg)
        else:
            result.add_warning(msg)
        return result

    try:
        data = json.loads(bundles_json.read_text(encoding="utf-8"))
        status = data.get("status", "unknown")
        if status != "done":
            result.add_error(f"{bundles_json}: webpack status is '{status}', expected 'done'")
        else:
            log_ok(f"bundles.json is valid (status={status})")
    except json.JSONDecodeError as exc:
        result.add_error(f"{bundles_json}: invalid JSON ({exc})")

    return result


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def get_domain(site: str) -> str:
    mapping = {
        "ctc-research": "ctc-research.com",
        "lms-demo": "lms-demo.com",
        "vresume": "vresume.structa.cloud",
    }
    return mapping.get(site, f"{site}.example.com")


def site_alias(site: str) -> str:
    mapping = {
        "ctc-research": "ctc",
        "lms-demo": "structa",
        "VResume": "vresume",
    }
    return mapping.get(site, site)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify ctc-research.com asset pipeline consistency."
    )
    parser.add_argument(
        "--site",
        default="ctc-research",
        help="Site slug to verify (default: ctc-research)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if webpack bundles.json is missing (default: warn only)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    site = args.site

    log_info(f"Verifying asset pipeline for site: {site}")

    checks = [
        ("Templates", check_templates(site)),
        ("Django Settings", check_django_settings(site)),
        ("Webpack Config", check_webpack_config(site)),
        ("Nginx Config", check_nginx_config(site)),
        ("Traefik Routing", check_traefik_routing(site)),
        ("Webpack bundles.json", check_bundles_json(site, args.strict)),
    ]

    all_ok = True
    for label, result in checks:
        print(f"\n{Colors.CYAN}── {label} ──{Colors.RESET}")
        if result.ok and not result.warnings:
            log_ok("passed")
        else:
            for warning in result.warnings:
                log_warn(warning)
            for error in result.errors:
                log_err(error)
        if not result.ok:
            all_ok = False

    print()
    if all_ok:
        log_ok(f"All asset pipeline checks passed for {site}.")
        return 0
    else:
        log_err(f"Asset pipeline verification failed for {site}.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
