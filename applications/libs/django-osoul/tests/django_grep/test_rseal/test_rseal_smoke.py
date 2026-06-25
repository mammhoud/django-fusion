"""Smoke tests for django-rseal modules."""
import pytest


def test_rseal_renderer_import():
    from crafts_ai.renderer import TemplateRenderer
    renderer = TemplateRenderer()
    assert renderer is not None
    assert hasattr(renderer, "render")
    assert hasattr(renderer, "render_email")
    assert hasattr(renderer, "render_to_response")
    assert hasattr(renderer, "render_component")
    assert hasattr(renderer, "get_default")


def test_rseal_newsletter_import():
    from crafts_ai.communication.newsletter import EmailDesigner, NewsletterEnhancer
    enhancer = NewsletterEnhancer()
    designer = EmailDesigner()
    assert enhancer is not None
    assert designer is not None


def test_rseal_seeder_import():
    from django_grep.seeder import ModelSeeder, Provider, Seeder
    assert Seeder is not None


def test_rseal_email_models_completeness():
    from crafts_ai.communication.email.models import EmailLog, EmailTemplate, UserGroup, UserRole
    assert all([EmailLog, EmailTemplate, UserRole, UserGroup])


def test_rseal_ai_import():
    from crafts_ai.ai.integrations import (
        AIIntegrationRegistry,
        ClaudeIntegration,
        OpenAIIntegration,
    )
    assert "openai" in AIIntegrationRegistry.list_integrations()
    assert "claude" in AIIntegrationRegistry.list_integrations()


def test_django_grep_test_utilities():
    """Verify django-grep test utilities are importable."""
    from django_grep.tests.base import BaseAPITestCase, BaseTestCase
    from django_grep.tests.fixtures import UserFactory, create_test_user
    from django_grep.tests.mixins import AssertEmailMixin, AssertHTMLMixin
    assert BaseTestCase is not None
    assert UserFactory is not None
