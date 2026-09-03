# Dynamic Template Fields (DF-022)

> **Status:** ✅ Exists · **Source:** `src/django_fusion/template_fields/`
> **Spec:** `docs/features/template-fields/` (architecture, models, workflow,
> security, examples)

## Purpose

Render user-authored templates containing inline variable placeholders
(`{{ customer.name }}`, `{{ order.total|currency:"USD" }}`) against live
data — for emails, invoices, receipts, notifications, and landing-builder
copy. The engine is **sandboxed by design**: templates are regex-parsed, not
evaluated through Django/Jinja2, so server-side template injection is
impossible.

## Architecture

```text
template string
   │  TOKEN_RE / FILTER_SEGMENT_RE
   ▼
parse_fields() → FieldReference(path, root, filters, raw, position)
   │  resolve_path() — dotted traversal, allowlist, no method calls
   ▼
TemplateFieldEngine
   ├─ render()     → resolved, escaped string (fail-safe)
   ├─ validate()   → ValidationIssue list (ERROR/WARNING)
   └─ preview()    → PreviewResult (html + resolved/unresolved + issues)
   ▼
FilterRegistry (filters.py) — 14 built-in filters, product extension point
```

Security controls (per the spec): auto-escape, sandboxed resolution,
root allowlist, string/list length caps, URL sanitization, fail-safe output.

## Examples

```python
from django_fusion.template_fields import TemplateFieldEngine

engine = TemplateFieldEngine()

engine.render(
    "Hello {{ customer.name|default:'there' }}",
    {"customer": {"name": "Alice"}},
    allowlist=["customer"],
)
# "Hello Alice"

engine.render("{{ order.total|currency:\"USD\" }}", {"order": {"total": 99.5}})
# "$99.50"

engine.render("{{ v }}", {"v": "<script>x</script>"})
# "&lt;script&gt;x&lt;/script&gt;"   (auto-escaped)

engine.render("{{ u|safe_url }}", {"u": "javascript:alert(1)"})
# "#"   (dangerous scheme stripped)

engine.preview("{{ a }} and {{ b }}", {"a": "yes"})
# PreviewResult(html="yes and ", resolved=["a"], unresolved=["b"], issues=[...])
```

## Usage

- **Landing builder** — the `BuilderRenderer` resolves every `{{ var }}` in
  section copy against the page's `template_context` before rendering.
- **Emails** — render `EmailTemplate` content through the engine for merge
  fields (subject + HTML + text).
- **Any product** — call `TemplateFieldEngine().render(...)` directly.

## Customization

| Need | How |
|---|---|
| Custom filter | `register_filter("shout", lambda v, args: str(v).upper() + "!")` |
| Own registry | `TemplateFieldEngine(registry=my_registry)` |
| Tighter limits | `TemplateFieldEngine(max_string_length=500, max_list_items=20)` |
| Disable escaping | `engine.render(..., auto_escape=False)` (only for trusted values) |
| Restrict roots | `engine.render(..., allowlist=["customer", "order"])` |

## Best practices

- Always pass an `allowlist` when the template is user-authored.
- Treat `safe=True` filters (e.g. `linebreaks`, `safe_url`) as the only
  sources of trusted HTML; everything else is escaped.
- Surface `validate()`/`preview()` issues to editors before publish.
- Never feed raw template source into Django/Jinja2 engines.

## Remarks & Notes

- Unknown filters raise `KeyError` at render time and are `ERROR` issues in
  validation — authoring mistakes surface loudly, never silently.
- Callables are never resolved (bound methods are not data), so
  `{{ user.delete }}` renders empty rather than leaking internals.
- The engine is pure Python (no database, no Wagtail) and is covered by
  `tests/test_template_fields.py` in the framework suite.
