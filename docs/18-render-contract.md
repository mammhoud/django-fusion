# Slot & Prop Render Contract — DF-018

> Introduced in **django-fusion 0.5.0** (2026-08-10).
> This is a companion to [DF-004 `{% comp %}` template tag](./04-component-tag.md)
> and documents the **breaking** render-contract changes shipped in 0.5.0:
> single-render slots, bare-context-var prop exposure, and kwarg-style prop
> defaults — plus migration examples for affected templates.
>
> Source of truth: `src/django_fusion/comp/_init.py`
> (`BoundComponent.fill_slots` / `BoundComponent.render`),
> `src/django_fusion/comp/templatetags/tags/slot.py`,
> `src/django_fusion/comp/templatetags/tags/prop.py`,
> `tests/test_slot_prop_fixes.py`.

## TL;DR (what changed in 0.5.0)

| Contract | Before 0.5.0 | After 0.5.0 |
|----------|--------------|-------------|
| **Slot rendering** | Caller's slot content was eagerly rendered to a string, then **re-parsed as a fresh template** → every `{{ }}` / `{% %}` in the slot body ran **twice**. | Slot content is stored as a raw `NodeList` and rendered **exactly once**. |
| **Empty slot** | Caller's empty slot blocked the component's fallback body. | Empty caller slot → `None` → component's own fallback body renders. |
| **Prop access** | Props only via `{{ props.name }}`. | Props available **both** as `{{ props.name }}` **and** as bare `{{ name }}`. |
| **Unpassed declared prop** | Fell through to the outer (parent) context. | Resolves to `None` and **shadows** the outer context. |
| **`{% prop name default=X %}`** | `default=` was parsed but silently dropped → prop always `None`. | Default is now applied. |

These are deliberate, breaking changes. Existing components that relied on
either double-rendered slots or implicit outer-context leakage **must** be
migrated. The migration recipes below cover every affected pattern.

---

## 1. Slots render exactly once

### What was wrong

`BoundComponent.fill_slots` eagerly rendered the caller's nodelist to a
string, and `SlotNode.render` then fed that string back into Django's
`template.Template(...)` — a brand-new compile. Any template variable or tag
in the slot body was evaluated twice, which:

- doubled the work for expensive template tags (`{% image %}`, queries, …);
- caused **visible duplicates** (e.g. HTMX fragments rendering their own
  copy of a component), the "component renders more than once" symptom;
- made slot content order-dependent on the outer context at *fill* time
  rather than *render* time.

### The new contract

```python
# src/django_fusion/comp/_init.py — BoundComponent.fill_slots (abridged)
slot_nodes = {
    node.name: node.nodelist if node.nodelist else None   # raw, unrendered
    for node in self.nodelist
    if isinstance(node, SlotNode)
}
```

`SlotNode.render` renders the stored `NodeList` **once** with the current
context; a legacy pre-rendered string is emitted verbatim; `None` renders
the node's own fallback body:

```python
# src/django_fusion/comp/templatetags/tags/slot.py — SlotNode.render (abridged)
if isinstance(slot_content, (Node, NodeList)):
    return slot_content.render(context)   # exactly once
if slot_content is None:
    return self.nodelist.render(context)  # component fallback body
return cast(str, slot_content)            # legacy string: verbatim
```

### Migration

**Before** (component template with a fallback body):

```django
{# components/panels/header.html #}
{% load components %}
{% prop title %}
<h2>{{ props.title }}</h2>
{% slot subtitle %}
  <p class="muted">Default subtitle</p>
{% endslot %}
```

**After** — the template itself is **unchanged**; only the *caller* behavior
changes. Verify the caller:

```django
{# Correct: caller content is rendered once, verbatim #}
{% comp "components/panels/header.html" title=page.title %}
  <p class="muted">{{ page.subtitle|lower }}</p>   {# {{ }} runs ONCE now #}
{% endcomp %}
```

If you were **relying on double-rendering** (i.e. you put raw template
syntax in the slot body expecting it to be compiled by the slot), stop:
pass already-rendered markup instead.

```django
{# ❌ Was: caller passes template syntax as data #}
{% comp "components/panels/header.html" title=page.title %}
  {% slot subtitle %}{{ some_markup_string }}{% endslot %}   {# markup string was re-compiled #}
{% endcomp %}

{# ✅ Now: render first, then pass the result #}
{% comp "components/panels/header.html" title=page.title %}
  {% slot subtitle %}{% include "partials/subtitle.html" %}{% endslot %}
{% endcomp %}
```

---

## 2. Props are exposed as bare context variables

### What changed

`BoundComponent.render` now pushes resolved props **twice** into the
component context: as the documented `props` mapping **and** as bare
context variables:

```python
# src/django_fusion/comp/_init.py — BoundComponent.render (abridged)
with context.push(**{
    **props,          # bare vars: {{ title }}, {{ summary }}, ...
    "props": props,   # documented mapping: {{ props.title }}, ...
    "slots": slots,
    "attrs": attrs,
}):
    ...
```

Both of these now work inside a component template:

```django
{# components/cards/post_card.html #}
{% load components %}
{% prop title %}
{% prop image_height default=250 %}

<article>
  <h3>{{ title }}</h3>                 {# bare var — NEW in 0.5.0 #}
  <h3>{{ props.title }}</h3>           {# mapping — unchanged #}
</article>
```

### Breaking edge case: shadowing

A **declared-but-unpassed** prop now resolves to `None` and **shadows** any
outer-context variable of the same name. Before 0.5.0 the bare name fell
through to the parent context.

