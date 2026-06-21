"""
django_rseal.newsletter.enhancer
==================================

AI-powered newsletter content enhancement.

The enhancer works with **two interchangeable AI backends**:

1. ``django_rseal.ai`` (built-in, Django-integrated) — default.
2. ``craftsai.ai`` (optional, standalone) — used when
   ``RSEAL_AI_BACKEND = "craftsai"`` is set in Django settings, or when
   ``backend="craftsai"`` is passed to the constructor.

This makes ``craftsai`` an **optional** dependency: if it is not installed
the enhancer falls back to the built-in rseal AI integration silently.

Classes
-------
NewsletterEnhancer
    Enhance subject lines, body copy, and generate A/B variants using AI.

Usage::

    from django_rseal.communication.newsletter.enhancer import NewsletterEnhancer

    # Default — uses django_rseal.ai (OpenAI or Claude via Django settings)
    enhancer = NewsletterEnhancer()
    subject  = enhancer.enhance_subject("Monthly product update")
    body     = enhancer.enhance_body(html_body, tone="friendly")
    variants = enhancer.generate_subject_variants("New feature launch", count=3)

    # Optional craftsai backend
    enhancer = NewsletterEnhancer(backend="craftsai", api_key="sk-...")
    subject  = enhancer.enhance_subject("Monthly product update")
"""

from __future__ import annotations

import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


def _get_ai_registry(backend: str):
    """
    Return the AIIntegrationRegistry for the requested *backend*.

    Args:
        backend: ``"rseal"`` (default) or ``"craftsai"``.

    Returns:
        An ``AIIntegrationRegistry`` class, or ``None`` if unavailable.
    """
    if backend == "craftsai":
        try:
            from craftsai.ai.integrations import AIIntegrationRegistry  # noqa: PLC0415
            return AIIntegrationRegistry
        except ImportError:
            logger.warning(
                "craftsai is not installed. "
                "AI features will be unavailable. "
                "Install it with: pip install craftsai[openai]"
            )
            return None

    # Default: try craftsai first (nawaai), then fall back to rseal's re-export
    try:
        from craftsai.ai.integrations import AIIntegrationRegistry  # noqa: PLC0415
        return AIIntegrationRegistry
    except ImportError:
        try:
            from django_rseal.ai.integrations import AIIntegrationRegistry  # noqa: PLC0415
            return AIIntegrationRegistry
        except ImportError:
            logger.warning(
                "No AI backend available. "
                "Install craftsai with: pip install craftsai[openai]"
            )
            return None


class NewsletterEnhancer:
    """
    Enhance newsletter content using an AI integration.

    The AI backend is resolved in this order:

    1. ``backend`` constructor argument.
    2. ``RSEAL_AI_BACKEND`` Django setting (``"rseal"`` or ``"craftsai"``).
    3. Falls back to ``"rseal"`` (built-in).

    Args:
        ai_provider: AI provider name registered in the registry
            (e.g. ``"openai"``, ``"claude"``).  Defaults to ``"openai"``.
        api_key: API key for the provider.  If ``None`` the provider reads
            from its environment variable (``OPENAI_API_KEY`` etc.).
        backend: ``"rseal"`` or ``"craftsai"``.  Overrides the Django setting.

    Usage::

        enhancer = NewsletterEnhancer()
        better   = enhancer.enhance_subject("Our latest news")
    """

    def __init__(
        self,
        ai_provider: str = "openai",
        api_key: Optional[str] = None,
        backend: Optional[str] = None,
    ):
        self.ai_provider = ai_provider
        self.api_key = api_key
        self._backend = backend or getattr(settings, "RSEAL_AI_BACKEND", "rseal")
        self._ai = None

    def _get_ai(self):
        """Lazily initialise the AI integration instance."""
        if self._ai is None:
            registry = _get_ai_registry(self._backend)
            if registry is None:
                logger.warning("No AI registry available — AI features disabled.")
                return None
            try:
                self._ai = registry.get(self.ai_provider, api_key=self.api_key)
            except Exception as exc:
                logger.warning("AI backend unavailable: %s", exc)
        return self._ai

    def enhance_subject(self, subject: str, context: Optional[dict] = None) -> str:
        """
        Improve an email subject line using AI.

        Falls back to the original *subject* if AI is unavailable.

        Args:
            subject: The original subject line.
            context: Optional extra context dict passed to the AI prompt.

        Returns:
            Improved subject line string.

        Example::

            enhancer.enhance_subject("Monthly update", context={"product": "Acme"})
        """
        ai = self._get_ai()
        if not ai:
            return subject
        prompt = (
            "Improve this email subject line to be more engaging and clickable. "
            "Return only the improved subject, nothing else.\n\n"
            f"Original: {subject}"
        )
        if context:
            prompt += f"\nContext: {context}"
        try:
            return ai.generate(prompt).strip()
        except Exception as exc:
            logger.error("Subject enhancement failed: %s", exc)
            return subject

    def enhance_body(self, body: str, tone: str = "professional") -> str:
        """
        Improve email body copy using AI.

        Falls back to the original *body* if AI is unavailable.

        Args:
            body: Raw HTML or plain-text email body.
            tone: Desired tone — e.g. ``"professional"``, ``"friendly"``,
                ``"urgent"``.

        Returns:
            Enhanced body string (preserves HTML structure if present).

        Example::

            enhancer.enhance_body("<p>Hello…</p>", tone="friendly")
        """
        ai = self._get_ai()
        if not ai:
            return body
        prompt = (
            f"Improve this email body content. Tone: {tone}. "
            "Keep HTML structure if present. Return only the improved content.\n\n"
            f"{body}"
        )
        try:
            return ai.generate(prompt).strip()
        except Exception as exc:
            logger.error("Body enhancement failed: %s", exc)
            return body

    def generate_subject_variants(self, topic: str, count: int = 3) -> list[str]:
        """
        Generate multiple subject line variants for A/B testing.

        Falls back to ``[topic]`` if AI is unavailable.

        Args:
            topic: The email topic or campaign name.
            count: Number of variants to generate (default ``3``).

        Returns:
            List of subject line strings (up to *count* items).

        Example::

            variants = enhancer.generate_subject_variants("Black Friday sale", count=5)
        """
        ai = self._get_ai()
        if not ai:
            return [topic]
        prompt = (
            f"Generate {count} different email subject lines for this topic. "
            "Return one per line, no numbering.\n\n"
            f"Topic: {topic}"
        )
        try:
            result = ai.generate(prompt).strip()
            return [line.strip() for line in result.split("\n") if line.strip()][:count]
        except Exception as exc:
            logger.error("Subject variant generation failed: %s", exc)
            return [topic]

    def personalize_content(self, template: str, recipient_data: dict) -> str:
        """
        Replace ``{{key}}`` placeholders in *template* with *recipient_data* values.

        This is a simple string-substitution personalisation — no AI call is made.

        Args:
            template: Template string with ``{{field_name}}`` placeholders.
            recipient_data: Mapping of placeholder names to replacement values.

        Returns:
            Personalised string.

        Example::

            enhancer.personalize_content(
                "Hi {{name}}, your order {{order_id}} is ready.",
                {"name": "Alice", "order_id": "ORD-42"},
            )
        """
        content = template
        for key, value in recipient_data.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return content
