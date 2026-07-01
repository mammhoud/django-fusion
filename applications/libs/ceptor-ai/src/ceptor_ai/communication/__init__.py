"""Communication domain — email, newsletter, chat, and async task execution.

Sub-packages
------------
communication.email         Email service, queue manager, CSV pipeline, template selector.
communication.chat          Chat bubble client, Rasa NLU connector, Django chat app.
communication.newsletter    Newsletter designer, content enhancer, subscriber management.
communication.tasks         Async task runners (Celery and Django-Q backends).

Usage::

    from ceptor_ai.communication.email.services.services import EmailService
    from ceptor_ai.communication.chat import ChatBubble
    from ceptor_ai.communication.newsletter.designer import NewsletterDesigner
"""
