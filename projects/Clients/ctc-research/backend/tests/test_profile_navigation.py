"""Regression coverage for the authenticated profile navigation contract."""

from pathlib import Path

from django.test import SimpleTestCase, override_settings
from django.urls import resolve, reverse

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_DIR = _BACKEND_DIR.parent


@override_settings(ROOT_URLCONF="tests.urls")
class ProfileNavigationContractTests(SimpleTestCase):
    """Keep profile navigation and password actions on real routes."""

    def test_sidebar_routes_resolve_under_legacy_fusion_namespace(self):
        expected = {
            "handlers:dashboard": "/profile/dashboard/",
            "handlers:profile": "/profile/profile/",
            "handlers:courses": "/profile/courses/",
            "handlers:certifications": "/profile/certifications/",
            "handlers:settings": "/profile/settings/",
            "handlers:change_password": "/profile/settings/change-password/",
        }
        for name, path in expected.items():
            with self.subTest(name=name):
                self.assertEqual(reverse(name), path)

    def test_password_action_is_handled_by_settings_view(self):
        resolved = resolve("/profile/settings/change-password/")
        self.assertEqual(resolved.url_name, "change_password")
        self.assertEqual(resolved.func.view_class.__name__, "SettingsView")

    def test_sidebar_uses_learning_and_security_choices(self):
        navigation = (
            _PROJECT_DIR
            / "assets"
            / "templates"
            / "profile"
            / "profile"
            / "partials"
            / "nav-menu.html"
        ).read_text()
        for label in ("Dashboard", "Courses", "Certificates", "Settings", "Change password"):
            with self.subTest(label=label):
                self.assertIn(label, navigation)
        self.assertIn("Enrollments & progress", navigation)
        self.assertIn("Privacy, security & preferences", navigation)

    def test_frontend_profile_does_not_use_removed_learning_routes(self):
        profile_page = (
            _PROJECT_DIR / "frontend" / "src" / "pages" / "profile.astro"
        ).read_text()
        self.assertNotIn("/learning/dashboard/", profile_page)
        self.assertNotIn("/learning/profile/", profile_page)
        for path in (
            "/profile/dashboard/",
            "/profile/courses/",
            "/profile/certifications/",
            "/profile/settings/",
            "/accounts/password/change/",
        ):
            with self.subTest(path=path):
                self.assertIn(path, profile_page)
