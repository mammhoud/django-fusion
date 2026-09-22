# Dynamic Template Field System — Architecture

> **Status:** Specification · **Version:** 1.0
> **Location:** `docs/features/template-fields/`

## Overview

The Dynamic Template Field System enables user-authored templates with
inline variable placeholders (`{{ customer.name }}`, `{{ order.total }}`)
that are resolved against live data at render time. It is designed for
emails, invoices, receipts, notifications, and any product document that
mixes static layout with dynamic data.

## Design principles

1. **Declarative, not imperative** — templates declare *what* to show,
   not *how* to fetch it. The resolver handles data access.
2. **Fail safe, never crash** — unresolved variables produce fallback
   values, not exceptions. Missing data never breaks rendering.
3. **Security first** — templates are sandboxed: no arbitrary code
   execution, no raw DB access, no HTML injection.
4. **Previewable** — every template can be rendered against sample data
   before going live.
5. **Product-agnostic** — the core engine lives in `django-fusion` and
   is consumed by CRM, POS, LMS, and Landing.

## Architecture diagram

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                         Template Field System                            │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  Template    │───▶│  Variable    │───▶│  Data        │              │
│  │  Source      │    │  Parser     │    │  Resolver    │              │
│  │              │    │             │    │              │              │
│  │ DB / File /  │    │ Tokenises   │    │ Dotted-path  │              │
│  │ Inline       │    │ {{ a.b.c }} │    │ lookup with  │              │
│  └──────────────┘    └──────┬──────┘    │ fallbacks    │              │
│                             │            └──────┬───────┘              │
│                             │                   │                     │
│                             ▼                   ▼                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  Security    │◀──│  Validator   │◀──│  Formatter   │              │
│  │  Filter      │    │             │    │              │              │
│  │              │    │ Type-checks │    │ Pipes output │              │
│  │ Escapes HTML │    │ Required?   │    │ through      │              │
│  │ Strips JS    │    │ Permissions │    │ format funcs │              │
│  └──────┬───────┘    └──────────────┘    └──────────────┘              │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │  Rendered    │───▶│  Preview     │───▶│  Delivery   │              │
│  │  Output      │    │  Mode       │    │              │              │
│  │              │    │             │    │ Email / PDF  │              │
│  │ Safe HTML   │    │ Sample data  │    │ HTMX / JSON  │              │
│  └──────────────┘    └──────────────┘    └──────────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

## System layers

```text
Layer 1 — Template Source
│   Where the template body lives (DB row, file path, inline string).
│   Maps to the existing EmailTemplate.template_source field.
│
Layer 2 — Variable Parser
│   Tokenises {{ variable.path }} and {{ variable.path|filter }}
│   into structured FieldReference objects.
│
Layer 3 — Data Resolver
│   Resolves a FieldReference against a context dict using dotted-path
│   traversal (customer.name → context["customer"]["name"]).
│   Supports fallback values: {{ customer.name|default:"Guest" }}
│
Layer 4 — Validator
│   Checks that referenced fields exist in the template's declared
│   schema, that required fields have values, and that the caller
│   has permission to access the data source.
│
Layer 5 — Security Filter
│   Escapes all resolved values for the output context (HTML, text,
│   URL). Strips <script>, on* attributes, and javascript: URLs.
│   No raw HTML passthrough unless explicitly whitelisted.
│
Layer 6 — Formatter
│   Applies format filters (currency, date, uppercase, truncate).
│   Filter pipeline: {{ order.total|currency:"USD" }}
│
Layer 7 — Renderer
│   Combines the template skeleton with resolved, escaped, and
│   formatted values to produce the final output string.
│
Layer 8 — Preview Mode
│   Renders against sample/mock data so editors can see the result
│   before publishing. Produces a watermarked preview.
│
Layer 9 — Delivery
│   Sends the rendered output to its destination (email, PDF
│   attachment, HTMX fragment, JSON payload).
```

## Request lifecycle

