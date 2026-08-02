# django-fusion Component Case Studies

Real-world usage patterns for every shared component shipped in
`django_fusion/comp/templates/components/`. Each case study pairs the
`{% comp %}` template syntax with its Python equivalent so you can drive
the same component from views, services, and async jobs without writing
parallel render logic.

---

## Table of Contents

1. [Anatomy of a Case Study](#anatomy-of-a-case-study)
2. [Python Entry Points (Read This First)](#python-entry-points-read-this-first)
3. [Forms & Inputs](#forms--inputs)
   - [Case Study: `form/form.html` — Unified Django Form](#case-study-formformhtml--unified-django-form)
   - [Case Study: `button.html` — Brand-Gradient CTA](#case-study-buttonhtml--brand-gradient-cta)
   - [Case Study: `submit_button.html` — HTMX Submit with Spinner](#case-study-submit_buttonhtml--htmx-submit-with-spinner)
   - [Case Study: `form_field.html` — Wagtail-Block-Aware Field Renderer](#case-study-form_fieldhtml--wagtail-block-aware-field-renderer)
4. [Modals](#modals)
   - [Case Study: `modal.html` — Trigger + Skeleton Combo](#case-study-modalhtml--trigger--skeleton-combo)
   - [Case Study: `modal_trigger.html` — Reusable Trigger Button](#case-study-modal_triggerhtml--reusable-trigger-button)
   - [Case Study: `modal_static.html` — Block-Extendable Skeleton](#case-study-modal_statichtml--block-extendable-skeleton)
5. [Notifications](#notifications)
   - [Case Study: `notification.html` — Drop-In Notification Center](#case-study-notificationhtml--drop-in-notification-center)
   - [Case Study: `notification_small.html` — Inline Status Pill](#case-study-notification_smallhtml--inline-status-pill)
6. [Pagination](#pagination)
   - [Case Study: `pagination.html` — HTMX + Unpoly Pagination](#case-study-paginationhtml--htmx--unpoly-pagination)
   - [Case Study: `pagination/load_more.html` — "Load More" Button](#case-study-paginationload_morehtml--load-more-button)
   - [Case Study: `pagination/infinite.html` — Intersection-Observer Scroll](#case-study-paginationinfinitehtml--intersection-observer-scroll)
7. [Tables & Search](#tables--search)
   - [Case Study: `table.html` — django-tables2 + Explicit Modes](#case-study-tablehtml--django-tables2--explicit-modes)
   - [Case Study: `search.html` — HTMX Search w/ Filter Preservation](#case-study-searchhtml--htmx-search-w-filter-preservation)
   - [Case Study: `breadcrumbs.html` — Schema.org + Unpoly](#case-study-breadcrumbshtml--schemaorg--unpoly)
8. [Chat & Cookies](#chat--cookies)
   - [Case Study: `chat/bubble.html` — Floating AI Chat Widget](#case-study-chatbubblehtml--floating-ai-chat-widget)
   - [Case Study: `cookies/cookie-consent.html` — Cookie Preferences UI](#case-study-cookiescookie-consenthtml--cookie-preferences-ui)
9. [Navigation](#navigation)
   - [Case Study: `navigation/nav_link.html` — Single Nav Link](#case-study-navigationnav_linkhtml--single-nav-link)
   - [Case Study: `menu/app_menu.html` + `menu/site_menu.html`](#case-study-menuapp_menuhtml--menusite_menuhtml)
10. [Cross-Cutting Recipes](#cross-cutting-recipes)
11. [Recipe Index](#recipe-index)

---

## Anatomy of a Case Study

Every component case study below follows the same six-section structure so
you can compare components at a glance:

| Section | What it answers |
|---------|-----------------|
| **Description** | A one-sentence summary of what the component renders. |
| **Use Case** | When to reach for it (and when not to). |
| **Template Syntax** | How to invoke it from a Django template with `{% comp %}`. |
| **Python Props** | Full table of accepted kwargs. |
| **Python Usage** | Realistic examples of rendering it from a view, service, or async job. |
| **Styling & Customization** | How CSS classes, BEM modifiers, and theme variants are passed in. |
| **Extension Patterns** (where relevant) | Block overrides, per-call class swaps, and per-site overrides. |

A component that ships in more than one variant (e.g. `modal` / `modal_trigger` /
`modal_static`) gets its own short case study so you can compare trade-offs.

---

## Python Entry Points (Read This First)

Before diving into individual case studies, memorize these three patterns.
They are the only entry points you need to render any django-fusion
component from Python code.

### 1. The singleton `TemplateRenderer`

```python
from django_fusion.web.rendering import TemplateRenderer

renderer = TemplateRenderer.get_default()   # honours `OSOUL_TEMPLATE_RENDERER` setting
```

`TemplateRenderer` is a thin wrapper around `django.template.loader.render_to_string`
with extras for component rendering, email rendering, and `HttpResponse` building.

### 2. Three render methods you'll actually use

| Method | Returns | When to use |
|--------|---------|-------------|
| `renderer.render(template_name, ctx, request=request)` | `str` | Generic template render to string. |
| `renderer.render_component(component_name, props, request=request)` | `str` | Component render. **Auto-prepends `components/`** if missing. |
| `renderer.render_to_response(template_name, ctx, request=request, status=200)` | `HttpResponse` | Drop-in shortcut for a Django view return value. |

### 3. Canonical render rules

- Component names **always** use the `components/` prefix in `render()`. With `render_component()` you can omit it: `render_component("button.html", {...})` resolves to `components/button.html`.
- Pass `request=request` to enable context processors (`request.user`, `LANGUAGE_CODE`, `global_settings`, etc.).
- Any kwarg that the component doesn't declare as a prop is appended to `{{ attrs }}` (see [COMPONENT_TAG.md](./COMPONENT_TAG.md)).
- `css_class` is a *convention* — most components accept it as a top-level kwarg and append it to the root element. See the [Styling from Python](#styling-from-python-passing-css-classes-via-kwargs) recipe.

### 4. When to prefer `FragmentComponent` over `render_component`

Use `render_component(...)` for one-off rendering inside a view or email
job. Reach for `FragmentComponent` when you want:

- a routable HTMX endpoint (URL + view)
- auto-pagination (`paginate_by`)
- OOB fragment injection (`oob_fragments`)
- the `htmx_only` guard

See [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md) and
[`comp/routes/fragments.py`](../src/django_fusion/comp/routes/fragments.py)
for the full `FragmentComponent` API.

---

## Forms & Inputs

### Case Study: `form/form.html` — Unified Django Form

**Description**: Canonical Django form renderer with HTMX, multipart, field-level
success hints, cancel button, and block-extendable structure.

**Use Case**: The default for any `Form` / `ModelForm` rendering — especially when
the form lives inside a fragment that needs to swap itself out via HTMX.

**Template Syntax**:

```django
<div id="post-create-form" data-fragment>
  {% comp "components/form/form.html"
      form=form
      hx_post=request.path
      hx_target="#post-create-form"
      hx_swap="outerHTML"
      hx_indicator=".htmx-indicator"
      submit_label="Create Post"
      show_cancel=True
      cancel_label="Cancel"
      cancel_hx_get=list_url
      cancel_hx_target="#post-create-form"
      cancel_hx_swap="outerHTML" / %}
</div>
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `form` | `django.forms.Form` | *required* | Django form instance. |
| `hx_post` / `hx_url` | str | `None` | HTMX POST endpoint. Falls back to standard POST. |
| `hx_target` | str | `None` | HTMX target selector (e.g. `#result`). |
| `hx_swap` | str | `'outerHTML'` | HTMX swap strategy. |
| `hx_indicator` | str | `None` | HTMX loading spinner selector. |
| `is_multipart` | bool | auto | Force `multipart/form-data`. |
| `form_class` | str | `''` | Extra CSS classes on `<form>`. |
| `form_id` | str | `None` | `<form id="...">` attribute. |
| `form_action` | str | `None` | Non-HTMX `action=""` URL. |
| `form_method` | str | `'post'` | Non-HTMX HTTP method. |
| `form_extra_attrs` | safe str | `''` | Raw `<form>` attribute string. |
| `submit_label` | str | `'Submit'` | Submit button text. |
| `submit_attrs` | safe str | `''` | Raw submit-button attribute string. |
| `show_cancel` | bool | `False` | Render a cancel button. |
| `cancel_label` | str | `'Cancel'` | Cancel button text. |
| `cancel_onclick` | str | `None` | JS onclick for cancel. |
| `cancel_hx_get` | str | `None` | HTMX GET URL for cancel navigation. |
| `cancel_hx_target` | str | `None` | HTMX target for cancel. |
| `cancel_hx_swap` | str | `None` | HTMX swap for cancel. |
| `field_success` | str | `None` | Field name to highlight with a success hint. |
| `success_message` | str | `None` | Text of the success hint. |

**Python Usage**:

```python
# views.py
from django.views import View
from django_fusion.web.rendering import TemplateRenderer

class PostCreateFragment(View):
    """Render the form once, then re-render the same form for HTMX posts."""

    def get(self, request):
        form = PostForm()
        return TemplateRenderer.get_default().render_to_response(
            "components/form/form.html",
            {
                "form": form,
                "hx_post": request.path,
                "hx_target": "#post-create-form",
                "submit_label": "Create Post",
            },
            request=request,
        )

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            return TemplateRenderer.get_default().render_to_response(
                "components/notification.html",
                {},  # form swapped out entirely on success
                request=request,
                status=204,
            )
        # Re-render the same form with errors via the outer fragment.
        return TemplateRenderer.get_default().render_to_response(
            "components/form/form.html",
            {
                "form": form,
                "hx_post": request.path,
                "hx_target": "#post-create-form",
                "submit_label": "Create Post",
            },
            request=request,
        )
```

**Styling & Customization**:

The root `<form>` element gets `class="form-container {{ form_class }}"`. Pass
`form_class="form-container--compact"` from either Python or the template to
swap to a compact variant. The submit button and cancel button both accept
`btn` Bootstrap classes via `submit_attrs` / `cancel_hx_get` extras.

**Extension Patterns (Block Overrides)**:

`form/form.html` exposes **eight** `{% block %}` hooks for surgical customization.
Create a site-level template that extends it:

```django
{# myapp/templates/posts/post_form.html #}
{% extends "components/form/form.html" %}

{% block form_hidden_fields %}
    {{ block.super }}
    <input type="hidden" name="tenant_id" value="{{ request.tenant.id }}">
{% endblock %}

{% block form_actions %}
    <div class="form-actions form-actions--inline">
        <button type="submit" class="btn btn-primary btn-lg">Publish</button>
    </div>
{% endblock %}

{% block after_form %}
    <p class="text-muted small mt-2">By submitting you agree to the terms.</p>
{% endblock %}
```

Available blocks: `form_tag`, `form_hidden_fields`, `form_field_extra`,
`form_after_fields`, `form_actions`, `form_cancel_button`, `form_content_after`,
`after_form`.

---

### Case Study: `button.html` — Brand-Gradient CTA

**Description**: Generic styled button that flips between `<button>` and `<a>` and
supports a hover-reverse icon animation.

**Use Case**: Anywhere you need a Bootstrap-5 button with a brand-flavored
gradient variant — and where the element may be either a link or a button.

**Template Syntax**:

```django
{% comp "components/button.html"
    label="Contact With Us"
    variant="border-gradient"
    icon="feather-arrow-right"
    href="/contact/" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | str | *required* | Visible text. |
| `href` | str | `None` | If set, renders `<a>`; otherwise `<button>`. |
| `type` | str | `'button'` | Button `type` (ignored when `href` is set). |
| `variant` | str | `'primary'` | `primary` / `secondary` / `outline-primary` / `border-gradient` / `ghost` / `link` |
| `size` | str | `''` | `sm` / `md` / `lg` — emitted as `btn--{size}`. |
| `icon` | str | `None` | Icon class (e.g. `bi-check`, `feather-user`). |
| `icon_position` | str | `'right'` | `left` / `right`. |
| `block` | bool | `False` | Full-width (`d-block w-100`). |
| `css_class` | str | `''` | Extra CSS classes appended to the root. |
| `extra_attrs` | safe str | `''` | Raw HTML attribute string (e.g. `data-bs-toggle="modal"`). |

**Python Usage**:

```python
from django_fusion.web.rendering import TemplateRenderer

# Simple: render to string for an HTMX-OOB swap
btn = TemplateRenderer.get_default().render_component(
    "button.html",
    {
        "label": "Download PDF",
        "variant": "outline-primary",
        "icon": "bi-download",
        "href": "/exports/report.pdf",
        "css_class": "mt-3 shadow-sm",
    },
)
```

**Styling & Customization**:

The component emits `class="btn btn--{variant} btn--{size} {css_class}"`. To
introduce a new variant, add a SCSS rule in your theme:

```scss
// applications/assets/static/styles/components/_button.scss
.btn--border-gradient {
    background: linear-gradient(90deg, #6366f1, #ec4899);
    color: #fff;
    border: 0;
}
```

Then reference it via `variant="border-gradient"`. Variants are not
typed in Python — the field is just a string — so you can drop in custom
variants per site without forking the template.

**Icon Reverse Animation**:

When `icon_position != 'left'`, the component renders the icon twice
inside `.icon-reverse-wrapper.has-icon` so a CSS hover state can flip them.

---

### Case Study: `submit_button.html` — HTMX Submit with Spinner

**Description**: A form-submit button that emits an inline HTMX indicator
spinner and a `hx-confirm` dialog.

**Use Case**: Place inside any `<form>` (including the one rendered by
`form/form.html`) to get a submit button that *shows* loading state without
extra JS.

**Template Syntax**:

```django
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    {% comp "components/submit_button.html"
        label="Save"
        hx_indicator="#save-spinner" / %}
</form>
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `label` | str | `'Submit'` | Visible text. |
| `variant` | str | `'primary'` | Bootstrap variant: `primary` / `secondary` / `outline-primary` / `success` / `danger`. |
| `size` | str | — | `sm` / `md` (default; no class) / `lg` — emitted as `btn-sm` / `btn-lg`. |
| `icon` | str | `None` | Icon class. |
| `icon_position` | str | `'right'` | `left` / `right`. |
| `hx_indicator` | str | `None` | When set, renders an inline spinner with this id. |
| `hx_confirm` | str | `None` | HTMX confirmation dialog text. |
| `confirm_text` | str | `None` | Alias for `hx_confirm` (form.html convention). |
| `disabled` | bool | `False` | Render as `disabled`. |
| `css_class` | str | `''` | Extra CSS classes. |
| `extra_attrs` | safe str | `''` | Raw HTML attribute string. |

**Python Usage**:

```python
# forms/handlers.py
from django_fusion.web.rendering import TemplateRenderer

def render_delete_button(item_id: int) -> str:
    return TemplateRenderer.get_default().render_component(
        "submit_button.html",
        {
            "label": "Delete",
            "variant": "danger",
            "confirm_text": f"Delete item #{item_id}? This cannot be undone.",
            "css_class": "btn--sm",
            "extra_attrs": f'hx-delete="/api/items/{item_id}/" hx-target="#item-{item_id}" hx-swap="outerHTML"',
        },
    )
```

**Styling & Customization**:

The root `<button>` gets `class="btn btn-{variant} [btn-sm|btn-lg] d-flex align-items-center gap-2 {css_class}"`. The variant uses the **standard Bootstrap** `btn-primary` /
`btn-danger` names, not the BEM `btn--primary` form. Spinner placement and
colour follow the inline `spinner-border` from Bootstrap.

> **Note**: This component does **not** render `<form>`. CSRF is the host
> form's responsibility. Pair it with the form component (`form/form.html`)
> or your own `<form>`.

---

### Case Study: `form_field.html` — Wagtail-Block-Aware Field Renderer

**Description**: A single-field renderer (textarea / select / checkbox / radio /
file / text / email / password / number) that accepts BEM-class overrides per
call and is Wagtail-StreamField-block aware.

**Use Case**: StreamField custom blocks that need to render a field
description from a Wagtail block context. Also useful for synthesizing a
fake block context to render a single field outside a stream field.

**Template Syntax**:

```django
{# From within a Wagtail StreamField block template #}
{% comp "components/form/form_field.html"
    block=block
    field_config=field
    css_class="form-field--compact" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `block` | block | `None` | Wagtail `StructBlock` instance (or any namespace with `.value.*` and `.id`). |
| `field_config` | dict | *required* | Field definition dict: `name`, `field_type`, `label`, `placeholder`, `default_value`, `required`, `min_length`, `max_length`, `pattern`, `icon`, `choices`, `help_text`. |
| `class_field` | str | `'form-field'` | Override for outer container class. |
| `class_input_group` | str | `'form-input-group'` | Override for input-group wrapper. |
| `class_icon` | str | `'form-icon'` | Override for icon container. |
| `class_label` | str | `'form-label'` | Override for label. |
| `class_control` | str | `'form-control'` | Override for control wrapper. |
| `class_textarea` | str | `'form-textarea'` | Override for textarea. |
| `class_select` | str | `'form-select'` | Override for `<select>`. |
| `class_checkbox` / `class_checkbox_label` / `class_checkbox_group` | str | `form-checkbox*` | Per-element BEM overrides. |
| `class_radio` / `class_radio_label` / `class_radio_group` / `class_radio_item` | str | `form-radio*` | Per-element BEM overrides. |
| `class_file` | str | `'form-file'` | Override for `<input type="file">`. |
| `class_input` | str | `'form-input'` | Override for generic text input. |
| `class_help_text` | str | `'form-help-text'` | Override for help-text div. |
| `class_error` | str | `'form-error'` | Override for error container. |

**Python Usage (synthesized block context)**:

```python
# Use the helper tag to convert a dict into a block-like namespace
from types import SimpleNamespace
from django_fusion.web.rendering import TemplateRenderer

def render_single_field(field_def: dict) -> str:
    block = SimpleNamespace(id="synth", value={"show_icons": True, "show_labels": True})
    return TemplateRenderer.get_default().render_component(
        "form_field.html",
        {"block": block, "field_config": field_def},
    )

# Or pass the same dict directly — `block.value.*` lookups fall back
# to attribute access on a SimpleNamespace built by the helper tag
# `{% as_form_block <dict> as block %}` in templates.
```

**Styling & Customization**:

Per-call class overrides are the primary extension surface. The
canonical BEM classes (`form-field`, `form-input`, `form-select`, …) are
the defaults; every one has a `class_*` override. The component also
honours `block.value.layout` (`two-column`, `split`) to compose a
responsive grid automatically.

**Extension Patterns (Block Overrides)**:

`form_field.html` defines `{% block field_icon %}`, `{% block field_label %}`, and
`{% block field_input %}` so you can `{% extends "components/form/form_field.html" %}`
and override any one of them without rewriting the rest.

---

## Modals

### Case Study: `modal.html` — Trigger + Skeleton Combo

**Description**: A combined HTMX trigger button and the modal skeleton it opens —
the most common "click-to-edit" pattern.

**Use Case**: One-shot modal flows: "Edit user", "Confirm delete", "Show details".
Use this when the trigger and the modal are tightly coupled and rendered in
the same place.

**Template Syntax**:

```django
{% comp "components/modal.html"
    modal_id="userModal"
    hx_url="/api/users/42/edit/"
    modal_title="Edit User"
    modal_icon="bi-person"
    modal_size="modal-lg"
    submit_label="Save changes" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modal_id` | str | *required* | Unique HTML id (becomes the `#target`). |
| `hx_url` | str | `None` | URL the trigger fetches into `#modal_id-body`. |
| `modal_title` | str | `''` | Header title. |
| `modal_icon` | str | `None` | Bootstrap icon class (e.g. `bi-person`). |
| `modal_size` | str | `'modal-md'` | `modal-sm` / `modal-md` / `modal-lg` / `modal-xl`. |
| `modal_centered` | bool | `True` | Vertically centre the dialog. |
| `modal_scrollable` | bool | `False` | Long-content scroll mode. |
| `modal_body_content` | safe str | `''` | Static body HTML (ignored when `hx_url` is set). |
| `show_trigger` | bool | `True` | Render the trigger button. |
| `btn_label` | str | `''` | Trigger button text. |
| `btn_class` | str | `'btn btn-primary'` | Trigger button classes. |
| `btn_icon` | str | `None` | Trigger button icon. |
| `hx_indicator` | str | `None` | HTMX loading spinner selector. |
| `show_close_button` | bool | `True` | Render the default footer close button. |
| `extra_attrs` | safe str | `''` | Raw HTML attribute string on the trigger. |

**Python Usage (HTMX view returning a modal body)**:

```python
# views.py
from django_fusion.web.rendering import TemplateRenderer
from django.views import View
from django.http import HttpResponse

class UserEditModalBody(View):
    def get(self, request, pk):
        user = User.objects.get(pk=pk)
        form = UserForm(instance=user)
        # The view returns *just the body*, not the modal shell.
        # The shell was already rendered next to the trigger.
        return TemplateRenderer.get_default().render_to_response(
            "components/form/form.html",
            {
                "form": form,
                "hx_post": f"/api/users/{pk}/edit/",
                "hx_target": "#user-edit-fragment",
                "submit_label": "Save",
            },
            request=request,
        )
```

**Styling & Customization**:

The trigger button accepts arbitrary Bootstrap classes via `btn_class`
(default `btn btn-primary`). The dialog itself uses Bootstrap's
`modal-dialog-{size}` family and `modal-dialog-centered` /
`modal-dialog-scrollable` for behaviour flags. Pass `css_class` via
`extra_attrs` to layer site-specific classes on the trigger.

---

### Case Study: `modal_trigger.html` — Reusable Trigger Button

**Description**: A standalone trigger button that loads content into a
pre-existing modal skeleton.

**Use Case**: When the modal skeleton is rendered once at the top of a
page and many different buttons (or rows in a list) each open it with
their own content.

**Template Syntax**:

```django
<button class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#userModal">
  Open modal
</button>
{% comp "components/modal_trigger.html"
    hx_url="/users/42/edit/"
    hx_target="#userModal-body"
    icon="bi-pencil"
    label="Edit User" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `hx_url` | str | *required* | URL that returns the modal body. |
| `hx_target` | str | `'#modal-container'` | CSS selector to swap content into. |
| `hx_swap` | str | `'innerHTML'` | HTMX swap strategy. |
| `hx_indicator` | str | `None` | HTMX loading spinner selector. |
| `btn_class` | str | `'btn btn-primary'` | Trigger button classes. |
| `icon` | str | `None` | Bootstrap icon class. |
| `label` | str | `''` | Button text. |
| `extra_attrs` | safe str | `''` | Raw HTML attribute string. |

**Python Usage**:

```python
# services/tables.py — return a list of triggers for a user table
from django_fusion.web.rendering import TemplateRenderer

def render_edit_triggers(user_ids):
    renderer = TemplateRenderer.get_default()
    return [
        renderer.render_component(
            "modal_trigger.html",
            {
                "hx_url": f"/api/users/{uid}/edit/",
                "hx_target": "#userModal-body",
                "icon": "bi-pencil",
                "label": "Edit",
                "btn_class": "btn btn-sm btn-outline-secondary",
            },
        )
        for uid in user_ids
    ]
```

---

### Case Study: `modal_static.html` — Block-Extendable Skeleton

**Description**: A static modal skeleton with `{% block %}` hooks for
`title`, `body`, and `footer`. No trigger.

**Use Case**: When you want to extend the modal in a site template and
provide your own title, body, or footer. Pair with `modal_trigger.html` or
your own `data-bs-toggle` button.

**Template Syntax**:

```django
{% comp "components/modal_static.html"
    id="confirmDelete"
    title="Confirm Delete"
    size="modal-md"
    centered=True
    close_text="Cancel"
    primary_action=True
    primary_action_text="Yes, delete"
    primary_action_id="confirm-delete-btn" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `id` | str | `'genericModal'` | Unique HTML id. |
| `title` | str | `''` | Title text. |
| `body` | safe str | `''` | Static body HTML. |
| `size` | str | `''` | `modal-sm` / `modal-lg` / `modal-xl`. |
| `centered` | bool | `False` | Vertically centre. |
| `scrollable` | bool | `False` | Long-content scroll. |
| `backdrop` | str/None | `None` | `'static'`, `'true'`, or `False`. |
| `keyboard` | bool | `True` | Allow ESC closing. |
| `show_footer` | bool | `True` | Render default footer. |
| `close_text` | str | `'Close'` | Footer close button label. |
| `primary_action` | bool | `False` | Show default primary action button. |
| `primary_action_id` | str | `None` | id for primary action. |
| `primary_action_click` | str | `None` | JS onclick for primary action. |
| `primary_action_text` | str | `'Save changes'` | Primary action label. |

**Extension Patterns (Block Overrides)**:

`modal_static.html` defines `{% block title %}`, `{% block body %}`, and
`{% block footer %}`. A child template can extend it:

```django
{# myapp/templates/posts/confirm_delete.html #}
{% extends "components/modal_static.html" %}

{% block title %}Delete post?{% endblock %}

{% block body %}
    <p>Are you sure you want to delete <strong>{{ post.title }}</strong>?</p>
    <p class="text-muted small">This action cannot be undone.</p>
{% endblock %}

{% block footer %}
    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">No, keep it</button>
    <form method="post" action="{{ post.get_delete_url }}" style="display:inline">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger">Yes, delete</button>
    </form>
{% endblock %}
```

**Styling & Customization**:

Standard Bootstrap modal classes — no extra BEM. The `size`, `centered`, and
`scrollable` flags directly emit `modal-dialog-{size}`,
`modal-dialog-centered`, and `modal-dialog-scrollable`.

---

## Notifications

### Case Study: `notification.html` — Drop-In Notification Center

**Description**: A unified notification system with toasts (auto-dismiss),
alerts (inline persistent), popups (modal-style), Django messages bridge,
and an optional SSE live-update indicator. Includes a JavaScript API.

**Use Case**: Include once in `base.html` just before `</body>`. Then trigger
notifications from server responses (HTMX OOB toasts) or from any
JavaScript (API: `showToast`, `showAlert`, `showPopup`).

**Template Syntax**:

```django
{# In your base.html, just before </body> #}
{% comp "components/notification.html" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `hx_connection` | str | `None` | SSE endpoint URL; if unset, the SSE indicator is hidden. |

**Python Usage (HTMX view returning an OOB toast)**:

```python
# views.py
from django_fusion.web.rendering import TemplateRenderer
from django.http import HttpResponse
from django.contrib import messages

def save_profile(request):
    profile = request.user.profile
    profile.save()
    messages.success(request, "Profile saved!")

    # Return an OOB toast that injects itself into #toast-container
    toast_html = TemplateRenderer.get_default().render_component(
        "toast-success",
        {"message": "Profile saved!"},
        request=request,
    )
    # Wrap in the swap target id so hx-swap-oob resolves
    return HttpResponse(
        f'<div id="toast-container" hx-swap-oob="beforeend">{toast_html}</div>'
    )
```

**JavaScript API** (auto-bound after the component mounts):

```javascript
// Simple toast
showToast('success', 'File uploaded!', 'Upload Complete', 7000);

// Persistent alert (returns to the page on next render)
showAlert({
    level: 'warning',
    title: 'Heads up',
    message: 'Your session expires in 5 minutes.',
    details: 'Click here to extend your session.',
});

// Shorthand for danger-level alert
showErrorAlert('Failed to save changes.');

// Modal-style popup
showPopup({
    title: 'Confirm action',
    message: '<p>Are you sure?</p>',
    showCancel: true,
    size: 'modal-sm',
});
```

**HTMX OOB Templates** (shipped with the component, renderable individually):

- `toast-success` — green, 5 s auto-dismiss
- `toast-error` — red, 7 s auto-dismiss
- `toast-warning` — yellow, 5 s
- `toast-info` — blue, 5 s

**Styling & Customization**:

The component ships with its own CSS class family
(`notification-system__*`, `notification-system--fixed`) which your
theme should style. The `level` parameter on `showToast` /
`showAlert` selects the Bootstrap contextual colour (`bg-success`,
`bg-danger`, etc.) — the icons auto-resolve. Override the icon
explicitly by passing `icon` in `showAlert({...})`.

**SSE live updates**:

Pass `hx_connection="/api/notifications/stream/"` to enable the live
indicator. The widget auto-connects on page load when an authenticated
user is present.

---

### Case Study: `notification_small.html` — Inline Status Pill

**Description**: A minimal inline status indicator that sits beside form
fields, list items, or page sections.

**Use Case**: Where `notification.html` is too heavy — small inline
status messages, validation hints, list-item badges.

**Template Syntax**:

```django
{% comp "components/notification_small.html"
    level="success"
    message="Profile updated." / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `level` | str | `'info'` | `success` / `info` / `warning` / `danger`. |
| `message` | str | *required* | Notification text. |
| `icon` | str | auto | Override the auto-selected icon. |
| `title` | str | `None` | Optional small bold label. |
| `dismissible` | bool | `False` | Add a close button. |
| `css_class` | str | `''` | Extra CSS classes. |

**Python Usage**:

```python
# forms/validators.py
from django_fusion.web.rendering import TemplateRenderer

def render_validation_hint(field_name: str) -> str:
    return TemplateRenderer.get_default().render_component(
        "notification_small.html",
        {
            "level": "success",
            "title": field_name.title(),
            "message": "Looks good!",
            "css_class": "mt-1",
        },
    )
```

**Styling & Customization**:

`css_class` is the primary extension point. The component emits
`class="notification-small notification-small--{level} {css_class}"` so
themes can override `--{level}` colour sets in SCSS.

---

## Pagination

### Case Study: `pagination.html` — HTMX + Unpoly Pagination

**Description**: Standard prev/next/numbered pagination controls with
ellipsis, HTMX fragment support, and Unpoly fallbacks.

**Use Case**: Any paginated list view that wants consistent navigation
across full-page reloads and HTMX partial swaps.

**Template Syntax**:

```django
{% comp "components/pagination.html"
    page_obj=page_obj
    query_string=query_string
    hx_target="#post-list" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `page_obj` | `Page` | *required* | Django paginator `Page` object. |
| `query_string` | str | `''` | Pre-computed `request.GET` sans `page`. |
| `hx_target` | str | `'#fusion-content'` | HTMX swap target. |

**Python Usage**:

```python
# views.py
from django.core.paginator import Paginator
from django_fusion.web.rendering import TemplateRenderer

class PostListView(View):
    def get(self, request):
        posts = Post.objects.published().order_by("-created_at")
        page_obj = Paginator(posts, 20).get_page(request.GET.get("page", 1))

        # Build a query string sans `page` so pagination preserves filters
        query_string = "&".join(
            f"{k}={v}" for k, v in request.GET.items() if k != "page"
        )

        return TemplateRenderer.get_default().render_to_response(
            "posts/list.html",
            {
                "page_obj": page_obj,
                "query_string": query_string,
            },
            request=request,
        )
```

**Styling & Customization**:

Standard Bootstrap 5 `pagination pagination-sm justify-content-center`
classes — the page-item / page-link BEM is dropped. The entry-count
summary is a `blocktrans`-wrapped `<div class="text-center text-muted small mt-2">`
that you can override by extending the template.

---

### Case Study: `pagination/load_more.html` — "Load More" Button

**Description**: A click-to-append button that fetches the next page and
appends it to a target via HTMX.

**Use Case**: Feed-style listings, product grids, infinite-results views
where the user explicitly opts in to more content.

**Template Syntax**:

```django
{% comp "components/pagination/load_more.html"
    page_obj=page_obj
    hx_target="#product-grid"
    hx_indicator="#load-more-spinner" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `page_obj` | `Page` | *required* | Django `Page` object. |
| `hx_target` | str | `'#product-grid'` | Selector to append into. |
| `hx_swap` | str | `'beforeend'` | HTMX swap strategy. |
| `hx_indicator` | str | `'#load-more-spinner'` | HTMX loading spinner. |
| `css_class` | str | `''` | Extra CSS classes on the wrapper. |

**Styling & Customization**:

Wrapper class is `pagination-load-more text-center mt-4 {css_class}`.
The button itself is `btn btn-outline-primary` — override via
`extra_attrs` if you need a different style.

---

### Case Study: `pagination/infinite.html` — Intersection-Observer Scroll

**Description**: An invisible sentinel that auto-fetches the next page
when the user scrolls it into view (HTMX `intersect once`).

**Use Case**: Social feeds, blog streams, news tickers — anywhere you
want true infinite scroll without the user clicking.

**Template Syntax**:

```django
{% comp "components/pagination/infinite.html"
    page_obj=page_obj
    hx_target="#feed" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `page_obj` | `Page` | *required* | Django `Page` object. |
| `hx_target` | str | `'#product-grid'` | Selector to append into. |
| `hx_swap` | str | `'beforeend'` | HTMX swap strategy. |
| `hx_indicator` | str | `'#infinite-spinner'` | HTMX loading spinner. |

**Styling & Customization**:

The wrapper is `pagination-infinite` with a centred `<div>` spinner. To
hide the sentinel entirely once the last page is reached, simply omit
the include — `pagination/infinite.html` is a no-op when
`page_obj.has_next()` is false.

---

## Tables & Search

### Case Study: `table.html` — django-tables2 + Explicit Modes

**Description**: Unified table renderer that accepts either a
`django-tables2.Table` instance or an explicit `headers` / `rows` pair.

**Use Case**: One template covers both the legacy explicit-headers
pattern and a modern django-tables2 integration.

**Template Syntax**:

```django
{# Explicit mode #}
{% comp "components/table.html"
    headers=headers
    rows=rows
    hx_target="#user-table" / %}

{# django-tables2 mode #}
{% comp "components/table.html" table=user_table / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `table` | `django_tables2.Table` | `None` | If set, used directly. |
| `headers` | list | `None` | `[{label, sort_url, is_sorted, direction}, …]`. |
| `rows` | list | `None` | `[[cell, cell, …], …]`. |
| `hx_target` | str | `'#table-container'` | HTMX sort-link target. |
| `table_class` | str | `''` | Extra CSS classes on `<table>`. |
| `empty_message` | str | `'No records found'` | Empty-state text. |

**Python Usage**:

```python
# views.py
import django_tables2 as tables
from django_fusion.web.rendering import TemplateRenderer

class UserTable(tables.Table):
    class Meta:
        model = User
        fields = ("email", "full_name", "is_active")

def render_user_table(users) -> str:
    table = UserTable(users)
    return TemplateRenderer.get_default().render_component(
        "table.html",
        {"table": table, "hx_target": "#user-list"},
    )

# Or explicit mode
def render_users_explicit(users) -> str:
    headers = [
        {"label": "Email", "sort_url": "?sort=email"},
        {"label": "Name", "sort_url": "?sort=name"},
        {"label": "Status", "sort_url": "?sort=status"},
    ]
    rows = [[u.email, u.get_full_name(), "Active" if u.is_active else "Inactive"] for u in users]
    return TemplateRenderer.get_default().render_component(
        "table.html",
        {"headers": headers, "rows": rows},
    )
```

**Styling & Customization**:

Default classes: `table table-hover align-middle mb-0 {table_class}` with
`table-light` on thead and `border-top-0` on tbody. Empty state uses
`bi-inbox` icon and a muted centre-aligned cell.

---

### Case Study: `search.html` — HTMX Search w/ Filter Preservation

**Description**: A search form that submits via HTMX GET and preserves
hidden filter values.

**Use Case**: Filterable list views where the user expects their filters
to survive a search.

**Template Syntax**:

```django
{% comp "components/search.html"
    search_query=search_query
    hx_target="#user-list"
    extra_filters=extra_filters / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `search_query` | str | `''` | Current search term. |
| `search_placeholder` | str | `'Search…'` | Placeholder text. |
| `hx_target` | str | `None` | HTMX target (required for fragment mode). |
| `hx_get` | str | `None` | Override HTMX GET URL (defaults to `request.path`). |
| `extra_filters` | dict | `None` | Additional filter name→value to preserve as hidden inputs. |
| `max_width` | str | `'320px'` | Wrapper max-width. |

**Python Usage**:

```python
# views.py
from django_fusion.web.rendering import TemplateRenderer

def render_user_search(request) -> str:
    return TemplateRenderer.get_default().render_component(
        "search.html",
        {
            "search_query": request.GET.get("q", ""),
            "hx_target": "#user-list",
            "search_placeholder": "Search by name or email…",
            "extra_filters": {
                "status": request.GET.get("status", ""),
                "role": request.GET.get("role", ""),
            },
        },
    )
```

**Styling & Customization**:

Input group uses Bootstrap 5 `input-group input-group-sm`. The
`max_width` kwarg sets an inline `style="max-width:{value}"` so it
overrides cleanly without a SCSS change.

---

### Case Study: `breadcrumbs.html` — Schema.org + Unpoly

**Description**: Schema.org `BreadcrumbList` markup with Unpoly and
HTMX link support.

**Use Case**: Any navigable page that wants SEO-friendly breadcrumb
JSON-LD plus Unpoly/HTMX fragment navigation.

**Template Syntax**:

```django
{% comp "components/breadcrumbs.html" / %}
{# relies on the `breadcrumbs` context variable being set #}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `breadcrumbs` | list | `[]` | `[{title, url}, …]` from the view's `get_breadcrumbs()`. |
| `unpoly_enabled` | bool | `True` | Toggle Unpoly vs HTMX attribute emission. |

**Python Usage**:

```python
# views.py
from django_fusion.web.rendering import TemplateRenderer

class PageView(View):
    def get(self, request, slug):
        page = Page.objects.get(slug=slug)
        return TemplateRenderer.get_default().render_to_response(
            "pages/detail.html",
            {
                "page": page,
                "breadcrumbs": [
                    {"title": "Home", "url": "/"},
                    {"title": "Blog", "url": "/blog/"},
                    {"title": page.title, "url": page.get_absolute_url()},
                ],
            },
            request=request,
        )
```

**Styling & Customization**:

Bootstrap `breadcrumb` / `breadcrumb-item` classes. Override the wrapper
with `class="breadcrumbs mb-3"` via the auto-included `{{ attrs }}`.

---

## Chat & Cookies

### Case Study: `chat/bubble.html` — Floating AI Chat Widget

**Description**: A floating chat bubble with a slide-up panel, typing
indicator, unread badge, and `fetch`-based message submission.

**Use Case**: Embedding an AI/chat assistant in the corner of any page.
Pairs with the ceptor × nawaai backend exposed by `ceptor-ai`.

**Template Syntax**:

```django
{% comp "components/chat/bubble.html"
    chat_title="Support Bot"
    chat_placeholder="Ask a question…"
    chat_greeting="Hi! How can I help?" / %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `chat_config` | JSON str | `'{}'` | JSON-serialised config dict embedded as `data-config`. |
| `chat_title` | str | `'Assistant'` | Header name. |
| `chat_placeholder` | str | `'Type a message…'` | Input placeholder. |
| `chat_greeting` | str | `'Hi! How can I help you today?'` | First bot message. |
| `chat_endpoint` | str | `None` | Override POST endpoint URL. |

**Python Usage**:

```python
# views.py
from django_fusion.web.rendering import TemplateRenderer

def render_chat_widget(request) -> str:
    config = {
        "endpoint": "/api/chat/stream/",
        "user_id": request.user.id if request.user.is_authenticated else None,
        "language": request.LANGUAGE_CODE,
    }
    import json
    return TemplateRenderer.get_default().render_component(
        "chat/bubble.html",
        {
            "chat_config": json.dumps(config),
            "chat_title": "Structa Assistant",
            "chat_endpoint": "/api/chat/stream/",
        },
    )
```

**Styling & Customization**:

The component ships with its own scoped CSS using CSS custom properties
(`--ceptor-chat-primary`, `--ceptor-chat-radius`, etc.). Override them in
your theme to rebrand without forking the template:

```scss
:root {
    --ceptor-chat-primary: #6366f1;     /* brand primary */
    --ceptor-chat-primary-dark: #4f46e5;
    --ceptor-chat-radius: 0.75rem;     /* tighter than default */
}
```

**Behaviour**:

The widget manages its own session ID via `sessionStorage` (key
`ceptor_chat_sid`) and posts `{message, session_id}` JSON to the
configured endpoint. CSRF token is read from the page.

---

### Case Study: `cookies/cookie-consent.html` — Cookie Preferences UI

**Description**: A `<template>` element containing the cookie preferences
form (essential / analytics / marketing / preferences). Designed to be
cloned into a modal by `cookie-consent.js`.

**Use Case**: GDPR/CCPA-style consent dialogs. Render once in `base.html`;
`cookie-consent.js` clones the template into a `bootbox` dialog when the
user clicks "Manage cookies".

**Template Syntax**:

```django
{% comp "components/cookies/cookie-consent.html" / %}
```

**Python Props**: None — pure markup.

**Python Usage**:

```python
# base.py
from django_fusion.web.rendering import TemplateRenderer

def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    # Pre-render the cookie modal so cookie-consent.js can clone it
    ctx["cookie_consent_html"] = TemplateRenderer.get_default().render_component(
        "cookies/cookie-consent.html"
    )
    return ctx
```

**Styling & Customization**:

Bootstrap 5 `form-check` classes throughout. To add a new cookie
category, append a new `<div class="form-check">` block. The template
id (`cookie-consent-template`) is hardcoded — `cookie-consent.js`
looks it up by that id.

**Companion templates**:
- `cookies/cookie-policy.html` — cookie policy content (template id
  `cookie-policy-template`)
- `cookies/privacy-policy.html` — privacy policy content (template id
  `privacy-policy-template`)

All three follow the same `<template id="...">` pattern.

---

## Navigation

### Case Study: `navigation/nav_link.html` — Single Nav Link

**Description**: A single navigation link that emits Unpoly (`up-follow`
/ `up-target`) when `UNPOLY_ENABLED=True` and HTMX (`hx-get` /
`hx-target`) when False.

**Use Case**: Building menus, breadcrumbs, sidebars one link at a time.

**Template Syntax**:

```django
{% nav_link url="/blog/" label="Blog" icon="bi-newspaper" target="#fusion-content" %}
```

**Python Props**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `url` | str | *required* | href / hx-get target. |
| `label` | str | *required* | Display text. |
| `icon` | str | `None` | Icon class (e.g. `bi-house`). |
| `attrs` | safe str | `''` | Pre-rendered HTML attribute string. |
| `is_active` | bool | `False` | Whether the link matches the current page. |
| `target` | str | `None` | Swap target selector. |
| `layer` | str | `None` | Unpoly layer (modal / drawer / popup). |
| `unpoly_enabled` | bool | `True` | Toggle Unpoly vs HTMX attribute emission. |

**Python Usage**:

```python
# services/nav.py
from django_fusion.web.rendering import TemplateRenderer
from django_fusion.comp.templatetags.navigation import _build_attrs

def render_nav_link(request, item) -> str:
    attrs = _build_attrs(
        url=item["url"],
        target="#fusion-content",
        layer="modal" if item.get("modal") else None,
    )
    return TemplateRenderer.get_default().render_component(
        "navigation/nav_link.html",
        {
            "attrs": attrs,
            "url": item["url"],
            "label": item["title"],
            "icon": item.get("icon"),
            "is_active": request.path == item["url"],
        },
    )
```

**Styling & Customization**:

Renders an `<a>` with `class="nav-link"` from the `attrs` passthrough
plus `active` (when `is_active`). Use the `attrs` kwarg to layer
additional CSS classes per call.

---

### Case Study: `menu/app_menu.html` + `menu/site_menu.html`

**Description**: Two composing menu components — `app_menu` renders the
items of one `Application`, `site_menu` composes a list of
`Application` instances and delegates each to `app_menu`.

**Use Case**: The site-level navigation menu that appears in the header
or sidebar, with per-app sub-menus.

**Template Syntax**:

```django
{# Top-level site menu #}
{% comp "components/menu/site_menu.html" / %}

{# Single app menu #}
{% comp "components/menu/app_menu.html" app=blog_app / %}
```

**Python Props**:

**`menu/app_menu.html`**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `app` | `Application` | *required* | `Application` instance. |
| `items` | list | from `app.menu_items()` | Pre-resolved menu items. |
| `user` | `User` | `None` | Current user (for permission checks). |
| `request` | `HttpRequest` | `None` | Current request (for URL resolution). |

**`menu/site_menu.html`**:

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `site` | `Site` | *required* | The `Site` instance. |
| `apps` | list | from `site.applications` | Application list. |
| `user` | `User` | `None` | Current user. |
| `request` | `HttpRequest` | `None` | Current request. |

**Python Usage**:

```python
# views.py
from django_fusion.web.rendering import TemplateRenderer
from django_fusion.routes.core.sites import Site

def render_main_menu(request) -> str:
    site = Site.get_current(request)
    return TemplateRenderer.get_default().render_component(
        "menu/site_menu.html",
        {
            "site": site,
            "apps": site.applications,
            "user": request.user,
            "request": request,
        },
    )
```

**Styling & Customization**:

`app_menu` emits `class="app-menu nav flex-column"` with BEM children
(`app-menu__item`, `app-menu__link`, `app-menu__icon`,
`app-menu__label`). `site_menu` emits `class="site-menu"` with
`site-menu__app`, `site-menu__app-header`, `site-menu__icon`, etc. All
classes are BEM-style and themeable.

---

## Cross-Cutting Recipes

### Styling from Python: passing CSS classes via kwargs

Most components accept a `css_class` kwarg (and a few also accept
`extra_attrs`). Convention:

- **`css_class`** — appends to the root element's class list. Use this
  for size, position, and theme variants (`css_class="btn--lg mt-3"`).
- **`extra_attrs`** — raw attribute string emitted on the root element
  (or button, depending on the component). Use this for `data-*` /
  `aria-*` / Bootstrap behaviour attributes
  (`extra_attrs='data-bs-toggle="modal"'`).
- **Per-element BEM overrides** — `form_field.html` exposes 14
  `class_*` kwargs (`class_label`, `class_checkbox`, …) for sites that
  need to rebrand individual sub-elements.

```python
# Standard pattern: theme a component without forking the template
button = TemplateRenderer.get_default().render_component(
    "button.html",
    {
        "label": "Get Started",
        "variant": "border-gradient",
        "css_class": "btn--xl mt-3 shadow-lg",        # layout / theme
        "extra_attrs": 'data-analytics="cta-click"',  # analytics attrs
    },
)
```

### Customizing a component for one site only

Two clean strategies, in order of preference:

1. **Block extension**: Create a site-local template that `{% extends %}`
   the component and overrides only the blocks you care about
   (`{% block form_actions %}`, `{% block title %}`, `{% block field_input %}`…).
2. **Template directory priority**: Drop a same-named file in a
   higher-priority template directory (`applications/<site>/templates/`
   or `applications/<site>/www/<app>/templates/`). Django's
   `TEMPLATES["DIRS"]` resolves the closer file first.

Avoid editing `django_fusion/comp/templates/components/*` directly — the
package is version-pinned and will be overwritten on upgrade.

### Block extension patterns

`{% extends "components/<file>.html" %}` works on any component that
defines `{% block %}` regions. The full list of available blocks is
documented per-component in [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md)
and in the comments at the top of each template. The most commonly
extended components are:

- `form/form.html` — 8 blocks (`form_tag`, `form_hidden_fields`,
  `form_field_extra`, `form_after_fields`, `form_actions`,
  `form_cancel_button`, `form_content_after`, `after_form`)
- `modal_static.html` — 3 blocks (`title`, `body`, `footer`)
- `form_field.html` — 3 blocks (`field_icon`, `field_label`, `field_input`)

### Theming via component directories

Each site can ship its own component directory
(`applications/<site>/www/<app>/templates/components/`) and Django's
`TEMPLATES` setting will find site-specific overrides before
falling through to the package defaults. The auto-registration in
`CoreExtAppConfig.ready()` walks every `*.html` under
`COMPONENTS_INCLUDE_PATH_ROOTS`, so a site-local `button.html` is
automatically registered under the same component name.

### Returning a fragment from Python with `FragmentComponent`

`FragmentComponent` is the route-driven equivalent of
`render_component()`. Use it when you want a URL endpoint, not just a
string:

```python
from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.web.rendering import TemplateRenderer

class PostPreviewFragment(FragmentComponent):
    route_path = "blog/<slug:slug>/preview/"
    fragment_name = "blog.fragments.post_preview"
    template_name = "blog/post_detail.html"   # full-page fallback
    htmx_only = False
    paginate_by = None

    def get_queryset(self):
        return Post.objects.published()

    def get_fragment_context(self, **kwargs):
        ctx = super().get_fragment_context(**kwargs)
        ctx["post"] = self.get_object()
        return ctx
```

The view renders the fragment template directly (no layout wrapper) when
called with `HX-Request: true`, and the full-page template otherwise.

---

## Recipe Index

| Recipe | Component(s) | Link |
|--------|--------------|------|
| Render a button to string for an API payload | `button.html` | [Case Study](#case-study-buttonhtml--brand-gradient-cta) |
| Form HTMX submission with inline cancel button | `form/form.html` | [Case Study](#case-study-formformhtml--unified-django-form) |
| Dispatch a success toast via `render_component` | `notification.html` | [Case Study](#case-study-notificationhtml--drop-in-notification-center) |
| Inline status pill next to a form field | `notification_small.html` | [Case Study](#case-study-notification_smallhtml--inline-status-pill) |
| HTMX-driven "Load More" pagination | `pagination/load_more.html` | [Case Study](#case-study-paginationload_morehtml--load-more-button) |
| Intersection-observer infinite scroll | `pagination/infinite.html` | [Case Study](#case-study-paginationinfinitehtml--intersection-observer-scroll) |
| Trigger a modal from a list row | `modal_trigger.html` | [Case Study](#case-study-modal_triggerhtml--reusable-trigger-button) |
| Extend a modal with custom title / footer | `modal_static.html` | [Case Study](#case-study-modal_statichtml--block-extendable-skeleton) |
| Render a django-tables2 table to string | `table.html` | [Case Study](#case-study-tablehtml--django-tables2--explicit-modes) |
| Search form that preserves filter params | `search.html` | [Case Study](#case-study-searchhtml--htmx-search-w-filter-preservation) |
| Schema.org breadcrumbs w/ Unpoly | `breadcrumbs.html` | [Case Study](#case-study-breadcrumbshtml--schemaorg--unpoly) |
| Embed a chat widget with custom config | `chat/bubble.html` | [Case Study](#case-study-chatbubblehtml--floating-ai-chat-widget) |
| Block-extend a form to inject hidden fields | `form/form.html` | [Extension Patterns](#extension-patterns-block-overrides) |
| Build a site-level theme via class overrides | `form_field.html` | [Case Study](#case-study-form_fieldhtml--wagtail-block-aware-field-renderer) |
| Build a site menu from `Application` list | `menu/site_menu.html` | [Case Study](#case-study-menuapp_menuhtml--menusite_menuhtml) |

---

**See also**:
- [COMPONENT_TAG.md](./COMPONENT_TAG.md) — full `{% comp %}` API reference (props, slots, vars, attrs)
- [COMPONENT_SYSTEM.md](./COMPONENT_SYSTEM.md) — component hierarchy & lifecycle
- [API_REFERENCE.md](./API_REFERENCE.md) — every Python entry point
- [FORMS_TABLES_INTEGRATION.md](./FORMS_TABLES_INTEGRATION.md) — form & table integration patterns
- [ROUTING_SYSTEM.md](./ROUTING_SYSTEM.md) — `RoutableComponent` / `FragmentComponent` URL routing

---

## Form Sample

A complete, end-to-end example showing how to wire `components/form/form.html` into a Django project: a `ContactForm` → view → URL config → template, with both full-page and HTMX-fragment modes.

### 1. The form

```python
# myapp/forms.py
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, label="Your name")
    email = forms.EmailField(label="Email address")
    subject = forms.ChoiceField(choices=[
        ("general", "General enquiry"),
        ("sales", "Sales"),
        ("support", "Support"),
    ])
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))
    subscribe = forms.BooleanField(required=False, label="Email me product updates")
```

### 2. The view (full-page + HTMX modes)

```python
# myapp/views.py
from django.urls import reverse_lazy
from django.views import View
from django_fusion.web.rendering import TemplateRenderer
from myapp.forms import ContactForm

class ContactView(View):
    template_name = "myapp/contact_page.html"
    form_fragment = "myapp.fragments.contact_form"

    def get(self, request):
        form = ContactForm()
        # HTMX callers get just the form fragment; full-page callers get the page.
        if request.headers.get("HX-Request") == "true":
            return TemplateRenderer.get_default().render_to_response(
                "myapp/fragments/contact_form.html",
                {
                    "form": form,
                    "submit_label": "Send message",
                    "show_cancel": True,
                    "cancel_hx_get": reverse_lazy("home"),
                    "cancel_hx_target": "#contact-form",
                },
                request=request,
            )
        return TemplateRenderer.get_default().render_to_response(
            self.template_name, {"form": form}, request=request,
        )

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            # … handle the form (send email, persist, etc.) …
            form.save() if hasattr(form, "save") else None
            return TemplateRenderer.get_default().render_to_response(
                "myapp/fragments/contact_form.html",
                {
                    "form": ContactForm(),  # reset
                    "submit_label": "Send message",
                    "field_success": "email",
                    "success_message": "Thanks — we’ll be in touch!",
                },
                request=request,
                status=200,
            )
        # Validation failed — re-render the form with errors.
        if request.headers.get("HX-Request") == "true":
            return TemplateRenderer.get_default().render_to_response(
                "myapp/fragments/contact_form.html",
                {"form": form, "submit_label": "Send message"},
                request=request,
                status=400,
            )
        return TemplateRenderer.get_default().render_to_response(
            self.template_name, {"form": form}, request=request,
        )
```

### 3. URL config

```python
# myapp/urls.py
from django.urls import path
from myapp.views import ContactView

urlpatterns = [
    path("contact/", ContactView.as_view(), name="contact"),
]
```

### 4. The page template

```django
{# myapp/templates/myapp/contact_page.html #}
{% extends "base.html" %}
{% load i18n %}

{% block content %}
<div class="container py-5">
    <h1>{% trans "Contact us" %}</h1>
    <p class="text-muted">{% trans "Drop us a line and we’ll get back within 1 business day." %}</p>

    <div id="contact-form">
        {% include "myapp/fragments/contact_form.html" %}
    </div>
</div>
{% endblock %}
```

### 5. The form fragment (HTMX target)

```django
{# myapp/templates/myapp/fragments/contact_form.html #}
{% load i18n %}

{% comp "components/form/form.html"
    form=form
    hx_post=request.path
    hx_target="#contact-form"
    hx_swap="outerHTML"
    hx_indicator="#contact-spinner"
    submit_label=submit_label|default:_("Send message")
    show_cancel=show_cancel|default:False
    cancel_hx_get=cancel_hx_get|default:""
    cancel_hx_target=cancel_hx_target|default:"#contact-form"
    cancel_hx_swap=cancel_hx_swap|default:"outerHTML"
    field_success=field_success|default:""
    success_message=success_message|default:"" / %}
```

The same fragment is rendered on every state (initial GET, validation errors, success). Because the fragment wraps the entire `#contact-form` div, HTMX `outerHTML` swap replaces it cleanly with no flicker.

---

## Component Sample

A complete, drop-in example of a reusable custom component. We build a `<FeatureCard />` component end-to-end — template + Python entry point + view + CSS — and demonstrate both template-side and Python-side usage.

### 1. The template

```django
{# myapp/templates/components/feature_card.html #}
{% load i18n %}
{% prop title %}                        {# required — no default #}
{% prop subtitle="" %}                  {# optional w/ default #}
{% prop icon="bi-stars" %}              {# Bootstrap icon class #}
{% prop accent="primary" %}             {# primary | success | warning | danger | info #}
{% prop href="" %}                      {# if set, wraps the whole card in <a> #}
{% prop cta_label="Learn more" %}

<article class="feature-card feature-card--{{ props.accent }} {{ attrs }}">
  {% if props.icon %}
  <div class="feature-card__icon" aria-hidden="true">
    <i class="bi {{ props.icon }}"></i>
  </div>
  {% endif %}

  <div class="feature-card__body">
    <h3 class="feature-card__title">{{ props.title }}</h3>
    {% if props.subtitle %}
    <p class="feature-card__subtitle text-muted">{{ props.subtitle }}</p>
    {% endif %}
    {% slot %}{{ slot }}{% endslot %}
  </div>

  {% if props.href %}
  <a href="{{ props.href }}" class="feature-card__cta stretched-link">
    {{ props.cta_label }}
    <i class="bi bi-arrow-right ms-1" aria-hidden="true"></i>
  </a>
  {% endif %}
</article>
```

> The template uses the `{% prop %}` / `{% slot %}` / `{{ attrs }}` API described in
> [COMPONENT_TAG.md](./COMPONENT_TAG.md).

### 2. Auto-register on app startup

```python
# myapp/apps.py
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = "myapp"

    def ready(self):
        from django_fusion.comp.registry import register_include_paths
        register_include_paths(["components/feature_card.html"])
```

### 3. Template-side usage

```django
{% comp "components/feature_card.html"
    title="Real-time collaboration"
    subtitle="Edit documents together with sub-second sync."
    icon="bi-people-fill"
    accent="success"
    href="/features/realtime/" / %}
```

With a default slot:

```django
{% comp "components/feature_card.html"
    title="Pro plan"
    subtitle="For teams of 10+"
    accent="warning" %}
  <ul class="feature-card__list">
    <li>Unlimited projects</li>
    <li>SSO + audit log</li>
    <li>Priority support</li>
  </ul>
{% endcomp %}
```

### 4. Python-side usage

```python
# myapp/services/landing.py
from django_fusion.web.rendering import TemplateRenderer

def render_feature_cards(features: list[dict]) -> str:
    renderer = TemplateRenderer.get_default()
    return "\n".join(
        renderer.render_component(
            "feature_card.html",
            {
                "title": f["title"],
                "subtitle": f.get("subtitle", ""),
                "icon": f.get("icon", "bi-stars"),
                "accent": f.get("accent", "primary"),
                "href": f.get("href", ""),
                "cta_label": f.get("cta_label", "Learn more"),
            },
        )
        for f in features
    )
```

### 5. View that composes them

```python
# myapp/views.py
from django.views.generic import TemplateView
from django_fusion.web.rendering import TemplateRenderer
from myapp.services.landing import render_feature_cards

class LandingView(TemplateView):
    template_name = "landing/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["feature_cards_html"] = render_feature_cards([
            {"title": "Real-time collaboration",  "icon": "bi-people-fill",   "accent": "success"},
            {"title": "Built-in version control",  "icon": "bi-clock-history", "accent": "info"},
            {"title": "SOC 2 + GDPR",               "icon": "bi-shield-check", "accent": "warning"},
        ])
        return ctx
```

```django
{# landing/index.html #}
<section class="features-grid py-5">
    <div class="container">
        <div class="row g-4">
            {{ feature_cards_html|safe }}
        </div>
    </div>
</section>
```

### 6. SCSS (theme-side)

```scss
// applications/assets/static/styles/components/_feature_card.scss
.feature-card {
    position: relative;
    padding: 1.5rem;
    border-radius: 0.75rem;
    background: #fff;
    border: 1px solid var(--bs-border-color);
    transition: transform 0.2s, box-shadow 0.2s;
}
.feature-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}
.feature-card__icon {
    width: 48px; height: 48px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; color: #fff;
    margin-bottom: 1rem;
}
.feature-card--primary  .feature-card__icon { background: #6366f1; }
.feature-card--success  .feature-card__icon { background: #10b981; }
.feature-card--warning  .feature-card__icon { background: #f59e0b; }
.feature-card--danger   .feature-card__icon { background: #ef4444; }
.feature-card--info     .feature-card__icon { background: #3b82f6; }
.feature-card__title    { font-size: 1.125rem; font-weight: 600; margin-bottom: 0.25rem; }
.feature-card__subtitle { font-size: 0.875rem; margin-bottom: 0.75rem; }
.feature-card__cta      { display: inline-block; margin-top: 0.5rem; font-weight: 500; text-decoration: none; }
```

The component is now fully reusable: from any template (`{% comp "components/feature_card.html" %}`), from any Python call (`TemplateRenderer.render_component("feature_card.html", {...})`), and styled via the SCSS class family. The `accent` prop maps directly to BEM modifiers, so introducing a new accent is a one-line SCSS addition.

---

## Styling from Python Recipe

A full worked example showing how to add a new visual variant to an existing component without forking the template, by passing CSS classes via Python kwargs. We'll add a new `btn--gradient-rainbow` variant to `components/button.html`.

### Step 1 — Add the SCSS rule (theme-side, no Python touched)

```scss
// applications/assets/static/styles/components/_button.scss
.btn--gradient-rainbow {
    background: linear-gradient(
        90deg,
        #ff6b6b 0%,
        #feca57 25%,
        #48dbfb 50%,
        #ff9ff3 75%,
        #54a0ff 100%
    );
    color: #fff;
    border: 0;
    background-size: 200% 100%;
    transition: background-position 0.4s ease;
}
.btn--gradient-rainbow:hover {
    background-position: 100% 0;
    color: #fff;
}
```

That's the only theme-side change. No Python or template touched.

### Step 2 — Use the new variant from a template

```django
{% comp "components/button.html"
    label="Try the new dashboard"
    variant="gradient-rainbow"
    icon="bi-stars"
    href="/dashboard/" / %}
```

The template's `variant` prop is a free-form string — no enum in Python — so any new variant works as soon as the SCSS exists.

### Step 3 — Use the new variant from Python

```python
# myapp/services/cta.py
from django_fusion.web.rendering import TemplateRenderer

def render_dashboard_cta(request) -> str:
    return TemplateRenderer.get_default().render_component(
        "button.html",
        {
            "label": "Try the new dashboard",
            "variant": "gradient-rainbow",   # <-- new variant
            "icon": "bi-stars",
            "href": "/dashboard/",
            # Composition — multiple Python args become one styled element:
            "css_class": "mt-3 shadow-lg btn--xl",    # size + shadow + spacing
            "extra_attrs": 'data-analytics="cta"',    # behaviour / tracking
        },
    )
```

### Step 4 — Inside a Django view (one-liner)

```python
class LandingView(TemplateView):
    template_name = "landing/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["dashboard_cta"] = render_dashboard_cta(self.request)
        return ctx
```

```django
{# landing/index.html #}
{{ dashboard_cta|safe }}
```

### Step 5 — Inside a service / email / async job

```python
# myapp/emails.py
from django_fusion.web.rendering import TemplateRenderer

def build_welcome_email(user) -> dict:
    renderer = TemplateRenderer.get_default()
    cta_html = renderer.render_component(
        "button.html",
        {
            "label": "Open your dashboard",
            "variant": "gradient-rainbow",
            "href": f"https://app.example.com/dashboard/?u={user.id}",
            "extra_attrs": 'style="display:inline-block; padding:12px 24px; border-radius:8px; text-decoration:none;"',
        },
    )
    return renderer.render_email(
        "emails/welcome.html",
        {"user": user, "cta_html": cta_html},
        subject=f"Welcome, {user.first_name}!",
    )
```

### What just happened

| Surface | What changed | Who controls it |
|---------|--------------|-----------------|
| SCSS | Added `.btn--gradient-rainbow` rule | Theme team |
| Python | Passed `variant="gradient-rainbow"` | App / service code |
| Template | Unchanged — `variant` is a free-form string | (no edit) |

Three roles touched three different layers, and the component contract (`variant` is a string) didn't change. That's the "art of customizations" — the **contract** stays small, the **surface** stays decoupled, and the **styling** scales through SCSS rather than through Python enums.

### Anti-patterns to avoid

1. **Hardcoding the SCSS class in Python** — `css_class="btn--gradient-rainbow"` works, but it bypasses the `variant` contract and duplicates styling intent. Use `variant=` so the SCSS continues to drive presentation.
2. **Forking the template to add a new variant** — never copy `button.html` to add a single class. The `variant` string is the extension point.
3. **Adding a Python enum to gate variants** — variants are *theme*, not *app*. The Python side should remain stringly-typed so the theme can ship new variants without app deploys.
4. **Inlining `style="..."` for layout** — pass `css_class="mt-3 ..."` instead. Inline styles override theme cascade and break responsiveness.

