"""
crafts_ai.ai.newsletter — Newsletter AI enhancement utilities.

Pure Python, zero Django imports.
Provides subject line enhancement, body copy improvement, and A/B variant generation.
"""
from __future__ import annotations

from typing import Any


class NewsletterAI:
    """
    AI-powered newsletter content enhancement.

    No Django dependencies — can be used standalone or via django_rseal.newsletter.enhancer.
    """

    def __init__(self, client: Any = None) -> None:
        self.client = client

    def enhance_subject(self, subject: str, context: dict | None = None) -> str:
        """Return an improved subject line."""
        if self.client is None:
            return subject
        return self.client.complete(
            prompt=f"Improve this email subject line: {subject}",
            context=context or {},
        )

    def enhance_body(self, body: str, context: dict | None = None) -> str:
        """Return improved body copy."""
        if self.client is None:
            return body
        return self.client.complete(
            prompt=f"Improve this newsletter body:\n\n{body}",
            context=context or {},
        )

    def generate_variants(self, subject: str, n: int = 2) -> list[str]:
        """Generate n A/B subject line variants."""
        if self.client is None:
            return [subject] * n
        variants = []
        for i in range(n):
            variant = self.client.complete(
                prompt=f"Write variant {i + 1} of this subject line: {subject}"
            )
            variants.append(variant)
        return variants


__all__ = ["NewsletterAI"]
