from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from apps.content.models.contact import ContactSubmission
from apps.pages.blog.models import BlogComment, BlogPost


class BlogCommentsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="commenter",
            email="commenter@example.com",
            password="pass-1234",
        )
        self.post = BlogPost.objects.create(
            title="A Precis post",
            slug="a-precis-post",
            author=self.user,
            content="A useful post body.",
            status="published",
        )

    def test_public_get_returns_approved_comments_only(self):
        BlogComment.objects.create(
            post=self.post,
            author=self.user,
            content="Visible comment",
            is_approved=True,
        )
        BlogComment.objects.create(
            post=self.post,
            author=self.user,
            content="Hidden comment",
            is_approved=False,
        )

        response = self.client.get(f"/apis/blog/{self.post.slug}/comments/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 1)
        self.assertEqual(response.json()["comments"][0]["body"], "Visible comment")

    def test_post_requires_auth_and_is_pending(self):
        anonymous = self.client.post(
            f"/apis/blog/{self.post.slug}/comments/",
            data={"body": "Please sign me in"},
        )
        self.assertEqual(anonymous.status_code, 401)

        self.client.force_login(self.user)
        response = self.client.post(
            f"/apis/blog/{self.post.slug}/comments/",
            data='{"body":"Needs review"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 202)
        self.assertTrue(response.json()["pending"])
        self.assertTrue(
            BlogComment.objects.filter(
                post=self.post,
                content="Needs review",
                is_approved=False,
            ).exists()
        )

    def test_unknown_post_returns_404(self):
        response = self.client.get("/apis/blog/does-not-exist/comments/")
        self.assertEqual(response.status_code, 404)

    def test_authenticated_post_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        blocked = csrf_client.post(
            f"/apis/blog/{self.post.slug}/comments/",
            data='{"body":"Blocked without token"}',
            content_type="application/json",
        )
        self.assertEqual(blocked.status_code, 403)

        csrf_client.get("/apis/auth/status/")
        csrf_token = csrf_client.cookies["csrftoken"].value
        allowed = csrf_client.post(
            f"/apis/blog/{self.post.slug}/comments/",
            data='{"body":"Allowed with token"}',
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(allowed.status_code, 202)


class LandingApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_contact_submission_accepts_json_payload(self):
        response = self.client.post(
            "/fragment/contact/",
            data={
                "name": "Ada Lovelace",
                "email": "ada@example.com",
                "subject": "Fusion question",
                "message": "Please tell me more about the LMS platform.",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Ada Lovelace", response.content.decode())
        self.assertIn("ada@example.com", response.content.decode())
        submission = ContactSubmission.objects.get(form_id="landing-contact")
        self.assertEqual(submission.get_email(), "ada@example.com")
        self.assertEqual(submission.submitted_data["subject"], "Fusion question")

    def test_contact_submission_rejects_incomplete_json_payload(self):
        response = self.client.post(
            "/fragment/contact/",
            data={"name": "Ada", "email": "not-an-email"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_landing_contract_routes_are_available(self):
        for path in (
            "/apis/site/settings/",
            "/apis/navigation/",
            "/apis/contact/",
            "/apis/pages/",
            "/apis/assets/",
            "/fragment/ping/",
        ):
            with self.subTest(path=path):
                self.assertNotEqual(self.client.get(path).status_code, 404)
