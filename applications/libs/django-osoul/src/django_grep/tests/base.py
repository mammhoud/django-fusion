"""Base test case classes for Django projects."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase


def _get_user_model():
    return get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup for Django projects.

    Provides a pre-created regular user and superuser, plus a helper to
    log in quickly.  Intended as the base class for all Django unit tests
    in the project.

    Attributes:
        user (User): A regular test user (``testuser / testpass123``).
        admin_user (User): A superuser (``admin / adminpass123``).
        client (Client): Django test client, reset before each test.

    Example::

        class ArticleTest(BaseTestCase):
            def test_list(self):
                self.login()
                response = self.client.get("/articles/")
                self.assertEqual(response.status_code, 200)
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = _get_user_model().objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        cls.admin_user = _get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

    def setUp(self):
        super().setUp()
        self.client = Client()

    def login(self, user=None):
        """Log in as the test user (or a provided user).

        Args:
            user: The user to log in as.  Defaults to ``self.user``.

        Returns:
            The user that was logged in.
        """
        u = user or self.user
        self.client.force_login(u)
        return u

    def login_as_admin(self):
        """Log in as the admin superuser.

        Returns:
            The admin user that was logged in.
        """
        return self.login(self.admin_user)


class BaseAPITestCase(BaseTestCase):
    """Base test case for JSON API views.

    Extends :class:`BaseTestCase` with convenience methods for sending
    JSON requests and asserting JSON responses.

    Example::

        class ItemAPITest(BaseAPITestCase):
            def test_list(self):
                self.login()
                response = self.get_json("/api/items/")
                data = self.assertJSONSuccess(response)
                self.assertIn("items", data)
    """

    def get_json(self, url, **kwargs):
        """Send a GET request with ``Content-Type: application/json``.

        Args:
            url: The URL to request.
            **kwargs: Extra keyword arguments forwarded to ``Client.get()``.

        Returns:
            The HTTP response object.
        """
        return self.client.get(url, content_type="application/json", **kwargs)

    def post_json(self, url, data, **kwargs):
        """Send a POST request with a JSON-encoded body.

        Args:
            url: The URL to request.
            data: A dict that will be JSON-encoded as the request body.
            **kwargs: Extra keyword arguments forwarded to ``Client.post()``.

        Returns:
            The HTTP response object.
        """
        import json
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **kwargs,
        )

    def put_json(self, url, data, **kwargs):
        """Send a PUT request with a JSON-encoded body.

        Args:
            url: The URL to request.
            data: A dict that will be JSON-encoded as the request body.
            **kwargs: Extra keyword arguments forwarded to ``Client.put()``.

        Returns:
            The HTTP response object.
        """
        import json
        return self.client.put(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **kwargs,
        )

    def patch_json(self, url, data, **kwargs):
        """Send a PATCH request with a JSON-encoded body.

        Args:
            url: The URL to request.
            data: A dict that will be JSON-encoded as the request body.
            **kwargs: Extra keyword arguments forwarded to ``Client.patch()``.

        Returns:
            The HTTP response object.
        """
        import json
        return self.client.patch(
            url,
            data=json.dumps(data),
            content_type="application/json",
            **kwargs,
        )

    def delete_json(self, url, **kwargs):
        """Send a DELETE request with ``Content-Type: application/json``.

        Args:
            url: The URL to request.
            **kwargs: Extra keyword arguments forwarded to ``Client.delete()``.

        Returns:
            The HTTP response object.
        """
        return self.client.delete(url, content_type="application/json", **kwargs)

    def assertJSONSuccess(self, response):
        """Assert the response is HTTP 200 with ``{"status": "success"}``.

        Args:
            response: The HTTP response to inspect.

        Returns:
            The parsed JSON body as a dict.

        Raises:
            AssertionError: If the status code is not 200 or the JSON body
                does not contain ``status == "success"``.
        """
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        return data

    def assertJSONError(self, response, status_code=400):
        """Assert the response is an error JSON response.

        Args:
            response: The HTTP response to inspect.
            status_code: Expected HTTP status code (default ``400``).

        Returns:
            The parsed JSON body as a dict.

        Raises:
            AssertionError: If the status code does not match or the JSON
                body does not contain ``status == "error"``.
        """
        self.assertEqual(response.status_code, status_code)
        data = response.json()
        self.assertEqual(data.get("status"), "error")
        return data


# ---------------------------------------------------------------------------
# Hypothesis strategy helpers
# ---------------------------------------------------------------------------
# These thin wrappers let website tests import strategies from django_grep
# without taking a direct dependency on hypothesis.
# ---------------------------------------------------------------------------

try:
    from hypothesis import strategies as _st

    def st_email():
        """Hypothesis strategy for valid email addresses.

        Returns:
            ``hypothesis.strategies.SearchStrategy[str]``
        """
        return _st.emails()

    def st_slug():
        """Hypothesis strategy for valid Django slug strings.

        Slugs are lowercase alphanumeric words separated by single hyphens.

        Returns:
            ``hypothesis.strategies.SearchStrategy[str]``
        """
        return _st.from_regex(r"[a-z0-9]+(?:-[a-z0-9]+)*", fullmatch=True)

    def st_uuid():
        """Hypothesis strategy for UUID4 strings.

        Returns:
            ``hypothesis.strategies.SearchStrategy[str]``
        """
        return _st.uuids().map(str)

except ImportError:  # pragma: no cover — hypothesis is optional at runtime
    def st_email():  # type: ignore[misc]
        raise ImportError("hypothesis is required for st_email()")

    def st_slug():  # type: ignore[misc]
        raise ImportError("hypothesis is required for st_slug()")

    def st_uuid():  # type: ignore[misc]
        raise ImportError("hypothesis is required for st_uuid()")
