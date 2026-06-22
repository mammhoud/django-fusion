"""Framework-agnostic Ollama client services."""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import httpx


Message = Mapping[str, str]
TaskMap = Mapping[str, str]


@dataclass(slots=True)
class OllamaService:
    """Small Ollama API client with multi-model task routing support."""

    base_url: str = "http://localhost:11434"
    default_model: str = "gemma3:4b"
    timeout: float = 60.0
    task_models: TaskMap = field(default_factory=dict)
    mcp_context: Sequence[Mapping[str, Any]] = field(default_factory=tuple)

    def model_for_task(self, task: str | None = None, model: str | None = None) -> str:
        """Resolve an explicit, task-specific, or default Ollama model name."""
        if model:
            return model
        if task and task in self.task_models:
            return self.task_models[task]
        return self.default_model

    def with_mcp_context(self, context: Iterable[Mapping[str, Any]]) -> "OllamaService":
        """Return a copy of the service with MCP tool/context metadata attached."""
        return OllamaService(
            base_url=self.base_url,
            default_model=self.default_model,
            timeout=self.timeout,
            task_models=dict(self.task_models),
            mcp_context=tuple(context),
        )

    def payload(
        self,
        messages: Sequence[Message],
        *,
        task: str | None = None,
        model: str | None = None,
        stream: bool = False,
        options: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build an Ollama chat payload including optional MCP metadata."""
        data: dict[str, Any] = {
            "model": self.model_for_task(task=task, model=model),
            "messages": list(messages),
            "stream": stream,
        }
        if options:
            data["options"] = dict(options)
        if self.mcp_context:
            data["tools"] = list(self.mcp_context)
        return data

    def chat(
        self,
        messages: Sequence[Message],
        *,
        task: str | None = None,
        model: str | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> str:
        """Run a non-streaming chat completion and return assistant text."""
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url.rstrip('/')}/api/chat",
                json=self.payload(messages, task=task, model=model, options=options),
            )
            response.raise_for_status()
            data = response.json()
        return str(data.get("message", {}).get("content", ""))

    def stream_chat(
        self,
        messages: Sequence[Message],
        *,
        task: str | None = None,
        model: str | None = None,
        options: Mapping[str, Any] | None = None,
    ) -> Iterator[str]:
        """Yield streaming chat tokens from Ollama."""
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream(
                "POST",
                f"{self.base_url.rstrip('/')}/api/chat",
                json=self.payload(
                    messages,
                    task=task,
                    model=model,
                    stream=True,
                    options=options,
                ),
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    data = json.loads(line)
                    token = data.get("message", {}).get("content")
                    if token:
                        yield str(token)
