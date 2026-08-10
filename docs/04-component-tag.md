# {% comp %} Component Tag — Props, Slots, Vars & Attrs

Complete reference for the `{% comp %}` template tag API in django-fusion. Covers props declaration,
named/default slots, local variables, attrs passthrough, and how these compare to django-bird and
django-cotton.

---

## Comparison: django-bird vs django-cotton vs django-fusion

All three systems implement a props + slots component model for Django templates. django-fusion's
`{% comp %}` uses pure Django template syntax with no third-party dependency.

| Feature | django-bird | django-cotton | django-fusion `{% comp %}` |
|---------|-------------|---------------|---------------------------|
| **Props declaration** | `{{ props.title }}` in template | `<c-vars title />` | `{% prop title %}` / `{% prop summary="" %}` (resolved as `{{ props.title }}` **and** bare `{{ title }}` since 0.5.0 — see DF-018) |
| **Default slot** | Content between tags → `{{ slot }}` | Content between `<c-card>` tags → `{{ slot }}` | Content between `{% comp %}...{% endcomp %}` → `{% slot %}{{ slot }}{% endslot %}` |
| **Named slots** | `{% bird:slot header %}` | `<c-slot name="header" />` | `{% slot header %}...{% endslot %}` |
| **Attrs passthrough** | `{{ attrs }}` | `{{ attrs }}` | `{{ attrs }}` |
| **Self-closing** | `{% bird "name" / %}` | `<c-card />` | `{% comp "name" / %}` |
| **Fragment ID** | N/A | N/A | `fragment_name="site.fragments.app.name"` |
| **Vars (local state)** | N/A | N/A | `{% var key="value" %}` |
| **Dynamic props** | `{% bird "card" :title="var" %}` | `<c-card :title="var" />` | `{% comp "card" title=var / %}` (standard Django syntax) |

---

## Props

### Declaring Props in a Component Template

Props define the interface of a component. Declare them at the top of the template with `{% prop %}`:

```django
{# components/cards/post_card.html #}
{% load components %}
{% prop title %}                  {# required prop — no default #}
{% prop summary="" %}             {# optional prop with empty default #}
{% prop show_author=True %}       {# optional prop with boolean default #}
{% prop image=None %}             {# optional prop with None default #}
{% prop css_class="card" %}       {# optional prop with string default #}

<article class="{{ props.css_class }} {{ attrs }}">
  {% if props.image %}
    <img class="card__image" src="{{ props.image }}" alt="{{ props.title }}">
  {% endif %}
  <h3 class="card__title">{{ props.title }}</h3>
  {% if props.summary %}
    <p class="card__summary">{{ props.summary }}</p>
  {% endif %}
  {% if props.show_author %}
    {% slot author %}{% endslot %}
  {% endif %}
  <div class="card__body">
    {% slot %}{{ slot }}{% endslot %}
  </div>
</article>
```

### Passing Props When Using a Component

Props are passed as keyword arguments on `{% comp %}` — standard Django template variable syntax:

```django
{% load components %}

{# All props explicitly set #}
{% comp "components/cards/post_card.html"
    title=post.title
    summary=post.excerpt
    show_author=True
    image=post.thumbnail.url
    css_class="card--featured"
%}
  <p>{{ post.body|truncatewords:50 }}</p>
  {% slot author %}
    <span class="card__author">{{ post.author.get_full_name }}</span>
  {% endslot %}
{% endcomp %}

{# Self-closing — no slots, only props #}
{% comp "components/cards/post_card.html"
    title="Welcome"
    show_author=False / %}
```

---

## Slots

### Default Slot

Content between `{% comp %}...{% endcomp %}` becomes the default slot, rendered via `{% slot %}{{ slot }}{% endslot %}`:

```django
{# Component template #}
<div class="modal">
  <div class="modal__body">
    {% slot %}{{ slot }}{% endslot %}
  </div>
</div>

{# Usage #}
{% comp "components/modals/base.html" %}
  <h2>Hello World</h2>
  <p>This content goes into the default slot.</p>
{% endcomp %}
```

### Named Slots

Named slots let you inject content into specific regions of a component:

