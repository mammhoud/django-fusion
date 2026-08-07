from django.test import Client, TestCase

from apps.content.models.contact import ContactSubmission


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
