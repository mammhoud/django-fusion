"""
ceptor_ai.newsletter
========================

Newsletter AI enhancement and email marketing tools.

This sub-package provides AI-powered content enhancement and brand-aware
email design.  The AI backend is **optional** — if no AI provider is
configured the enhancer returns the original content unchanged.

Optional ceptorai integration
------------------------------
Set ``RSEAL_AI_BACKEND = "ceptorai"`` in Django settings to route AI calls
through the standalone ``ceptorai`` package instead of the built-in
``ceptor_ai.ai`` integration::

    # settings.py
    RSEAL_AI_BACKEND = "ceptorai"   # requires: pip install ceptorai[openai]

Classes
-------
NewsletterEnhancer
    Enhance subject lines, body copy, and generate A/B variants.
EmailDesigner
    Apply brand styles and generate plain-text versions of HTML emails.

Usage::

    from ceptor_ai.communication.newsletter import NewsletterEnhancer, EmailDesigner

    enhancer = NewsletterEnhancer()
    subject  = enhancer.enhance_subject("Monthly update")
    body     = enhancer.enhance_body(html_body, tone="friendly")

    designer = EmailDesigner()
    branded  = designer.apply_brand_styles(html, brand_config={
        "primary_color": "#2563eb",
        "company_name":  "Acme Corp",
    })
"""

from .designer import EmailDesigner
from .enhancer import NewsletterEnhancer

__all__ = ["NewsletterEnhancer", "EmailDesigner"]
