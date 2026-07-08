"""Smoke tests for django-rseal modules."""
import pytest


def test_rseal_renderer_import():
    from ceptor_ai.renderer import TemplateRenderer
    renderer = TemplateRenderer()
    assert renderer is not None
    assert hasattr(renderer, "render")
    assert hasattr(renderer, "render_email")
    assert hasattr(renderer, "render_to_response")
    assert hasattr(renderer, "render_component")
    assert hasattr(renderer, "get_default")


def test_rseal_newsletter_import():
    from ceptor_ai.communication.newsletter import EmailDesigner, NewsletterEnhancer
    enhancer = NewsletterEnhancer()
    designer = EmailDesigner()
    assert enhancer is not None
    assert designer is not None


def test_rseal_seeder_import():
    from ceptor_ai.seeder import ModelSeeder, Provider, Seeder
    assert Seeder is not None


def test_rseal_email_models_completeness():
    from ceptor_ai.communication.email.models import EmailLog, EmailTemplate, UserGroup, UserRole
    assert all([EmailLog, EmailTemplate, UserRole, UserGroup])


def test_rseal_ai_import():
    from ceptor_ai.ai.integrations import (
        AIIntegrationRegistry,
        ClaudeIntegration,
        OpenAIIntegration,
    )
    assert "openai" in AIIntegrationRegistry.list_integrations()
    assert "claude" in AIIntegrationRegistry.list_integrations()


def test_django_grep_test_utilities():
    """Test utilities should be implemented in django-fusion or ceptor-ai."""
    # TODO: Implement test utilities (BaseTestCase, UserFactory, etc.) in django-fusion
    # For now, verify ceptor_ai has seeding capabilities
    from ceptor_ai.seeder import Seeder
    assert Seeder is not None
