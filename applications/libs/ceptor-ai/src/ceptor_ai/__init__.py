"""ceptor-ai — AI, MCP, content, and UI toolkit for structa.cloud.

Package layout
--------------
ceptor_ai.ai                AI provider integrations (Ollama, newsletter AI).
ceptor_ai.communication     Messaging: email processing, newsletter, chat.
  .email                    Email service, queue, template selector, CSV pipeline.
  .chat                     Chat bubble client, Rasa NLU connector, Django app.
  .newsletter               Newsletter designer, subscriber management.
  .tasks                    Async task runners (Celery, Django-Q).
ceptor_ai.content           CMS content layer — blocks, models, snippets, views.
  .blocks                   Wagtail StreamField blocks (contact, media, pages).
  .models                   Django models (contacts, newsletter, settings, users).
  .snippets                 Wagtail snippets (manage, site, newsletter).
  .site                     Auth views, payment hooks, search, notifications.
  .extraction               HTML component extraction utilities.
  .seeder                   Deterministic DB seeder for dev/test environments.
ceptor_ai.transport         HTTP transport layer — middleware, signals, handlers.
  .middlewares              Privacy-consent and request middleware.
  .signals                  User lifecycle, invitation, and notification signals.
  .handlers                 Wagtail hooks and blog/manage model stubs.
ceptor_ai.ui                UI tooling — BEM conversion, SCSS watchers, viewsets.
ceptor_ai.tools             Developer tools — migration analysis, project inventory.
  .migration                Rule-based import classification and migration plans.
  .inventory                Workspace package and project discovery.
ceptor_ai.orchestrator      Autonomous task orchestration engine (parser, executor).
ceptor_ai.mcp               Model Context Protocol server integration.
ceptor_ai.contrib           Shared admin, cache, privacy, and signal helpers.
ceptor_ai.base              Core app config, settings conf, and integration hooks.
ceptor_ai.services          Service layer: email, commerce, communication, content.
ceptor_ai.workflows         Temporal workflow definitions and activities.
ceptor_ai.templatetags      Django template tags (chat bubble, breadcrumbs, gallery).

Deprecated paths (compat shims kept for backward compatibility)
---------------------------------------------------------------
ceptor_ai.chat              -> ceptor_ai.communication.chat
ceptor_ai.http              -> ceptor_ai.transport
ceptor_ai.customizer        -> ceptor_ai.ui
ceptor_ai.components        -> ceptor_ai.content.extraction
ceptor_ai.seeder            -> ceptor_ai.content.seeder
ceptor_ai.rseal             -> ceptor_ai.tools.migration
ceptor_ai.projects          -> ceptor_ai.tools.inventory
"""

from __future__ import annotations

from .cli import package_info
from .tools.migration import (
    RSEAL_IMPORT_RULES,
    ImportRule,
    MigrationItem,
    classify_import,
    migration_plan,
)

__version__ = "0.1.0"

__all__ = [
    "ImportRule",
    "MigrationItem",
    "RSEAL_IMPORT_RULES",
    "classify_import",
    "migration_plan",
    "package_info",
]
