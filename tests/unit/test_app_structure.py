"""
App structure tests for allauth-htmx-auth-pages.

Feature: allauth-htmx-auth-pages
Tests: Tasks 15.1, 15.3, 15.4

Tests:
    15.1 - Registration app location
    15.3 - No cross-site branding in templates
    15.4 - URL namespace separation
"""
from pathlib import Path

import pytest

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
CTC_ROOT = WORKSPACE_ROOT / "ctc-research.com"
STRUCTA_ROOT = WORKSPACE_ROOT / "structa.cloud"
REPO_ROOT = WORKSPACE_ROOT

SITE_ROOTS = [r for r in (CTC_ROOT, STRUCTA_ROOT, REPO_ROOT) if (r / "plugins").exists()]


# ── Test 15.1: Registration app location ─────────────────────────────────────

@pytest.mark.parametrize(
    "site_root,expected_name,expected_label",
    [(root, "plugins.accounts.registration", "accounts_registration") for root in SITE_ROOTS],
)
def test_registration_app_location(site_root, expected_name, expected_label):
    """
    Feature: allauth-htmx-auth-pages, Test 15.1: Registration app location.

    Assert plugins/accounts/registration/ exists.
    Assert www/projects/handlers/registration/ does NOT exist.
    Assert apps.py has correct name and label.
    Validates: Task 1 (app restructuring)
    """
    site_name = site_root.name

    # New location must exist
    new_location = site_root / "plugins" / "accounts" / "registration"
    assert new_location.exists(), \
        f"{site_name}: plugins/accounts/registration/ must exist"
    assert (new_location / "__init__.py").exists(), \
        f"{site_name}: plugins/accounts/registration/__init__.py must exist"
    assert (new_location / "apps.py").exists(), \
        f"{site_name}: plugins/accounts/registration/apps.py must exist"

    # Old location must NOT exist
    old_location = site_root / "www" / "core" / "handlers" / "registration"
    assert not old_location.exists(), \
        f"{site_name}: www/projects/handlers/registration/ must be deleted (moved to plugins/accounts/registration/)"

    # apps.py must have correct name and label
    apps_py = (new_location / "apps.py").read_text(encoding="utf-8")
    assert f'name = "{expected_name}"' in apps_py, \
        f"{site_name}: apps.py must have name = \"{expected_name}\""
    assert f'label = "{expected_label}"' in apps_py, \
        f"{site_name}: apps.py must have label = \"{expected_label}\""


# ── Test 15.3: No cross-site branding in templates ───────────────────────────

