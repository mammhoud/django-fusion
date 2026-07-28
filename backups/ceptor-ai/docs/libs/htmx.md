# HTMX Integration Patterns

[HTMX](https://htmx.org/) enables dynamic page updates without full JavaScript frameworks.

## Fragment Pattern

Auth pages use the fragment pattern — templates render only a `<section class="fragment--form">` block. HTMX swaps this in-place; full-page loads wrap it in the skeleton.

```html
<!-- Fragment template (auth/login.html) -->
<section class="fragment--form">
  <form hx-post="{% url 'plugins:login' %}"
        hx-target=".auth__form"
        hx-swap="innerHTML">
    ...
  </form>
</section>
```

## HTMX Detection

The server detects HTMX requests via the `HX-Request` header:

```python
# In AuthHTMXAdapter
is_htmx = request.headers.get("HX-Request", False)
```

## Strategy Hidden Input

All auth forms include a `strategy` field so the server knows the request context:

```html
<input type="hidden" name="strategy"
       value="{% if request.htmx %}htmx{% else %}document{% endif %}">
```

## Social Login Exception

OAuth redirects **cannot** use `hx-post` — the browser must follow the redirect natively. Social buttons always use `<a href>`:

```html
<!-- CORRECT -->
<a href="{% provider_login_url 'google' %}" class="btn btn--social bg-google">
  Continue with Google
</a>

<!-- WRONG — OAuth cannot be intercepted by HTMX -->
<button hx-post="..." class="btn btn--social bg-google">...</button>
```

## HTMX Headers Reference

| Header | Purpose |
|--------|---------|
| `HX-Request: true` | Marks request as HTMX |
| `HX-Current-URL` | Current browser URL |
| `HX-Target` | ID of target element |
| `HX-Trigger` | ID of triggering element |

## SSE Integration

The `supports_sse` hidden input tells the server whether the client supports Server-Sent Events:

```html
<input type="hidden" name="supports_sse"
       value="{{ request.supports_sse|yesno:'true,false' }}">
```