```text
1. Caller requests render
   │   renderer.render("invoice_template", context={"order": order_obj})
   │
   ▼
2. Template Source loads
   │   EmailTemplate.objects.get(name="invoice_template")
   │   → reads html_content / template_path
   │
   ▼
3. Variable Parser tokenises
   │   Scans template for {{ ... }} tokens
   │   Produces list[FieldReference(name="order.total", filters=["currency:USD"])]
   │
   ▼
4. Data Resolver resolves each FieldReference
   │   For {{ order.total }}:
   │     context["order"] → Order instance
   │     getattr(order, "total") → Decimal("99.50")
   │   For unresolved: use fallback or "" (empty string)
   │
   ▼
5. Validator checks
   │   Required fields present? → yes/no
   │   Type matches declared schema? → yes/no
   │   Permission to access source? → yes/no
   │   → Collects ValidationIssue list (warnings, not fatal)
   │
   ▼
6. Security Filter escapes
   │   value = "Acme <Corp>" → "Acme &lt;Corp&gt;"
   │   No <script> tags survive.
   │
   ▼
7. Formatter applies filters
   │   Decimal("99.50") | currency:"USD" → "$99.50"
   │   "2024-01-15" | date:"M d, Y" → "Jan 15, 2024"
   │
   ▼
8. Renderer assembles
   │   Replaces {{ ... }} tokens with resolved values
   │   Produces final HTML string
   │
   ▼
9. Output delivered
   │   Email → send via TemplateRenderer.render_email()
   │   Preview → return with watermark + validation issues
   │   PDF → pass to weasyprint/wkhtmltopdf
   │   HTMX → return HttpResponse fragment
```

## Integration with existing systems

```text
┌─────────────────────────────────────────────────────────────────┐
│  Existing django-fusion infrastructure                          │
│                                                                 │
│  ┌─────────────────┐        ┌──────────────────────┐           │
│  │ TemplateRenderer│        │ EmailTemplate (model) │           │
│  │ (rendering.py)  │        │ (models/email.py)     │           │
│  └────────┬────────┘        └──────────┬───────────┘           │
│           │                            │                        │
│           │  render(template, ctx)     │  html_content          │
│           │                            │  subject_template      │
│           ▼                            ▼                        │
│  ┌──────────────────────────────────────────────────┐          │
│  │  NEW: TemplateFieldEngine                         │          │
│  │                                                  │          │
│  │  parse()  → list[FieldReference]                 │          │
│  │  resolve() → dict[str, ResolvedValue]            │          │
│  │  validate() → list[ValidationIssue]              │          │
│  │  render() → str (safe HTML)                      │          │
│  │  preview() → PreviewResult(html, issues)         │          │
│  └──────────────────────────────────────────────────┘          │
│           │                                                     │
│           ▼                                                     │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Products consume via:                           │          │
│  │                                                  │          │
│  │  • POS: invoice.html, receipt templates          │          │
│  │  • CRM: email templates, contact merge fields    │          │
│  │  • LMS: certificate templates, enrollment emails  │          │
│  │  • Landing: newsletter, campaign emails           │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Token syntax reference

| Syntax | Description | Example |
|---|---|---|
| `{{ object.field }}` | Simple field access | `{{ customer.name }}` |
| `{{ object.nested.field }}` | Nested field access | `{{ order.customer.email }}` |
| `{{ object.field\|filter }}` | Apply a format filter | `{{ order.total\|currency }}` |
| `{{ object.field\|filter:"arg" }}` | Filter with argument | `{{ order.created_at\|date:"M d, Y" }}` |
| `{{ object.field\|default:"fallback" }}` | Fallback if unresolved | `{{ customer.company\|default:"Individual" }}` |
| `{{ object.field\|filter1\|filter2 }}` | Chained filters | `{{ user.name\|upper\|truncate:20 }}` |

> **Note:** The pipe `|` and curly braces are shown escaped as `\|` and
> within code fences in this document to avoid Markdown rendering issues.
> In actual templates, use plain `{{ order.total|currency }}`.