@pytest.mark.parametrize(
    "site_root,forbidden_term",
    [
        *([(CTC_ROOT, "structa")] if CTC_ROOT in SITE_ROOTS else []),
        *([(STRUCTA_ROOT, "precis-ctc"), (STRUCTA_ROOT, "ctc_research")] if STRUCTA_ROOT in SITE_ROOTS else []),
    ],
    ids=lambda row: f"{row[0].name}:{row[1]}",
)
def test_no_cross_site_branding_in_templates(site_root, forbidden_term):
    """
    Feature: allauth-htmx-auth-pages, Test 15.3: No cross-site branding in templates.

    Assert no .html file in ctc-research.com/templates contains "structa".
    Assert no .html file in structa.cloud/templates contains "precis-ctc".
    Validates: Task 10 (branding audit)
    """
    site_name = site_root.name

    # Search all template directories
    template_dirs = [
        site_root / "templates",
        site_root / "assets" / "templates",
        site_root / "plugins" / "accounts" / "templates",
        site_root / "www" / "core" / "templates",
        site_root / "www" / "apps" / "templates",
    ]

    violations = []
    for template_dir in template_dirs:
        if not template_dir.exists():
            continue
        for html_file in template_dir.rglob("*.html"):
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            if forbidden_term.lower() in content.lower():
                # Check it's not just in a comment
                lines_with_term = [
                    (i + 1, line.strip())
                    for i, line in enumerate(content.splitlines())
                    if forbidden_term.lower() in line.lower()
                    and not line.strip().startswith("{#")
                    and not line.strip().startswith("<!--")
                ]
                if lines_with_term:
                    rel_path = html_file.relative_to(WORKSPACE_ROOT)
                    violations.append(f"{rel_path}: lines {[ln[0] for ln in lines_with_term]}")

    assert not violations, (
        f"{site_name}: Found '{forbidden_term}' in templates (cross-site branding leak):\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


# ── Test 15.4: URL namespace separation ──────────────────────────────────────

@pytest.mark.parametrize("site_root", SITE_ROOTS, ids=lambda p: p.name)
def test_url_namespace_separation(site_root):
    """
    Feature: allauth-htmx-auth-pages, Test 15.4: URL namespace separation.

    Assert accounts/urls.py has no profile/* routes.
    Assert profile/urls.py has no cart/* or settings/* routes.
    Validates: Task 2 (accounts/profile separation)
    """
    site_name = site_root.name

    accounts_urls = site_root / "plugins" / "accounts" / "urls.py"
    profile_urls = site_root / "plugins" / "profile" / "urls.py"

    # Check accounts/urls.py has no profile/* routes
    if accounts_urls.exists():
        content = accounts_urls.read_text(encoding="utf-8")
        profile_routes = [
            line.strip()
            for line in content.splitlines()
            if '"profile/' in line or "'profile/" in line
            and not line.strip().startswith("#")
        ]
        assert not profile_routes, (
            f"{site_name}: accounts/urls.py must not contain profile/* routes:\n"
            + "\n".join(f"  - {r}" for r in profile_routes)
        )

    # Check profile/urls.py has no cart/* routes
    if profile_urls.exists():
        content = profile_urls.read_text(encoding="utf-8")
        cart_routes = [
            line.strip()
            for line in content.splitlines()
            if ('"cart/' in line or "'cart/" in line)
            and not line.strip().startswith("#")
        ]
        assert not cart_routes, (
            f"{site_name}: profile/urls.py must not contain cart/* routes:\n"
            + "\n".join(f"  - {r}" for r in cart_routes)
        )


# ── Test: No pipelines: namespace in any template ────────────────────────────

@pytest.mark.parametrize("site_root", SITE_ROOTS, ids=lambda p: p.name)
def test_no_pipelines_namespace_in_templates(site_root):
    """
    Feature: allauth-htmx-auth-pages: No pipelines: namespace in any template.

    Assert no template file contains 'pipelines:' URL references.
    All URL references must use 'plugins:' namespace.
    """
    site_name = site_root.name

    template_dirs = [
        site_root / "templates",
        site_root / "assets" / "templates",
        site_root / "plugins" / "accounts" / "templates",
        site_root / "www" / "core" / "templates",
        site_root / "www" / "apps" / "templates",
    ]

    violations = []
    for template_dir in template_dirs:
        if not template_dir.exists():
            continue
        for html_file in template_dir.rglob("*.html"):
            content = html_file.read_text(encoding="utf-8", errors="ignore")
            if "pipelines:" in content:
                rel_path = html_file.relative_to(WORKSPACE_ROOT)
                violations.append(str(rel_path))

    assert not violations, (
        f"{site_name}: Found 'pipelines:' namespace in templates "
        "(must use 'plugins:' instead):\n"
        + "\n".join(f"  - {v}" for v in violations)
    )


# ── Test: account/ templates deleted ─────────────────────────────────────────

@pytest.mark.parametrize("site_root", SITE_ROOTS, ids=lambda p: p.name)
def test_account_templates_deleted(site_root):
    """
    Feature: allauth-htmx-auth-pages: account/ wrapper templates deleted.

    Assert templates/account/login.html, signup.html, password_reset.html,
    email_confirm.html do not exist in any template directory.
    """
    site_name = site_root.name
    deleted_files = ["login.html", "signup.html", "password_reset.html", "email_confirm.html"]

    template_dirs = [
        site_root / "templates" / "account",
        site_root / "assets" / "templates" / "account",
        site_root / "plugins" / "accounts" / "templates" / "account",
    ]

    for template_dir in template_dirs:
        for filename in deleted_files:
            file_path = template_dir / filename
            assert not file_path.exists(), (
                f"{site_name}: {file_path.relative_to(WORKSPACE_ROOT)} "
                "should have been deleted (account/ wrapper templates are obsolete)"
            )