```django
{# Component template — components/blocks/card.html #}
{% load components %}
{% prop title %}
<article class="card">
  <header class="card__header">
    <h3>{{ props.title }}</h3>
    {% slot header %}{% endslot %}
  </header>
  <div class="card__body">
    {% slot %}{{ slot }}{% endslot %}
  </div>
  <footer class="card__footer">
    {% slot footer %}{% endslot %}
  </footer>
</article>
```

```django
{# Usage — named slots are filled via {% slot name %} blocks #}
{% comp "components/blocks/card.html" title="Pricing" %}
  {% slot header %}
    <span class="badge badge--sale">On Sale</span>
  {% endslot %}

  <p>Monthly: $9.99</p>
  <p>Yearly: $99.99</p>

  {% slot footer %}
    <button class="button button--primary">Subscribe</button>
  {% endslot %}
{% endcomp %}
```

Named slots use `name=` syntax:

```django
{% slot header %}...{% endslot %}
{# is equivalent to #}
{% slot name="header" %}...{% endslot %}
```

---

## Attrs

`{{ attrs }}` passes through any extra HTML attributes not declared as props. Useful for `class`,
`id`, `data-*`, `aria-*`, and HTMX attributes:

```django
{# Component template #}
{% load components %}
{% prop label %}
<button class="btn {{ attrs }}">
  {{ props.label }}
</button>

{# Usage — extra kwargs become attrs #}
{% comp "components/button.html"
    label="Save"
    class="btn--primary btn--lg"
    id="save-btn"
    hx-post="/save/"
    hx-target="#result" / %}
```

Renders as:

```html
<button class="btn btn--primary btn--lg" id="save-btn" hx-post="/save/" hx-target="#result">
  Save
</button>
```

Any kwarg on `{% comp %}` that does not match a declared `{% prop %}` is automatically included in `{{ attrs }}`.

---

## Vars (Local State)

`{% var %}` declares a mutable variable scoped to the component render. Useful for accumulators,
counters, and conditional state:

```django
{# Increment a counter #}
{% var counter=0 %}
{% for item in items %}
  {% var counter+=1 %}
  <li>{{ counter }}. {{ item }}</li>
{% endfor %}

{# Toggle state #}
{% var is_open=False %}
{% if condition %}
  {% var is_open="true" %}
{% endif %}
```

The `vars` dict is available in the component context:

```django
{% var total=0 %}
{% for price in items %}
  {% var total+=price|floatformat:2 %}
{% endfor %}
<p>Total: ${{ vars.total }}</p>
```

To unset a var, use `{% endvar varname %}`. Useful for cleanup at the end of a component:

```django
{% var temp_data=queryset %}
{# ... use temp_data ... #}
{% endvar temp_data %}
```

---

## Self-Closing Syntax

Use `{% comp "name" / %}` when the component has no slots to fill:

```django
{# Self-closing — renders with only props/attrs #}
{% comp "components/table.html" headers=headers rows=rows hx_target="#container" / %}
{% comp "components/icons/star.html" filled=True / %}
{% comp "components/badges/status.html" status="active" / %}
```

---

## Fragment Name

django-fusion adds `fragment_name` for HTMX fragment scoping — unique to django-fusion:

> **Note on unpoly.js**: django-material's vibe branch also uses [unpoly](https://unpoly.com/) as an alternative to HTMX for progressive enhancement. django-fusion uses HTMX for fragment-based partial updates (`FragmentComponent`, `hx-get`, `hx-target`), which provides similar progressive enhancement capabilities. The `fragment_name` kwarg is django-fusion's equivalent of unpoly's `[up-target]` scoping mechanism.

```django
{# Declare the fragment identity on a component #}
{% comp "components/fragments/post_preview.html"
    post=post
    fragment_name="blog.fragments.post_preview" / %}
```

The `fragment_name` kwarg is reserved in django-fusion and **must** use this exact spelling. Legacy
synonyms (`fragment`, `fragment_slug`, `fragment_key`) are rejected with `TemplateSyntaxError`.

In Python, FragmentComponents use it for URL routing:

```python
from django_fusion.routes.components.fragments import FragmentComponent

class PostPreviewFragment(FragmentComponent):
    route_path = "blog/<slug:slug>/preview/"
    fragment_name = "blog.fragments.post_preview"
    template_name = "blog/fragments/post_preview.html"
```

---

## Template Authoring Patterns

### Pattern 1: Simple Display Component (Self-Closing)

