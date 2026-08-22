# Dynamic Template Field System — Data Models

> **Status:** Specification · **Version:** 1.0

## Overview

This document defines the data structures used by the template field
system: the `FieldReference` parsed token, the `ResolvedValue` wrapper,
the `ValidationIssue` report, and the `PreviewResult` container.

## Class diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│                      FieldReference                             │
│  Parsed from {{ customer.name|upper|truncate:20 }}            │
├─────────────────────────────────────────────────────────────────┤
│  raw: str               # full token text                      │
│  path: str              # "customer.name"                      │
│  segments: list[str]    # ["customer", "name"]                 │
│  filters: list[Filter]  # [upper, truncate("20")]             │
│  fallback: str | None   # "Guest" if |default:"Guest"          │
│  line: int              # source line number (for errors)     │
│  column: int            # source column (for errors)           │
├─────────────────────────────────────────────────────────────────┤
│  @classmethod from_token(token: str) -> FieldReference         │
│  @property root_object -> str          # "customer"            │
│  @property is_simple -> bool           # len(segments) == 1    │
└─────────────────────────────────────────────────────────────────┘

         │
         │ 1..*
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Filter                                     │
│  A single filter in the pipeline                                │
├─────────────────────────────────────────────────────────────────┤
│  name: str              # "currency", "date", "upper"          │
│  args: list[str]        # ["USD"], ["M d, Y"], []              │
│  raw: str               # "currency:USD"                        │
├─────────────────────────────────────────────────────────────────┤
│  @classmethod parse(filter_str: str) -> Filter                 │
│  apply(value: Any) -> str   # runs the filter logic            │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      ResolvedValue                              │
│  The result of resolving a FieldReference against context       │
├─────────────────────────────────────────────────────────────────┤
│  reference: FieldReference   # the original parsed token       │
│  raw_value: Any              # Python value before formatting  │
│  formatted: str              # after filters applied           │
│  escaped: str                # HTML-escaped for safe output    │
│  is_resolved: bool           # False if fallback was used      │
│  source: str                 # "context", "default", "empty"   │
├─────────────────────────────────────────────────────────────────┤
│  @property display_value -> str  # the final string for output  │
└─────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                      ValidationIssue                            │
│  Non-fatal problem found during validation                      │
├─────────────────────────────────────────────────────────────────┤
│  level: IssueLevel         # WARNING, ERROR                    │
│  field: str                # "order.total"                      │
│  message: str              # "Required field is empty"        │
│  line: int                 # template source line              │
│  suggestion: str           # "Provide order.total in context" │
└─────────────────────────────────────────────────────────────────┘

         │
         │ 0..*
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PreviewResult                             │
│  Result of preview-mode rendering                               │
├─────────────────────────────────────────────────────────────────┤
│  html: str                 # rendered preview HTML             │
│  issues: list[ValidationIssue]  # all issues found           │
│  resolved_count: int       # how many vars resolved           │
│  unresolved_count: int     # how many fell back / emptied     │
│  is_valid: bool            # no ERROR-level issues            │
│  watermark: str            # "PREVIEW" overlay text           │
├─────────────────────────────────────────────────────────────────┤
│  @property pass_rate -> float  # resolved / total              │
└─────────────────────────────────────────────────────────────────┘
```

## FieldReference model

The `FieldReference` is the central parsed object. One is created for
every `{{ ... }}` token in the template.

### Parsing

```text
Input token:  {{ order.customer.email|lower|default:"no-email" }}

                    FieldReference
  ┌─────────────────────────────────────────────┐
  │ raw:       '{{ order.customer.email|... }}' │
  │ path:      'order.customer.email'          │
  │ segments:  ['order', 'customer', 'email']   │
  │ filters:   [Filter('lower'),                │
  │             Filter('default', ['no-email'])]│
  │ fallback:  None (default filter handles it)│
  │ line:      12                               │
  │ column:    5                                │
  └─────────────────────────────────────────────┘
```

### Dotted-path resolution

The resolver walks the context dict using the `segments` list:

```text
FieldReference segments: ["order", "customer", "email"]
Context: {"order": {"customer": {"email": "alice@example.com"}}}

Step 1: context["order"]      → {"customer": {"email": ...}}
Step 2: ["customer"]          → {"email": "alice@example.com"}
Step 3: ["email"]             → "alice@example.com"

