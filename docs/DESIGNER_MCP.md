# django-fusion interactive MCP designer

The optional designer surface gives an authenticated MCP client a structured way
to explore and draft django-fusion UI primitives without allowing the client to
write project files or execute arbitrary template source.

## Capabilities

| Tool | Purpose | Side effects |
|---|---|---|
| `designer.component_catalog` | Search the registered `{% comp %}` component catalog | Read-only |
| `designer.wagtail_field` | Suggest a Django/Wagtail field or block schema | Returns a draft only |
| `designer.form_scaffold` | Generate a review-only Django form class | Returns code only |
| `designer.table_scaffold` | Generate a review-only `django-tables2` class | Returns code only |
| `designer.validate` | Validate a field, form, or table draft | Read-only |
| `designer.preview` | Render a registered component with JSON props | Read-only |

The JSON shape follows MCP `tools/list` conventions (`inputSchema` and safety
annotations) but does not require the MCP Python SDK. A project may adapt the
same metadata to FastMCP or another MCP transport.

## Project integration

Include the URLs in the owning project's URL configuration:

```python
from django.urls import include, path

urlpatterns = [
    path("fusion/mcp/designer/", include("django_fusion.designer.urls")),
]
```

The endpoints are:

- `POST /fusion/mcp/designer/tools/` — standard JSON-RPC `tools/list`
- `POST /fusion/mcp/designer/call/` — standard JSON-RPC `tools/call`

Both endpoints require an authenticated staff or superuser account. An
application can enable `FUSION_DESIGNER_ALLOW_ANONYMOUS` for a strictly local
development environment, but this must not be enabled on a public deployment.
Use the project's normal authentication, CSRF, origin, and rate-limiting
middleware around any remote deployment.

## JSON-RPC example

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": "design-1",
  "params": {
    "name": "designer.form_scaffold",
    "arguments": {
      "class_name": "NewsletterForm",
      "style_framework": "bootstrap",
      "fields": [
        {"name": "email", "type": "email", "required": true}
      ]
    }
  }
}
```

The result includes generated code and `write_required: true`. The designer does
not persist it. A human or an explicitly approved project workflow must review
permissions, validation, migrations, templates, and tests before writing code.

## Safe preview contract

`designer.preview` accepts only:

1. a component name already present in the django-fusion registry; and
2. JSON-compatible `props`.

It never accepts a template string, filesystem path, Python expression, or
Django template context object. This prevents the designer endpoint from
becoming an SSTI or arbitrary-file-read primitive. Use the full template path
when a bare component alias is ambiguous.

## Recommended workflow for projects

1. **Discover** — browse the component catalog and existing project-owned
   templates.
2. **Model** — ask for a Wagtail field/block recommendation and review its
   ownership, migration, indexing, localization, and permissions.
3. **Draft** — generate a form or table scaffold with the project's preferred
   base class and style framework.
4. **Validate** — call `designer.validate`; then run project checks, migrations,
   accessibility checks, and template tests locally.
5. **Preview** — render only registered components with representative,
   non-sensitive props.
6. **Apply manually** — commit code through the project's normal review path;
   do not grant MCP clients direct filesystem or shell access.

### Project-specific guidance

- **Precis LMS:** keep course, enrollment, progress, and profile fields in the
  Precis backend models. Have the designer produce suggestions only; preserve
  editorial permissions and Wagtail localization rules.
- **Precis Landing:** use the designer for catalog/marketing components and
  newsletter forms, while keeping content and assets project-owned.
- **Formint:** keep business rules, pricing, inventory, and role permissions in
  the relevant Formint edition. Treat generated tables as presentation drafts,
  not authorization boundaries.

## Security and operations checklist

- Require staff/superuser authorization and a protected deployment route.
- Apply authentication, CSRF/origin policy, rate limiting, and audit logging at
  the project boundary.
- Keep `readOnlyHint=true` and `destructiveHint=false` for the current tools.
- Do not expose arbitrary code execution, shell commands, migrations, or file
  writes through this surface.
- Redact secrets and personal data from preview props and audit logs.
- Treat generated code as untrusted until linted, tested, reviewed, and applied
  by a project owner.
- If a future apply tool is needed, make it a separate explicit approval flow
  with a short-lived capability, a diff preview, audit event, and rollback.
