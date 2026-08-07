from django.test import TestCase

from .models import Conversation


class ConversationContextTests(TestCase):
    """Regression tests for bounded, chronological chat context."""

    def test_context_uses_latest_messages_in_chronological_order(self):
        conversation = Conversation.objects.create(title="Context test")
        for content in ("one", "two", "three", "four"):
            conversation.messages.create(content=content, is_user=True)

        context = conversation.get_context_messages(limit=2)

        self.assertEqual([message.content for message in context], ["three", "four"])

    def test_context_with_non_positive_limit_is_empty(self):
        conversation = Conversation.objects.create(title="Empty context")
        conversation.messages.create(content="one", is_user=True)

        self.assertEqual(conversation.get_context_messages(limit=0), [])
        self.assertEqual(conversation.get_context_messages(limit=-1), [])