Result: ResolvedValue(raw_value="alice@example.com", is_resolved=True)
```

If any step fails (KeyError, AttributeError, TypeError), the resolver
checks for a fallback, then returns an empty-string ResolvedValue with
`source="empty"`.

## Filter registry

Filters are registered in a central registry. Each filter receives the
raw value and optional arguments, and returns a formatted string.

```text
┌─────────────────────────────────────────────────────────────────┐
│  FilterRegistry                                                  │
├─────────────────────────────────────────────────────────────────┤
│  _filters: dict[str, callable]                                 │
│                                                                 │
│  register(name, func)   # add a custom filter                 │
│  get(name) -> callable  # lookup                               │
│  apply(name, value, args) -> str  # run filter                 │
├─────────────────────────────────────────────────────────────────┤
│  Built-in filters:                                              │
│  ┌──────────────┬──────────────┬────────────────────────┐     │
│  │ currency      │ date         │ upper                  │     │
│  │ truncate      │ lower        │ default                │     │
│  │ title         │ strip        │ length                 │     │
│  │ join          │ split        │ yesno                  │     │
│  │ phone         │ url_encode   │ linebreaks             │     │
│  └──────────────┴──────────────┴────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Built-in filters

| Filter | Arguments | Example | Output |
|---|---|---|---|
| `currency` | `code` (optional) | `{{ order.total\|currency:"USD" }}` | `$99.50` |
| `date` | `format` | `{{ order.created\|date:"M d, Y" }}` | `Jan 15, 2024` |
| `upper` | — | `{{ customer.name\|upper }}` | `ACME CORP` |
| `lower` | — | `{{ customer.email\|lower }}` | `alice@acme.com` |
| `title` | — | `{{ product.name\|title }}` | `Premium Coffee` |
| `truncate` | `max_chars` | `{{ post.title\|truncate:30 }}` | `A very long title th…` |
| `default` | `fallback_str` | `{{ customer.company\|default:"N/A" }}` | `N/A` |
| `yesno` | `yes,no,maybe` | `{{ order.is_paid\|yesno:"Paid,Pending" }}` | `Paid` |
| `phone` | `country_code` | `{{ user.phone\|phone:"+1" }}` | `+1 (555) 123-4567` |
| `length` | — | `{{ order.items\|length }}` | `3` |
| `join` | `separator` | `{{ tags\|join:", " }}` | `coffee, tea, milk` |
| `linebreaks` | — | `{{ message\|linebreaks }}` | `<p>line1</p><p>line2</p>` |
| `url_encode` | — | `{{ query\|url_encode }}` | `hello%20world` |
| `strip` | — | `{{ name\|strip }}` | `trimmed` |

## Template schema model

Each template can declare an optional schema listing the variables it
expects. The validator uses this to check for missing required fields.

```text
┌─────────────────────────────────────────────────────────────────┐
│  TemplateSchema                                                 │
├─────────────────────────────────────────────────────────────────┤
│  fields: list[SchemaField]                                      │
├─────────────────────────────────────────────────────────────────┤
│  validate(context: dict) -> list[ValidationIssue]               │
│  get_missing(context: dict) -> list[str]                        │
└─────────────────────────────────────────────────────────────────┘

         │
         │ 1..*
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  SchemaField                                                   │
├─────────────────────────────────────────────────────────────────┤
│  path: str            # "order.total"                          │
│  label: str           # "Order Total" (display)                │
│  type: FieldType      # STRING, NUMBER, DATE, BOOLEAN, LIST   │
│  required: bool        # True if must be present               │
│  default: Any         # fallback if missing                   │
│  description: str      # help text for editors                 │
│  allowed_sources: list[str]  # ["order", "customer"]          │
└─────────────────────────────────────────────────────────────────┘
```

### FieldType enum

```text
FieldType.STRING   → any text value
FieldType.NUMBER   → int, float, Decimal
FieldType.DATE     → datetime, date, ISO string
FieldType.BOOLEAN  → bool, truthy/falsy
FieldType.LIST     → list, queryset, iterable
FieldType.OBJECT   → dict, model instance (nested access)
```

## Database model extension

The existing `EmailTemplate` model gains two fields for schema support:

```python
# Addition to EmailTemplate (models/email.py)

class EmailTemplate(models.Model):
    # ... existing fields ...

    field_schema = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            'Declared variable schema: '
            '[{"path": "order.total", "type": "number", "required": true, '
            '"label": "Order Total"}]'
        ),
    )

    is_previewable = models.BooleanField(
        default=True,
        help_text="Whether this template supports preview mode",
    )
```

### Sample schema JSON

```json
[
  {
    "path": "customer.name",
    "label": "Customer Name",
    "type": "string",
    "required": true,
    "description": "The customer's full name"
  },
  {
    "path": "customer.email",
    "label": "Customer Email",
    "type": "string",
    "required": true,
    "description": "Recipient email address"
  },
  {
    "path": "order.total",
    "label": "Order Total",
    "type": "number",
    "required": true,
    "default": "0.00",
    "description": "Total amount in the order currency"
  },
  {
    "path": "order.items",
    "label": "Order Items",
    "type": "list",
    "required": false,
    "description": "List of ordered items for line-item rendering"
  }
]
```
