# Dynamic Template Field System

> **Status:** Implemented ✅ · **Version:** 1.0
> **Location:** `docs/features/template-fields/` (spec) +
> `libs/django-fusion/src/django_fusion/template_fields/` (engine)

A reusable system for rendering user-authored templates with inline
variable placeholders (`{{ customer.name }}`, `{{ order.total }}`)
against live data. Designed for emails, invoices, receipts, and
notifications across all Structa Cloud products — and the content-values
layer of the Landing Builder (`django_fusion.builder`).

## Guides

| # | Guide | Description |
|---|---|---|
| 1 | [Architecture](01-architecture.md) | System layers, request lifecycle, integration with django-fusion |
| 2 | [Data Models](02-models.md) | FieldReference, ResolvedValue, ValidationIssue, FilterRegistry, TemplateSchema |
| 3 | [Rendering Workflow](03-rendering-workflow.md) | Parse → Resolve → Validate → Escape → Format → Assemble → Preview |
| 4 | [Security & Validation](04-security-validation.md) | Threat model, security controls, permission model, audit logging |
| 5 | [Examples](05-examples.md) | Real templates with context data and rendered output per product |

## Quick reference

### Variable syntax

```
{{ object.field }}                    simple field
{{ object.nested.field }}             nested access
{{ object.field|filter }}             apply filter
{{ object.field|filter:"arg" }}       filter with argument
{{ object.field|default:"fallback" }} fallback if unresolved
{{ object.field|filter1|filter2 }}    chained filters
```

### Built-in filters

| Filter | Example | Output |
|---|---|---|
| `currency` | `{{ order.total\|currency:"USD" }}` | `$99.50` |
| `date` | `{{ created\|date:"M d, Y" }}` | `Jan 15, 2024` |
| `upper` | `{{ name\|upper }}` | `ACME CORP` |
| `lower` | `{{ email\|lower }}` | `alice@acme.com` |
| `title` | `{{ name\|title }}` | `Premium Coffee` |
| `truncate` | `{{ text\|truncate:30 }}` | `A very long title th…` |
| `default` | `{{ company\|default:"N/A" }}` | `N/A` |
| `yesno` | `{{ is_paid\|yesno:"Paid,Pending" }}` | `Paid` |
| `phone` | `{{ phone\|phone:"+1" }}` | `+1 (555) 123-4567` |
| `length` | `{{ items\|length }}` | `3` |
| `join` | `{{ tags\|join:", " }}` | `coffee, tea, milk` |
| `linebreaks` | `{{ msg\|linebreaks }}` | `<p>line1</p><p>line2</p>` |
| `url_encode` | `{{ url\|url_encode }}` | `hello%20world` |

### Security guarantees

- **Auto-escape** — all values HTML-escaped, no raw passthrough
- **Sandboxed** — no eval/exec, dotted-path resolution only
- **Allowlist** — only declared root objects can be accessed
- **Length limits** — lists and strings bounded to prevent DoS
- **URL sanitization** — `javascript:`, `data:`, `vbscript:` stripped
- **Fail-safe** — unresolved variables produce fallback or empty, never crash

### Product usage

| Product | Use case | Example variables |
|---|---|---|
| POS | Invoice, receipt | `{{ company.name }}`, `{{ invoice.number }}`, `{{ order.total }}` |
| CRM | Email templates, merge fields | `{{ customer.name }}`, `{{ deal.value }}`, `{{ agent.name }}` |
| LMS | Certificates, enrollment emails | `{{ student.name }}`, `{{ course.title }}`, `{{ certificate.number }}` |
| Landing | Newsletters, campaigns | `{{ post.title }}`, `{{ author.name }}`, `{{ post.url }}` |

## Integration with django-fusion

The `TemplateFieldEngine` extends the existing `TemplateRenderer`
(`django_fusion.core.rendering`) and `EmailTemplate` model
(`django_fusion.models.email`). See
[01-architecture.md](01-architecture.md) for the integration diagram.

```python
from django_fusion.template_fields import TemplateFieldEngine

engine = TemplateFieldEngine()

# Render a template with dynamic fields
html = engine.render(template_html, context={"customer": customer})

# Preview with validation issues
preview = engine.preview(template_html, sample_context)
```

The engine is implemented at
`libs/django-fusion/src/django_fusion/template_fields/` (see
[`docs/22-template-fields.md`](../../libs/django-fusion/docs/22-template-fields.md))
and covered by `tests/test_template_fields.py` in the framework suite. The
Landing Builder consumes it through `BuilderRenderer` to resolve
`{{ variable }}` placeholders in section copy against a page's
`template_context`.
