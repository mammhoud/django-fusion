"""Tests for the in-project AI/MCP/chat services (replaces ceptor_stubs)."""

from __future__ import annotations

import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from .ceptor import (
    AIIntegrationRegistry,
    CeptorAIService,
    CeptorChatService,
    CeptorMCPService,
    ChatBubble,
    CraftsClient,
    _resolve_model_id,
)


@contextmanager
def temp_project(files: dict[str, str]):
    """Context manager creating a temp dir with the given relative files."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel, content in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        yield root


class AIIntegrationRegistryTests(SimpleTestCase):
    def test_list_integrations_reports_real_backends(self):
        backends = AIIntegrationRegistry.list_integrations()
        for expected in ("ollama", "openai", "claude", "gemini"):
            self.assertIn(expected, backends)

    def test_get_returns_real_backend(self):
        backend = AIIntegrationRegistry.get("ollama")
        self.assertEqual(backend.backend, "ollama")
        self.assertEqual(backend.model_id, "gemma3-4b")

    def test_resolve_model_id_honours_explicit_model(self):
        self.assertEqual(_resolve_model_id("ollama", "llama3-8b"), "llama3-8b")
        self.assertEqual(_resolve_model_id("openai", None), "gpt4o")
        self.assertEqual(_resolve_model_id("claude", None), "claude-sonnet")
        self.assertEqual(_resolve_model_id("gemini", None), "gemini-2.5-flash")


class CeptorAIServiceTests(SimpleTestCase):
    def test_generate_delegates_to_real_ai_service(self):
        svc = CeptorAIService()
        with mock.patch(
            "chat.ceptor.AIService.chat", return_value="real reply"
        ) as chat_mock:
            reply = svc.generate("ollama", "Hello")
        self.assertEqual(reply, "real reply")
        chat_mock.assert_called_once()
        args = chat_mock.call_args[0]
        self.assertEqual(args[0], "gemma3-4b")
        self.assertEqual(args[1], [{"role": "user", "content": "Hello"}])

    def test_stream_yields_tokens_from_real_service(self):
        svc = CeptorAIService()
        raw_chunks = [
            '{"type": "token", "content": "Hello"}',
            '{"type": "token", "content": " world"}',
            '{"type": "complete", "content": "Hello world"}',
        ]
        with mock.patch(
            "chat.ceptor.AIService.stream", return_value=iter(raw_chunks)
        ):
            tokens = list(svc.stream("ollama", "Hi"))
        self.assertEqual(tokens, ["Hello", " world"])


class CeptorMCPServiceTests(SimpleTestCase):
    def setUp(self):
        self.mcp = CeptorMCPService()

    def test_list_tools(self):
        self.assertEqual(
            self.mcp.list_tools(),
            ["theme_analyzer", "component_mapper", "config_inspector"],
        )

    def test_unknown_tool_raises(self):
        with self.assertRaises(ValueError):
            self.mcp.run_tool("does_not_exist")

    def test_theme_analyzer_scans_tokens(self):
        with temp_project({"styles.css": ":root { --fu-paper: 60 17% 95%; }"}) as root:
            result = self.mcp.analyze_themes(root=str(root))
        self.assertEqual(result["files_scanned"], 1)
        self.assertIn("--fu-paper", result["tokens"])

    def test_component_mapper_finds_components(self):
        with temp_project({}) as root:
            comp_dir = root / "projects" / "precis-ctc" / "templates" / "components"
            comp_dir.mkdir(parents=True)
            (comp_dir / "card.html").write_text("<div>card</div>", encoding="utf-8")
            result = self.mcp.map_components(
                root=str(root), central="projects/precis-ctc"
            )
        self.assertEqual(result["component_count"], 1)
        self.assertIn("card.html", result["components"][0])

    def test_config_inspector_redacts_values(self):
        with mock.patch.dict(
            os.environ, {"SYNTARA_TEST_FOO": "secret", "SYNTARA_TEST_BAR": "1"}
        ):
            result = self.mcp.inspect_config(prefix="SYNTARA_TEST_")
        self.assertEqual(result["count"], 2)
        self.assertIn("SYNTARA_TEST_FOO", result["variables"])
        self.assertNotIn("secret", result)


class CeptorChatServiceTests(SimpleTestCase):
    def test_health_false_when_server_unreachable(self):
        client = CraftsClient(base_url="http://127.0.0.1:1", timeout=1)
        self.assertFalse(client.health())

    def test_send_message_falls_back_to_local_ai(self):
        chat = CeptorChatService(server_url="http://127.0.0.1:1", timeout=1)
        with mock.patch(
            "chat.ceptor.AIService.chat", return_value="local reply"
        ) as chat_mock:
            reply = chat.send_message("Hello")
        self.assertEqual(reply["text"], "local reply")
        self.assertEqual(reply["role"], "assistant")
        chat_mock.assert_called_once()

    def test_chat_bubble_returns_real_reply(self):
        bubble = ChatBubble(server_url="http://127.0.0.1:1", timeout=1)
        with mock.patch(
            "chat.ceptor.AIService.chat", return_value="fallback reply"
        ):
            reply = bubble.send("Hello")
        self.assertEqual(reply.text, "fallback reply")
        self.assertEqual(reply.role, "assistant")