```django
{# components/badges/status.html #}
{% load components %}
{% prop status="default" %}
{% prop label="" %}
<span class="badge badge--{{ props.status }} {{ attrs }}"
      {% if not props.label %}aria-label="{{ props.status }}"{% endif %}>
  {{ props.label|default:props.status }}
</span>
```

```django
{% comp "components/badges/status.html" status="active" label="Active" / %}
```

### Pattern 2: Layout Component with Named Slots

```django
{# components/layouts/sidebar_layout.html #}
{% load components %}
<div class="layout layout--sidebar {{ attrs }}">
  <aside class="layout__sidebar">
    {% slot sidebar %}{% endslot %}
  </aside>
  <main class="layout__main">
    {% slot %}{{ slot }}{% endslot %}
  </main>
</div>
```

```django
{% comp "components/layouts/sidebar_layout.html" %}
  {% slot sidebar %}
    <nav>...</nav>
  {% endslot %}
  <h1>Page Content</h1>
  <p>Main content goes here.</p>
{% endcomp %}
```

### Pattern 3: Form Input with Attrs Passthrough

```django
{# components/forms/input.html #}
{% load components %}
{% prop name %}
{% prop type="text" %}
{% prop label="" %}
{% prop value="" %}
{% prop error="" %}
<div class="form-field {{ attrs }}">
  {% if props.label %}
    <label class="form-field__label" for="{{ props.name }}">{{ props.label }}</label>
  {% endif %}
  <input class="form-field__input {% if props.error %}form-field__input--error{% endif %}"
         type="{{ props.type }}"
         name="{{ props.name }}"
         id="{{ props.name }}"
         value="{{ props.value }}">
  {% if props.error %}
    <span class="form-field__error">{{ props.error }}</span>
  {% endif %}
</div>
```

```django
{% comp "components/forms/input.html"
    name="email"
    type="email"
    label="Email Address"
    value=form.email.value
    error=form.email.errors|first
    class="form-field--wide" / %}
```

### Pattern 4: Pagination with Vars

```django
{# components/pagination/numbers.html #}
{% load components %}
{% prop page_obj %}
{% var current=page_obj.number %}
<nav class="pagination {{ attrs }}" aria-label="Page navigation">
  {% for page in page_obj.paginator.page_range %}
    {% if page == vars.current %}
      <span class="pagination__item pagination__item--active">{{ page }}</span>
    {% else %}
      <a class="pagination__item" href="?page={{ page }}">{{ page }}</a>
    {% endif %}
  {% endfor %}
</nav>
```

### Pattern 5: HTMX-Enabled Component

```django
{# components/blocks/notification-banner.html #}
{% load i18n %}
{% load components %}
{% prop message %}
{% prop level="info" %}
{% prop dismissible=False %}
{% prop banner_id="notification-banner" %}
<div class="notification-banner notification-banner--{{ props.level }} {{ attrs }}"
     id="{{ props.banner_id }}">
  <span class="notification-banner__message">{{ props.message }}</span>
  {% if props.dismissible %}
    <button class="notification-banner__close"
            hx-delete="{% url 'dismiss-notification' props.banner_id %}"
            hx-target="#{{ props.banner_id }}"
            hx-swap="outerHTML"
            aria-label="Dismiss">&#x2715;</button>
  {% endif %}
</div>
```

---

## Related Documentation

| Topic | File |
|-------|------|
| Component System Overview | [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) |
| Routing System | [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) |
| Viewflow Mapping | [VIEWFLOW_MAPPING.md](./VIEWFLOW_MAPPING.md) |
| Forms & Tables | [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md) |
| Architecture Overview | [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) |
| Shared Components Inventory | `applications/assets/templates/components/AGENTS.md` |
| django-bird (reference) | https://github.com/josemachado/django-bird |
| django-cotton (reference) | https://django-cotton.com/docs/components |

---

> **0.5.0 breaking changes:** slots now render **exactly once**, props are
> exposed as **bare context variables** (`{{ name }}` in addition to
> `{{ props.name }}`), and `{% prop name default=X %}` now applies its
> default. If you're upgrading from ≤ 0.4.x, read
> [DF-018 Slot & Prop Render Contract](./18-render-contract.md) first —
> including the shadowing migration examples.

---

**Next**: See [VIEWFLOW_MAPPING.md](./VIEWFLOW_MAPPING.md) for django-material → django-fusion URL pattern mapping.
