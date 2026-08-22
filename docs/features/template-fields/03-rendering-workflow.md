# Dynamic Template Field System — Rendering Workflow

> **Status:** Specification · **Version:** 1.0

## Overview

This document traces the full rendering pipeline from raw template text
to final output, showing each stage, its inputs, outputs, and error
handling.

## Pipeline overview

```text
Template text ──────▶ Parse ──────▶ Resolve ──────▶ Validate
     "Hello {{ customer.name }}!"        │              │
                                         │              │
                                         ▼              ▼
                                    ResolvedValues  ValidationIssues
                                         │              │
                                         ▼              │
                                    Escape ─────▶ Format ─────▶ Assemble
                                         │              │            │
                                         ▼              ▼            ▼
                                    EscapedVals  FormattedVals  FinalHTML
                                                                    │
                                                                    ▼
                                                              Deliver / Preview
```

## Stage 1 — Parse

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: PARSE                                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  template_text: str                                     │
│    "Invoice {{ invoice.number }}                                │
│     Total: {{ order.total|currency:'USD' }}                    │
│     Customer: {{ customer.name|default:'Guest' }}"              │
│                                                                 │
│  Process:                                                       │
│    1. Regex scan for {{ ... }} tokens                           │
│       Pattern: r'\{\{\s*([^}]+?)\s*\}\}'                       │
│                                                                 │
│    2. For each match, parse the inner expression:               │
│       a. Split on | → ["invoice.number", "currency:'USD'"]     │
│       b. First part = path → segments = path.split(".")        │
│       c. Remaining parts = filters                              │
│       d. Parse each filter: name + args (split on ":")         │
│                                                                 │
│    3. Build FieldReference objects                              │
│                                                                 │
│  Output: ParseResult                                            │
│    .template_segments: list[str | FieldReference]              │
│      → ["Invoice ", FR(invoice.number),                        │
│         "\nTotal: ", FR(order.total, [currency:USD]),          │
│         "\nCustomer: ", FR(customer.name, [default:Guest])]   │
│    .references: list[FieldReference]                           │
│    .errors: list[ParseError]  (malformed tokens)               │
│                                                                 │
│  Error handling:                                                │
│    Malformed token (e.g. {{ order.total|) → ParseError         │
│    → token is replaced with empty string at render              │
│    → error is logged for editor review                           │
└─────────────────────────────────────────────────────────────────┘
```

### Regex tokenisation

```text
Token pattern:  \{\{\s*([^}]+?)\s*\}\}

Match groups:
  Group 1 = inner expression (e.g. "order.total|currency:USD")

Inner expression parsing:
  Split on "|" (not inside quotes)
  → ["order.total", "currency:USD"]

Path parsing:
  "order.total" → segments = ["order", "total"]

Filter parsing:
  "currency:USD" → name="currency", args=["USD"]
  "default:'Guest'" → name="default", args=["Guest"]
  "upper" → name="upper", args=[]
  "date:M d, Y" → name="date", args=["M d, Y"]
```

## Stage 2 — Resolve

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: RESOLVE                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  list[FieldReference], context: dict                    │
│    context = {                                                  │
│      "invoice": {"number": "INV-2024-0042"},                   │
│      "order": {"total": Decimal("99.50")},                     │
│      "customer": {}  ← name is missing                         │
│    }                                                            │
│                                                                 │
│  Process: For each FieldReference:                              │
│    1. Walk segments through context dict                        │
│       FR("invoice.number"):                                     │
│         context["invoice"] → {"number": "INV-..."}             │
│         ["number"] → "INV-2024-0042"                            │
│         → ResolvedValue(raw="INV-2024-0042", resolved=True)     │
│                                                                 │
│    2. If path traversal fails (KeyError/AttributeError):       │
│       a. Check for fallback filter → use fallback value        │
│       b. No fallback → ResolvedValue(raw="", resolved=False,   │
│          source="empty")                                        │
│                                                                 │
│       FR("customer.name", fallback="Guest"):                   │
│         context["customer"] → {}                                │
│         ["name"] → KeyError                                     │
│         fallback="Guest" → ResolvedValue(raw="Guest",           │
│           resolved=False, source="default")                    │
│                                                                 │
│  Output: dict[str, ResolvedValue]                               │
│    {                                                            │
│      "invoice.number": RV("INV-2024-0042", True),               │
│      "order.total": RV(Decimal("99.50"), True),                │
│      "customer.name": RV("Guest", False, source="default"),     │
│    }                                                            │
│                                                                 │
│  Resolution sources (priority order):                           │
│    1. context    → resolved from provided data                  │
│    2. default    → from |default:"..." filter                   │
│    3. empty     → "" (empty string, never None)                 │
└─────────────────────────────────────────────────────────────────┘
```

### Dotted-path resolution flowchart

```text
          ┌───────────────────┐
          │ FieldReference    │
          │ segments=[a,b,c]  │
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ current = context │
          │ segment = "a"     │
          └─────────┬─────────┘
                    │
                    ▼
          ┌───────────────────┐
          │ Is current a dict?│──No──▶ Is current an object?──No──▶ FAIL
          │ or has __getitem__?│      │ has attr "a"?            │
          └─────────┬─────────┘      └───────────┬───────────────┘
                    │ Yes                          │ Yes
                    ▼                              ▼
          ┌───────────────────┐         ┌───────────────────┐
          │ current =         │         │ current =         │
          │ current["a"]      │         │ getattr(current,  │
          │                   │         │   "a")            │
          └─────────┬─────────┘         └─────────┬─────────┘
                    │                              │
                    └──────────┬───────────────────┘
                               │
                               ▼
                    ┌───────────────────┐
                    │ More segments?    │──Yes──▶ loop back
                    └─────────┬─────────┘
                              │ No
                              ▼
                    ┌───────────────────┐
                    │ RESOLVED           │
                    │ raw_value = current│
                    └───────────────────┘
```

## Stage 3 — Validate

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3: VALIDATE                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  resolved_values, template_schema, context              │
│                                                                 │
│  Checks:                                                        │
│    1. Required field present?                                   │
│       Schema: customer.name (required=True)                     │
│       Resolved: source="default" (used fallback)                 │
│       → WARNING: "Required field customer.name used fallback"  │
│                                                                 │
│    2. Type matches?                                             │
│       Schema: order.total (type=NUMBER)                        │
│       Resolved: Decimal("99.50") → isinstance(Decimal) ✓       │
│       → No issue                                                 │
│                                                                 │
│       Schema: invoice.number (type=STRING)                     │
│       Resolved: 42 (int) → not str                              │
│       → WARNING: "Type mismatch: expected STRING, got NUMBER"   │
│                                                                 │
│    3. Unknown variables (not in schema)?                        │
│       Template has {{ invoice.date }} but schema has no         │
│       "invoice.date" field                                      │
│       → INFO: "Undeclared variable invoice.date"                │
│                                                                 │
│  Output: list[ValidationIssue]                                  │
│    [Warning("customer.name", "Required field used fallback"),   │
│     Info("invoice.date", "Undeclared variable")]                │
│                                                                 │
│  NOTE: Validation issues are NEVER fatal. The template renders  │
│  regardless. Issues are surfaced to the editor in preview mode. │
└─────────────────────────────────────────────────────────────────┘
```

## Stage 4 — Escape (Security Filter)

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4: ESCAPE (Security Filter)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  resolved_values: dict[str, ResolvedValue]              │
│                                                                 │
│  Process: For each ResolvedValue:                               │
│    1. Convert raw_value to string                               │
│       Decimal("99.50") → "99.50"                                │
│       "Acme <Corp>" → "Acme <Corp>"                             │
│                                                                 │
│    2. HTML-escape the string:                                   │
│       & → &amp;                                                 │
│       < → &lt;                                                  │
│       > → &gt;                                                  │
│       " → &quot;                                                │
│       ' → &#x27;                                                │
│                                                                 │
│    3. Strip dangerous patterns (defense in depth):             │
│       Remove: <script>...</script>                             │
│       Remove: on* attributes (onclick, onload, …)              │
│       Remove: javascript: URLs                                  │
│       Remove: data: URLs (except images)                        │
│                                                                 │
│    4. Store as ResolvedValue.escaped                            │
│                                                                 │
│  Output: resolved_values with .escaped populated                │
│    "Acme <Corp>" → escaped = "Acme &lt;Corp&gt;"                │
│    "99.50" → escaped = "99.50" (no special chars)               │
│                                                                 │
│  Security guarantees:                                           │
│    • No user-supplied data reaches output unescaped             │
│    • No <script> tags survive                                   │
│    • No event handler attributes survive                        │
│    • No javascript: URLs survive                                 │
│    • |linebreaks filter is the ONLY way to insert HTML          │
│      (it wraps text in <p> tags, not raw passthrough)          │
└─────────────────────────────────────────────────────────────────┘
```

## Stage 5 — Format (Filter Pipeline)

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5: FORMAT                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  resolved_values (escaped), FieldReference.filters      │
│                                                                 │
│  Process: For each ResolvedValue, apply filters left-to-right:  │
│                                                                 │
│    FR("order.total", filters=[currency:USD])                    │
│      escaped = "99.50"                                           │
│      → FilterRegistry.apply("currency", "99.50", ["USD"])       │
│      → formatted = "$99.50"                                     │
│                                                                 │
│    FR("user.name", filters=[upper, truncate:20])               │
│      escaped = "Alexander Hamilton"                             │
│      → apply("upper", "Alexander Hamilton", [])                 │
│      → "ALEXANDER HAMILTON"                                      │
│      → apply("truncate", "ALEXANDER HAMILTON", ["20"])          │
│      → "ALEXANDER HAMILTO…"                                     │
│      → formatted = "ALEXANDER HAMILTO…"                        │
│                                                                 │
│    FR("customer.name", filters=[], fallback="Guest")            │
│      escaped = "Guest"                                           │
│      → no filters                                               │
│      → formatted = "Guest"                                      │
│                                                                 │
│  Output: resolved_values with .formatted populated               │
│                                                                 │
│  Filter pipeline order:                                          │
│    raw → escape → filter1 → filter2 → … → formatted             │
│                                                                 │
│  NOTE: Filters receive the ESCAPED value, so they cannot       │
│  introduce unescaped HTML. The |linebreaks filter is special:   │
│  it operates on the raw (pre-escape) value and produces safe    │
│  <p> tags, then the result is re-escaped except for those tags. │
└─────────────────────────────────────────────────────────────────┘
```

## Stage 6 — Assemble (Render)

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 6: ASSEMBLE                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  template_segments, resolved_values                    │
│                                                                 │
│  Process: Walk template_segments, replace tokens:               │
│    segment = "Invoice "        → output += "Invoice "          │
│    segment = FR(invoice.number)→ output += resolved[           │
│                                    "invoice.number"].display    │
│    segment = "\nTotal: "      → output += "\nTotal: "          │
│    segment = FR(order.total)  → output += "$99.50"             │
│    segment = "\nCustomer: "   → output += "\nCustomer: "       │
│    segment = FR(customer.name)→ output += "Guest"              │
│                                                                 │
│  Output: final_html: str                                         │
│    "Invoice INV-2024-0042\nTotal: $99.50\nCustomer: Guest"      │
│                                                                 │
│  The display_value property returns:                             │
│    .formatted if filters were applied                            │
│    .escaped   if no filters                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Stage 7 — Preview Mode

```text
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 7: PREVIEW MODE (optional)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input:  template, sample_context (mock data)                   │
│                                                                 │
│  Process:                                                        │
│    1. Run stages 1–6 with sample_context                        │
│    2. Collect all ValidationIssues                              │
│    3. Wrap output in preview chrome:                            │
│       <div class="fu-template-preview">                         │
│         <div class="fu-template-preview__watermark">PREVIEW     │
│         </div>                                                  │
│         <div class="fu-template-preview__issues">               │
│           <!-- validation issues listed here -->                │
│         </div>                                                  │
│         <div class="fu-template-preview__content">              │
│           <!-- rendered HTML -->                                │
│         </div>                                                  │
│       </div>                                                    │
│    4. Return PreviewResult                                       │
│                                                                 │
│  PreviewResult:                                                  │
│    html: "<div class='fu-template-preview'>...</div>"           │
│    issues: [Warning("customer.name", "Used fallback")]          │
│    resolved_count: 2                                             │
│    unresolved_count: 1                                           │
│    is_valid: True  (no ERROR-level issues)                      │
│    pass_rate: 0.67  (2/3 resolved from context)                 │
│                                                                 │
│  Watermark ensures preview output is never confused with        │
│  production output.                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Complete pipeline diagram

```text
Template Text                Context Data           Template Schema
      │                            │                       │
      ▼                            │                       │
┌───────────┐                     │                       │
│  Parse    │                     │                       │
└─────┬─────┘                     │                       │
      │                           │                       │
      ▼                           │                       │
list[FieldRef]                    │                       │
      │                           │                       │
      ▼                           ▼                       │
┌──────────────────────────────────────┐                   │
│           Resolve                     │                   │
│  (walk context via dotted paths)     │                   │
└──────────────────┬───────────────────┘                   │
                   │                                        │
                   ▼                                        │
dict[str, ResolvedValue]                                    │
      │                                        │            │
      │                                        ▼            │
      │                              ┌──────────────┐      │
      │                              │  Validate    │      │
      │                              │  (check      │      │
      │                              │   schema)   │      │
      │                              └──────┬───────┘      │
      │                                     │              │
      ▼                                     ▼              │
┌───────────┐                      list[ValidationIssue]   │
│  Escape   │                                               │
│ (security)│                                               │
└─────┬─────┘                                               │
      │                                                     │
      ▼                                                     │
┌───────────┐                                               │
│  Format   │  ← FilterRegistry                              │
│ (filters) │                                               │
└─────┬─────┘                                               │
      │                                                     │
      ▼                                                     │
┌───────────┐                                               │
│ Assemble  │                                               │
│ (replace  │                                               │
│  tokens)  │                                               │
└─────┬─────┘                                               │
      │                                                     │
      ▼                              │                     │
Final HTML ─────────┬────────────────┘                     │
                    │                     │                 │
                    ▼                     ▼                 │
           ┌──────────────┐     ┌──────────────┐            │
           │  Deliver     │     │  Preview     │            │
           │ (email/PDF)  │     │ (watermark + │◄───────────┘
           └──────────────┘     │  issues)    │
                                └──────────────┘
```

## Error handling summary

| Stage | Error | Handling | Effect |
|---|---|---|---|
| Parse | Malformed token `{{ order.total\|` | ParseError logged, token → "" | One field blank, template renders |
| Resolve | Path not found `{{ customer.company }}` | Check fallback, else "" | Field shows fallback or blank |
| Resolve | AttributeError on None | Same as path-not-found | Field shows fallback or blank |
| Validate | Required field missing | Warning issue | Editor notified in preview |
| Validate | Type mismatch | Warning issue | Editor notified, renders anyway |
| Escape | Dangerous content `<script>` | Stripped | Content sanitized |
| Format | Unknown filter `|nonexistent` | Token → "" + ParseError | Field blank, logged |
| Format | Filter raises exception | Caught, raw value used | Field shows unformatted value |