```django
{# components/sections/listing.html — declares block but caller passes nothing #}
{% load components %}
{% prop block %}
{% if block %}
  <div class="listing">{{ block.title }}</div>
{% else %}
  <div class="listing">No block</div>
{% endif %}
```

```django
{# Calling page template — page context has `block` #}
{# ❌ 0.4.x: `block` leaked in from the page context and rendered. #}
{# ✅ 0.5.0: `block` is None (prop declared, not passed) → renders fallback. #}
{% comp "components/sections/listing.html" / %}

{# ✅ Correct: pass the value explicitly #}
{% comp "components/sections/listing.html" block=block / %}
```

### Migration checklist for shadowing

1. Find every component whose `{% prop %}` names a variable that also
   exists in the calling page's context (`block`, `page`, `course`,
   `post`, `request`, …).
2. Update every `{% comp %}` call site to pass that value explicitly:
   `{% comp "…" block=block / %}`.
3. If the component never receives the value, either remove the `{% prop %}`
   declaration or keep it and treat `None` as the fallback path (the
   component must guard with `{% if prop %}`).

The LMS call-sites that were migrated in the same change set follow this
exact pattern:

```django
{# projects/precis — learning/course.html #}
{% comp "courses/details/header.html" course=course / %}
{% comp "courses/details/overview.html" course=course / %}
{% comp "courses/details/curriculum.html" course=course / %}

{# learning/index.html #}
{% comp 'learning/video_player.html' lesson=lesson / %}
{% comp 'learning/lesson_resources.html' lesson=lesson / %}
{% comp 'learning/course_sidebar.html' lesson=lesson course_modules=course_modules / %}
```

---

## 3. Kwarg-style prop defaults now work

### What changed

Both documented forms of `{% prop %}` are now equivalent:

```django
{% prop icon_style="inside" %}      {# classic form — unchanged #}
{% prop icon_style default="inside" %}   {# kwarg form — default previously DROPPED #}
```

Before 0.5.0, the kwarg form parsed `default=` but never stored it, so
`{% prop show_icons default=True %}` always resolved `show_icons` to `None`
regardless of the default. `do_prop` now applies the `default=` bit:

```python
# src/django_fusion/comp/templatetags/tags/prop.py — do_prop (abridged)
for bit in bits:
    if bit.startswith("default="):
        default = bit.split("=", 1)[1]
        break
return PropNode(name, default, [])
```

### Migration

If your component declared kwarg-style defaults that you worked around
manually, you can now delete the workaround:

```django
{# components/widgets/flags.html #}
{% load components %}
{% prop show_icons default=True %}
{% prop show_labels default=True %}
{% prop icon_style default='inside' %}

{# ✅ Now: defaults actually apply — no manual |default fallback needed #}
icons={{ show_icons }}|labels={{ show_labels }}|style={{ icon_style }}
```

```django
{# ❌ Before 0.5.0: the component's own defaults silently never applied #}
{% prop show_icons default=True %}
{# show_icons was ALWAYS None unless the caller passed it — even though a
   default was declared. The component rendered without its default state. #}

{# Caller omitting the prop got NO default (empty/False), not True #}
{% comp "components/widgets/flags.html" / %}
```

---

## 4. Component fallback bodies

An **empty** caller slot (no content between `{% slot name %}...{% endslot %}`,
or no default slot content at all) now means "render the component's own
fallback body":

```django
{# components/panels/notice.html #}
{% load components %}
<div class="notice">
  {% slot body %}
    <p class="muted">Default notice text</p>   {# fallback — renders when caller sends nothing #}
  {% endslot %}
</div>
```

```django
{# Usage A — caller fills the slot: fallback skipped #}
{% comp "components/panels/notice.html" %}
  {% slot body %}<p class="alert">Custom text</p>{% endslot %}
{% endcomp %}

{# Usage B — caller sends nothing: fallback body renders #}
{% comp "components/panels/notice.html" %}{% endcomp %}
```

The same applies to the default slot (`{% slot %}` / `{{ slot }}`): if the
caller provides no default-slot content, the component's own body inside
`{% slot %}` renders once.

---

## 5. Nested components and `{{ slot }}`

When component A renders component B and passes its own default slot
content along, the inner `{{ slot }}` accessor is rendered **once** with
B's context — never re-parsed:

```django
{# components/cards/outer.html — passes its default slot to inner #}
{% load components %}
{% comp "components/cards/inner.html" %}
  {{ slot }}          {# resolved once; caller syntax is NOT re-compiled #}
{% endcomp %}
```

A stored `SlotNode` is never rendered by `fill_slots` (that would re-enter
`SlotNode.render` → `context["slots"]` → infinite recursion). Raw nodelists
are stored instead, so nested composition is safe.

---

## Validation

The contract is pinned by `tests/test_slot_prop_fixes.py` in the library
test suite. Cover:

- slot content with `{{ var }}` and nested `{% %}` renders exactly once
  (no duplication);
- empty caller slots fall back to component bodies;
- props resolve via bare `{{ name }}` and `{{ props.name }}` identically;
- declared-but-unpassed props are `None` (shadowing), not leaked outer vars;
- `{% prop name default=X %}` applies its default.

Run:

```bash
cd libs/django-fusion
uv run pytest tests/test_slot_prop_fixes.py -q
```

---

## Cross-references

- [DF-004 `{% comp %}` template tag](./04-component-tag.md) — the full
  props/slots/vars/attrs API; DF-018 only covers the 0.5.0 render contract.
- [DF-013 Troubleshooting](./13-troubleshooting.md) — symptom → cause → fix.
- `CHANGELOG.md` `[0.5.0] — 2026-08-10` — the breaking-change entries.
