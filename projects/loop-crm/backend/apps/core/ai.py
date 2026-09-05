"""Provider-neutral AI hub for Loop-CRM.

The hub deliberately owns the policy boundary, not a vendor SDK: workspaces
must opt in before an operation can run, provider credentials remain in the
server environment, and an unconfigured adapter returns an honest deferred
result. The three supported operations are lead scoring, sales-email drafting,
and social-post drafting.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings

AI_OPERATIONS: tuple[dict[str, str], ...] = (
    {
        "id": "lead_score",
        "label": "Score a lead",
        "description": "Assess fit and buying intent from a contact or deal brief.",
    },
    {
        "id": "draft_sales_email",
        "label": "Draft a sales email",
        "description": "Create a reviewable first draft for a contact or opportunity.",
    },
    {
        "id": "draft_social_post",
        "label": "Draft a social post",
        "description": "Turn a campaign brief into a post ready for human approval.",
    },
)

_OPERATION_IDS = {operation["id"] for operation in AI_OPERATIONS}


@dataclass(frozen=True)
class AIResult:
    status: str
    provider: str
    operation: str
    output: dict[str, Any] | None = None
    reason: str = ""


class AIAdapter(Protocol):
    provider: str

    def execute(self, operation: str, prompt: str) -> AIResult: ...


class UnconfiguredAIAdapter:
    provider = "unconfigured"

    def execute(self, operation: str, prompt: str) -> AIResult:
        # ``prompt`` is intentionally unused: an unconfigured workspace must
        # never accidentally send sensitive CRM context anywhere.
        del prompt
        return AIResult(
            status="deferred",
            provider=self.provider,
            operation=operation,
            reason="No AI provider is configured for this deployment.",
        )


class OpenAICompatibleAdapter:
    """Small stdlib adapter for providers exposing /chat/completions.

    This is opt-in through environment variables and is intentionally isolated
    from views and workflow actions. A provider SDK is not required for the
    local contract, and no key is ever included in a response or audit row.
    """

    def __init__(self, provider: str, base_url: str, api_key: str, model: str) -> None:
        self.provider = provider
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model

    def execute(self, operation: str, prompt: str) -> AIResult:
        body = json.dumps(
            {
                "model": self.model,
                "temperature": 0.2,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a Loop CRM assistant. Return valid JSON only. "
                            "Do not invent facts; mark missing context as unknown."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            }
        ).encode("utf-8")
        request = Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=20) as response:  # noqa: S310 - URL is operator-configured
                payload = json.loads(response.read().decode("utf-8"))
            content = payload.get("choices", [{}])[0].get("message", {}).get("content", "")
            try:
                output = json.loads(content)
            except (TypeError, ValueError):
                output = {"text": str(content)}
            return AIResult(status="completed", provider=self.provider, operation=operation, output=output)
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            return AIResult(
                status="failed",
                provider=self.provider,
                operation=operation,
                reason=f"Provider request failed: {exc.__class__.__name__}.",
            )


def provider_configured() -> bool:
    return bool(
        getattr(settings, "AI_PROVIDER", "").strip()
        and getattr(settings, "AI_API_KEY", "").strip()
        and getattr(settings, "AI_BASE_URL", "").strip()
    )


def provider_catalog() -> list[dict[str, Any]]:
    provider = getattr(settings, "AI_PROVIDER", "").strip() or "unconfigured"
    return [
        {
            "id": provider,
            "label": provider.replace("_", " ").title(),
            "configured": provider_configured(),
            "transport": "OpenAI-compatible chat completions" if provider_configured() else "none",
        }
    ]


def adapter() -> AIAdapter:
    if not provider_configured():
        return UnconfiguredAIAdapter()
    return OpenAICompatibleAdapter(
        getattr(settings, "AI_PROVIDER", "configured"),
        getattr(settings, "AI_BASE_URL", ""),
        getattr(settings, "AI_API_KEY", ""),
        getattr(settings, "AI_MODEL", "loop-crm-default"),
    )


def operation_catalog() -> list[dict[str, str]]:
    return [dict(operation) for operation in AI_OPERATIONS]


def build_prompt(operation: str, context: dict[str, Any]) -> str:
    """Build a bounded, provider-neutral prompt from caller-supplied context."""
    if operation not in _OPERATION_IDS:
        raise ValueError("Unknown AI operation.")
    safe_context = json.dumps(context, ensure_ascii=True, sort_keys=True)[:12_000]
    instructions = {
        "lead_score": "Return score 0-100, fit_reasons, intent_signals, risks, and next_step.",
        "draft_sales_email": "Return subject, body, assumptions, and review_notes. Never claim an action happened.",
        "draft_social_post": "Return post, hashtags, assumptions, and review_notes. Keep it ready for human approval.",
    }
    return f"Operation: {operation}\n{instructions[operation]}\nCRM context:\n{safe_context}"


def run_operation(operation: str, context: dict[str, Any]) -> AIResult:
    prompt = build_prompt(operation, context)
    return adapter().execute(operation, prompt)


def consent_enabled(profile) -> bool:
    return bool((getattr(profile, "preferences", {}) or {}).get("ai_consent"))


def set_consent(profile, enabled: bool) -> None:
    preferences = dict(profile.preferences or {})
    preferences["ai_consent"] = bool(enabled)
    profile.preferences = preferences
    profile.save(update_fields=["preferences"])


__all__ = [
    "AIResult",
    "AI_OPERATIONS",
    "adapter",
    "build_prompt",
    "consent_enabled",
    "operation_catalog",
    "provider_catalog",
    "provider_configured",
    "run_operation",
    "set_consent",
]
