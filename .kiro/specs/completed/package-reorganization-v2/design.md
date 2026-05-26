# Design: Package Reorganization v2

## Target Directory Trees

### django-osoul (foundation)

```
libs/django-osoul/
├── assets/cover.png
├── pyproject.toml
├── README.md
└── src/django_osoul/
    ├── __init__.py              # exports BaseModel, TimeStampedModel, UUIDModel, mixins
    ├── py.typed
    ├── rendering.py             # TemplateRenderer (moved from rseal.renderer)
    ├── logging_config.py        # (to move from rseal)
    ├── conf.py / conf_utils.py
    ├── constants.py / enums.py / exceptions.py / typing.py
    ├── routes/                  # ← NEW (from rseal.routes + rseal.pipelines.routes.base)
    │   ├── __init__.py          # Viewset, BaseViewset, route, menu_path, IndexViewMixin
    │   ├── base.py              # full Viewset implementation
    │   └── README.md
    ├── models/
    │   ├── base.py              # BaseModel, TimeStampedModel, UUIDModel
    │   ├── mixins.py            # SoftDeleteMixin, AuditMixin, StatusMixin, UUIDPrimaryKeyModel
    │   ├── managers.py
    │   └── README.md
    ├── views/
    │   ├── mixins.py            # AjaxResponseMixin, JSONResponseMixin, MessageMixin,
    │   │                        # BaseDashboardMixin, BaseCartMixin
    │   └── README.md
    ├── utils/
    │   ├── text.py / responses.py / datetime_utils.py / validators.py / decorators.py
    │   └── README.md
    ├── middlewares/             # ← NEW (from rseal.pipelines.middlewares)
    │   ├── freeze.py / language.py / service.py / site.py
    │   └── README.md
    ├── forms/                   # ← NEW (base form classes from rseal.pipelines.forms)
    │   ├── base.py / mixins.py
    │   └── README.md
    ├── backends/                # ← NEW (from rseal.pipelines.backends)
    │   ├── auth.py
    │   └── README.md
    ├── filters/                 # ← NEW (from rseal.pipelines.filters)
    │   ├── base.py / cache.py / token.py
    │   └── README.md
    ├── managers/                # ← NEW (generic managers from rseal.pipelines.managers)
    │   ├── base.py / search.py / tags.py / token.py / user.py
    │   └── README.md
    ├── mixins/                  # ← NEW (generic mixins from rseal.pipelines.mixins)
    │   ├── cache.py / search.py / service.py / token.py
    │   └── README.md
    ├── contrib/
    │   ├── __init__.py          # DEFAULT, camel_case_to_underscore, utilities
    │   ├── debug_tools/         # ← NEW (from rseal.contrib.debug_tools)
    │   ├── admin_site.py        # ← NEW (from rseal.contrib)
    │   ├── cache.py             # ← NEW (from rseal.contrib)
    │   ├── email_config.py      # ← NEW (from rseal.contrib)
    │   ├── privacy.py           # ← NEW (from rseal.contrib)
    │   ├── choices/
    │   ├── context/             # auth, cookies, htmx, languages, settings
    │   ├── enums/
    │   ├── responses/
    │   ├── schemas/
    │   └── README.md
    ├── comp/                    # Wagtail UI components (wagtail imports allowed here)
    │   ├── adapters/ blocks/ management/ plugins/ site/ templatetags/
    │   └── README.md
    ├── handlers/                # ← NEW (from rseal.handlers)
    ├── scripts/                 # ← NEW (from rseal.scripts)
    ├── management/
    ├── services/
    ├── templatetags/
    └── CI/
```

### django-rseal (automation engine)

