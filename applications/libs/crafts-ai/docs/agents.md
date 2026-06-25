# crafts-ai Agent and Customizer Guide

## Merged package structure

`crafts-ai` now ships all runtime code from `src/crafts_ai/`. Former `crafts-ai` modules are available under the merged `crafts_ai` namespace, and new AI-facing customizer and MCP tools live in `crafts_ai.customizer` and `crafts_ai.mcp`.

## Template/component inventory workflow

Agents should scan these template roots for every site:

- `applications/assets/templates/`
- `applications/ctc-research/assets/templates/` and `applications/ctc-research/templates/`
- `applications/lms-demo/assets/templates/` and `applications/lms-demo/templates/`
- `applications/VResume/assets/templates/` and `applications/VResume/templates/`

For each template, collect:

- Included components (`{% include %}` and `{% comp %}` tags).
- Required data fields (`{{ field }}` expressions and context variables passed to includes/components).
- Optional style hooks (CSS classes and IDs).

## Component selection rules

When user input asks for a page or component, the agent must:

1. Extract required data fields from the request.
2. Prefer the component whose expected data set exactly matches all required fields.
3. If no exact match exists, choose the component with the closest field overlap and list the missing fields.
4. Prefer central `ctc-research` components over website-specific copies when the field match is equal.
5. Generate or update `.kilo/agent/*.json` configs with component path, default model, viewset, and cache TTL.

## BEM customizer workflow

The customizer scans page templates, landing pages, component templates, `theme/`, and `assets/static/styles/`. It extracts every `class="..."`, `id="..."`, `.class`, and `#id`, maps them to strict `Block__Element--Modifier` names, and rewrites templates and SCSS together so markup and styles stay synchronized. Agents should reuse the same BEM block name for related components to preserve visual consistency.

## Wagtail data model pattern

When a component needs new data, add fields to the relevant Wagtail page/snippet model and expose them in the component context:

```python
class FeaturePage(Page):
    feature_title = models.CharField(max_length=120)
    feature_summary = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("feature_title"),
        FieldPanel("feature_summary"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["feature_component"] = {
            "title": self.feature_title,
            "summary": self.feature_summary,
        }
        return context
```

Use exact field names whenever possible so component matching can prioritize components with the full required data set.


## MCP metadata endpoints

`crafts_ai.mcp_server` is the source of truth for framework-agnostic MCP
metadata. Keep these endpoints synchronized with `docs/ai/latest_features.md`
and `docs/ai/mcp_reference.md`:

- `/health` for readiness checks.
- `/info` for shared package metadata.
- `/features` for the latest AI/MCP feature inventory.
- `/file-structure` for canonical package, docs, and Kilo paths.

Do not import Django, Wagtail, Celery, databases, or website modules in the MCP
metadata module. Optional dependencies must use `importlib.util.find_spec` and
`importlib.import_module`.
