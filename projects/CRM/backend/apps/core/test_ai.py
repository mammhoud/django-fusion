"""Focused coverage for the consent-gated AI hub contract."""
from __future__ import annotations

import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from apps.core.ai import AIResult, build_prompt, consent_enabled, provider_catalog
from apps.core.models import AuditLog, Workspace


class AIHubTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="AI workspace", slug="ai-workspace")
        self.user = User.objects.create_user(
            username="ai-user", email="ai@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)

    def test_ai_page_renders_the_three_reviewable_operations(self):
        response = self.client.get("/ai/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Hub")
        self.assertContains(response, "Score a lead")
        self.assertContains(response, "Draft a sales email")
        self.assertContains(response, "Draft a social post")


        response = self.client.get("/apis/core/ai/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["consent"])
        self.assertEqual(
            {operation["id"] for operation in payload["operations"]},
            {"lead_score", "draft_sales_email", "draft_social_post"},
        )
        self.assertNotIn("api_key", json.dumps(payload).lower())
        self.assertNotIn("secret", json.dumps(payload).lower())

    def test_operation_requires_consent_and_does_not_audit_a_blocked_request(self):
        response = self.client.post(
            "/apis/core/ai/lead_score/",
            data=json.dumps({"context": {"brief": "A lead"}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(AuditLog.objects.filter(model_name="AIOperation").count(), 0)

    @override_settings(AI_PROVIDER="", AI_API_KEY="", AI_BASE_URL="")
    def test_consented_operation_degrades_honestly_without_provider(self):
        consent = self.client.post(
            "/apis/core/ai/consent/",
            data=json.dumps({"enabled": True}),
            content_type="application/json",
        )
        self.assertEqual(consent.status_code, 200)
        self.user.profile.refresh_from_db()
        self.assertTrue(consent_enabled(self.user.profile))

        response = self.client.post(
            "/apis/core/ai/draft_sales_email/",
            data=json.dumps({"context": {"brief": "A bounded opportunity"}}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "deferred")
        self.assertEqual(response.json()["provider"], "unconfigured")
        audit = AuditLog.objects.get(model_name="AIOperation")
        self.assertEqual(
            audit.changes,
            {
                "operation": "draft_sales_email",
                "status": "deferred",
                "provider": "unconfigured",
            },
        )

    def test_consent_rejects_non_boolean_values(self):
        response = self.client.post(
            "/apis/core/ai/consent/",
            data=json.dumps({"enabled": "yes"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_prompt_rejects_unknown_operations_and_bounds_context(self):
        with self.assertRaises(ValueError):
            build_prompt("invented", {})
        prompt = build_prompt("lead_score", {"brief": "x" * 20_000})
        self.assertLessEqual(len(prompt), 12_200)

    @override_settings(
        AI_PROVIDER="test-provider",
        AI_API_KEY="not-returned",
        AI_BASE_URL="https://ai.example.test",
        AI_MODEL="test-model",
    )
    def test_configured_adapter_result_is_audited_without_output_leak_in_audit(self):
        self.user.profile.preferences = {"ai_consent": True}
        self.user.profile.save(update_fields=["preferences"])
        with patch(
            "apps.core.ai.OpenAICompatibleAdapter.execute",
            return_value=AIResult(
                status="completed",
                provider="test-provider",
                operation="lead_score",
                output={"score": 82},
            ),
        ):
            response = self.client.post(
                "/apis/core/ai/lead_score/",
                data=json.dumps({"context": {"brief": "A qualified lead"}}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["output"], {"score": 82})
        audit = AuditLog.objects.get(model_name="AIOperation")
        self.assertNotIn("score", audit.changes)
        self.assertNotIn("not-returned", json.dumps(audit.changes))

    @override_settings(AI_PROVIDER="", AI_API_KEY="", AI_BASE_URL="")
    def test_provider_catalog_reports_unconfigured_state(self):
        self.assertEqual(provider_catalog()[0]["configured"], False)