```
libs/django-rseal/
├── assets/cover.png
├── pyproject.toml
├── README.md
└── src/django_rseal/
    ├── __init__.py
    ├── py.typed
    ├── exceptions.py / logging_config.py / models.py
    ├── renderer.py              # SHIM → django_osoul.rendering.TemplateRenderer
    ├── ai/
    │   ├── __init__.py          # SHIM → crafts_ai.ai (thin adapter)
    │   └── README.md
    ├── email/
    │   ├── models.py            # EmailLog, EmailTemplate
    │   └── README.md
    ├── email_tools/             # CSV manager, extractor, sender
    ├── services/                # EmailService, BulkEmailService, InvitationService,
    │                            # QueueManager, ReportGenerator
    ├── tasks/                   # Celery + Django-Q task definitions
    ├── newsletter/
    │   ├── designer.py          # EmailDesigner
    │   ├── enhancer.py          # NewsletterEnhancer (delegates to crafts_ai.ai)
    │   └── README.md
    ├── seeder/
    │   ├── __init__.py          # SHIM → django_grep.seeder
    │   └── README.md
    ├── pipelines/
    │   ├── models/              # Person, Team, Campaign, Workspace, etc.
    │   ├── routes/              # domain-specific URL routes
    │   ├── services/            # domain-specific services
    │   ├── site/                # auth/, generic/, users/ views
    │   ├── snippets/            # Wagtail snippets
    │   ├── signals/
    │   ├── migrations/
    │   ├── forms/               # domain-specific forms (auth, newsletter)
    │   └── README.md
    ├── workflows/               # SpecTaskOrchestrator
    ├── mcp_designer/            # Django app wrapper (apps.py, signals.py only)
    ├── management/              # Django management commands
    ├── migrations/              # EmailLog migrations
    ├── templates/               # Email and auth templates
    ├── contrib/
    │   ├── email_admin.py       # Admin for EmailLog
    │   └── README.md
    └── routes/                  # SHIM → django_osoul.routes
```

### nawaai / crafts-ai (standalone AI/MCP)

```
libs/nawaai/
├── assets/cover.png
├── pyproject.toml
├── README.md
├── setup.py
└── crafts_ai/
    ├── __init__.py              # nawa namespace alias
    ├── py.typed
    ├── ai/
    │   ├── __init__.py
    │   ├── integrations.py      # AIIntegration, OpenAIIntegration, ClaudeIntegration,
    │   │                        # AIIntegrationRegistry
    │   ├── newsletter.py        # ← NEW: AI newsletter enhancement (from rseal)
    │   └── README.md
    ├── chat/
    │   ├── __init__.py          # CraftsClient, ChatBubble, RasaClient
    │   ├── client.py            # CraftsClient, ChatBubble
    │   ├── rasa.py              # RasaClient (Rasa Open Source)
    │   └── README.md
    ├── mcp/
    │   ├── __init__.py
    │   ├── server.py            # MCPServer
    │   └── README.md
    ├── seeder/
    │   ├── __init__.py
    │   ├── simple_seeder.py     # SimpleSeeder (no ORM)
    │   ├── providers.py
    │   └── README.md
    └── orchestrator/
        ├── __init__.py          # SpecTaskOrchestrator
        ├── cli.py               # craftsai CLI entry point
        ├── compatibility.py / config.py / errors.py / executor.py
        ├── filter.py / interfaces.py / management.py / models.py
        ├── orchestrator.py / parser.py / pbt.py / progress.py
        ├── scanner.py / tracker.py
        └── README.md
```

### django-grep (testing framework)

```
libs/django-grep/
├── assets/cover.png
├── pyproject.toml
├── pytest.ini
├── conftest.py
├── README.md
├── docs/
│   ├── index.md / usage.md / examples.md / product.md
│   └── README.md
├── src/django_grep/
│   ├── __init__.py
│   ├── py.typed
│   ├── typing.py
│   ├── seeder/                  # ← NEW (moved from django_rseal.seeder)
│   │   ├── __init__.py          # Seeder, ModelSeeder, guessers, providers
│   │   ├── seeder.py
│   │   ├── guessers.py
│   │   ├── providers.py
│   │   ├── exceptions.py
│   │   └── README.md
│   └── tests/
│       ├── __init__.py
│       ├── base.py              # BaseTestCase, BaseAPITestCase
│       ├── factories.py         # ModelFactory
│       ├── assertions.py        # AssertEmailMixin
│       ├── selenium_base.py     # SeleniumTestCase
│       ├── pytest_plugin.py     # auto-registered fixtures
│       ├── fixtures.py
│       ├── mixins.py
│       └── README.md
└── tests/                       # centralized test suite
    ├── __init__.py
    ├── settings.py
    ├── conftest.py              # ← from libs/tests/conftest.py
    ├── test_deduplication_properties.py
    ├── test_osoul/
    │   ├── __init__.py
    │   └── test_osoul_smoke.py  # ← from libs/tests/test_osoul.py
    ├── test_rseal/
    │   ├── __init__.py
    │   ├── test_rseal_smoke.py  # ← from libs/tests/test_rseal.py
    │   ├── test_email.py
    │   ├── test_management_commands.py
    │   ├── test_orchestration.py
    │   ├── test_queue_manager.py
    │   ├── test_services.py
    │   └── test_tasks.py
    └── test_nawaai/
        ├── __init__.py
        └── test_crafts_ai.py   # ← from libs/tests/test_craftsai.py
```

