"""
crafts_ai.chat.rasa
====================

Optional Rasa Open Source integration.

Requires: ``pip install nawaai[rasa]`` (installs ``requests`` or uses stdlib urllib).

Classes
-------
RasaMessage
    Parsed response from the Rasa REST channel.
RasaClient
    Client for the Rasa Open Source REST API (``/webhooks/rest/webhook``).

Usage::

    from crafts_ai.chat import RasaClient

    rasa = RasaClient(rasa_url="http://localhost:5005")
    response = rasa.send_message(
        sender="user_123",
        message="Book a meeting for tomorrow at 3pm",
    )
    print(response.text)
    print(response.intent)    # "book_meeting"
    print(response.entities)  # [{"entity": "time", "value": "tomorrow at 3pm"}]
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RasaMessage:
    """Parsed response from the Rasa REST channel."""

    text: str
    sender: str = ""
    intent: Optional[str] = None
    intent_confidence: float = 0.0
    entities: List[Dict[str, Any]] = field(default_factory=list)
    buttons: List[Dict[str, Any]] = field(default_factory=list)
    image: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


class RasaClient:
    """
    Client for the Rasa Open Source REST API.

    Connects to the Rasa REST channel (``/webhooks/rest/webhook``) and
    optionally the NLU parse endpoint (``/model/parse``) for intent/entity
    extraction.

    Args:
        rasa_url: Base URL of the Rasa server (e.g. ``"http://localhost:5005"``).
        timeout: Request timeout in seconds (default 30).
        token: Optional Rasa JWT token for authenticated servers.

    Usage::

        rasa = RasaClient(rasa_url="http://localhost:5005")

        # Send a message and get a response
        reply = rasa.send_message(sender="user_1", message="Hello")
        print(reply.text)

        # Parse intent and entities without sending to dialogue
        parsed = rasa.parse("Book a flight to Paris tomorrow")
        print(parsed.intent, parsed.entities)
    """

    def __init__(
        self,
        rasa_url: str = "http://localhost:5005",
        timeout: int = 30,
        token: Optional[str] = None,
    ):
        self.rasa_url = rasa_url.rstrip("/")
        self.timeout = timeout
        self.headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def _post(self, path: str, data: Dict[str, Any]) -> Any:
        """POST JSON to the Rasa server and return parsed response."""
        url = f"{self.rasa_url}{path}"
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8") if exc.fp else ""
            logger.error("RasaClient HTTP %s → %d: %s", url, exc.code, raw)
            raise
        except urllib.error.URLError as exc:
            logger.error("RasaClient connection error %s: %s", url, exc.reason)
            raise

    def send_message(self, sender: str, message: str) -> RasaMessage:
        """
        Send a message to the Rasa REST channel and return the response.

        Args:
            sender: Unique sender/session identifier.
            message: User message text.

        Returns:
            :class:`RasaMessage` with the bot's reply.
        """
        payload = {"sender": sender, "message": message}
        responses = self._post("/webhooks/rest/webhook", payload)

        if not responses:
            return RasaMessage(text="", sender=sender)

        # Rasa returns a list of response objects; merge text responses
        texts = [r.get("text", "") for r in responses if r.get("text")]
        buttons = []
        image = None
        for r in responses:
            buttons.extend(r.get("buttons", []))
            if r.get("image"):
                image = r["image"]

        return RasaMessage(
            text=" ".join(texts),
            sender=sender,
            buttons=buttons,
            image=image,
            raw={"responses": responses},
        )

    def parse(self, text: str, model_id: Optional[str] = None) -> RasaMessage:
        """
        Parse a message for intent and entities without triggering dialogue.

        Calls the Rasa NLU ``/model/parse`` endpoint.

        Args:
            text: Text to parse.
            model_id: Optional model ID to use.

        Returns:
            :class:`RasaMessage` with ``intent``, ``intent_confidence``,
            and ``entities`` populated.
        """
        payload: Dict[str, Any] = {"text": text}
        if model_id:
            payload["model_id"] = model_id

        data = self._post("/model/parse", payload)

        intent_data = data.get("intent", {})
        entities = data.get("entities", [])

        return RasaMessage(
            text=text,
            intent=intent_data.get("name"),
            intent_confidence=intent_data.get("confidence", 0.0),
            entities=entities,
            raw=data,
        )

    def health(self) -> bool:
        """Return True if the Rasa server is reachable."""
        try:
            url = f"{self.rasa_url}/health"
            req = urllib.request.Request(url, headers=self.headers, method="GET")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("status") == "ok"
        except Exception:
            return False

    def get_tracker(self, sender: str) -> Dict[str, Any]:
        """
        Retrieve the conversation tracker for a sender.

        Args:
            sender: Sender/session identifier.

        Returns:
            Tracker dict from Rasa.
        """
        url = f"{self.rasa_url}/conversations/{sender}/tracker"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            logger.error("RasaClient.get_tracker error: %s", exc)
            return {}