---

## Namespace Map

| Namespace | Package | Purpose |
|-----------|---------|---------|
| `django_osoul` | django-osoul | Foundation: models, utils, routes, comp/ |
| `django_osoul.routes` | django-osoul | Viewset-based URL routing |
| `django_osoul.rendering` | django-osoul | TemplateRenderer |
| `django_osoul.middlewares` | django-osoul | Request middlewares |
| `django_osoul.forms` | django-osoul | Base form classes |
| `django_osoul.backends` | django-osoul | Auth backends |
| `django_osoul.filters` | django-osoul | Request filters |
| `django_osoul.managers` | django-osoul | Generic ORM managers |
| `django_osoul.mixins` | django-osoul | Generic view mixins |
| `django_osoul.contrib` | django-osoul | Utilities, debug tools, context processors |
| `django_osoul.comp` | django-osoul | Wagtail UI components |
| `django_rseal` | django-rseal | Automation: email, tasks, newsletter |
| `django_rseal.email` | django-rseal | EmailLog, EmailTemplate models |
| `django_rseal.services` | django-rseal | EmailService, BulkEmailService |
| `django_rseal.newsletter` | django-rseal | EmailDesigner, NewsletterEnhancer |
| `django_rseal.pipelines` | django-rseal | Domain models, views, routes |
| `django_rseal.workflows` | django-rseal | SpecTaskOrchestrator |
| `django_rseal.seeder` | django-rseal | SHIM → django_grep.seeder |
| `django_rseal.renderer` | django-rseal | SHIM → django_osoul.rendering |
| `django_rseal.ai` | django-rseal | SHIM → crafts_ai.ai |
| `crafts_ai` | nawaai | Standalone AI/MCP toolkit |
| `crafts_ai.ai` | nawaai | AI integrations (OpenAI, Claude, Rasa) |
| `crafts_ai.chat` | nawaai | CraftsClient, ChatBubble, RasaClient |
| `crafts_ai.mcp` | nawaai | MCPServer |
| `crafts_ai.seeder` | nawaai | SimpleSeeder (no ORM) |
| `crafts_ai.orchestrator` | nawaai | Spec task orchestration + CLI |
| `django_grep` | django-grep | Testing framework |
| `django_grep.seeder` | django-grep | Django ORM seeder (from rseal) |
| `django_grep.tests` | django-grep | BaseTestCase, factories, assertions |

---

## Dependency Graph

```
stdlib / Django
    └── django-osoul          (foundation — Django + stdlib + Wagtail in comp/)
            └── django-rseal  (automation — wagtail, celery, faker)
                    └── crafts-ai (optional AI backend)

crafts-ai                     (standalone — no Django)

django-grep                   (testing)
    ├── django-osoul
    ├── django-rseal
    └── crafts-ai (optional)
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/libs/run_tests.sh` | Run full test suite from django-grep |
| `scripts/libs/check_boundaries.sh` | Verify package boundary rules |
| `scripts/libs/scan_imports.py` | Report all boundary violations |
| `scripts/libs/move_seeder.sh` | Migrate seeder rseal → grep |
| `scripts/libs/generate_namespace_docs.py` | Write README.md at every package dir |

---

## Correctness Properties

1. `django_osoul` (excl. comp/) has zero wagtail/celery/AI/rseal imports
2. `crafts_ai` has zero Django imports
3. `django_rseal` has zero `django_grep` imports
4. `django_grep.seeder` exports same API as old `django_rseal.seeder`
5. All tests pass from `libs/django-grep/`
6. `libs/tests/` directory does not exist after migration
7. Every Python package directory has a README.md
