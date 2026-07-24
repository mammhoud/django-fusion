# Forms & Tables — DF-006

> Source of truth: `src/django_fusion/comp/routes/forms_tables.py`,
> `QUICKSTART.md`, `tests/test_form_components.py`, `tests/test_form_components_stage2.py`.
>
> See also: the Python entry points in
> `src/django_fusion/comp/routes/components.py` (RoutableComponent handling)
> and `src/django_fusion/comp/routes/fragments.py` (HTMX-aware rendering).

## Status

`FormMixin`, `TableMixin`, and `FormTableMixin` are supported and shipped
in this release. The simpler alternative for new code is to use Django's
standard `forms.Form` / `ModelForm` inside a `RoutableComponent.get_context_data`
and render through `{% comp "components/form/form.html" %}` from the
form / table template library (see COMPONENT_CASE_STUDIES' `form/form.html`
entry, in `docs/COMPONENT_CASE_STUDIES.md`). Both paths are valid; the
mixins just provide a shortcut for the cascade and helpers below.

## Quick start

If you must use the legacy mixins (existing site):
see [`QUICKSTART.md`](../QUICKSTART.md). This doc is a **deep reference**,
not a fast path — use it when you're customizing template-resolution order,
adding a new attribute, or debugging a missing context variable.

## `FormMixin`

```python
from django_fusion.routes.forms_tables import FormMixin

class CreateUserComponent(RoutableComponent, FormMixin):
    form_name = "user"
    form_class = UserForm
    template_name = "users/create.html"
```

### Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `form_name` | `str` | Lookup key for the form template (`components/form/<name>.html` etc.) |
| `form_class` | `type[forms.Form]` | Form class to instantiate (`None` → `get_form_class()` resolves) |
| `form_kwargs` | `dict` | Static kwargs forwarded to `Form(*form_kwargs, **dynamic)` |

### Methods

| Method | Returns | Default |
|--------|---------|---------|
| `get_form_name()` | `str` | `self.form_name` |
| `get_form_template_names()` | `list[str]` | Lookup cascade (site → assets → generic → library) |
| `get_form_class()` | `type[Form]` | `self.form_class` |
| `get_form_kwargs()` | `dict` | `{"data": request.POST/None, "files": request.FILES/None, **form_kwargs}` |
| `get_form()` | `Form` | Instantiated form |
| `get_form_context_data()` | `dict` | `{"form": self.get_form()}` plus extra overrides |

## `TableMixin`

```python
from django_fusion.routes.forms_tables import TableMixin

class UserListComponent(RoutableComponent, TableMixin):
    model = User
    table_name = "users"
    template_name = "users/list.html"

    def get_queryset(self):
        return User.objects.active().order_by("username")
```

### Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `table_name` | `str` | Lookup key for the table template |
| `table_headers` | `list[dict]` | Column definitions (`{"label, key, sortable?, sort_attr?, css_class?}"`) |
| `table_data` | `list` | Pre-computed rows |
| `default_headers_from_model` | `bool` | When `True`, fill `table_headers` from `model._meta.fields` |

### Methods

| Method | Returns | Default |
|--------|---------|---------|
| `get_table_name()` | `str` | `self.table_name` |
| `get_table_template_names()` | `list[str]` | Site → assets → generic → library cascade |
| `get_table_headers()` | `list[dict]` | `self.table_headers` or auto-from-model |
| `get_table_data()` | `list` | `list(self.get_queryset())` or `self.table_data` |
| `get_table_context_data()` | `dict` | Merged dict for the template |

## `FormTableMixin`

Combines `FormMixin` + `TableMixin` and adds the merged context method.

| Method | Returns | Notes |
|--------|---------|-------|
| `get_form_table_context_data()` | `dict` | Union of `get_form_context_data()` and `get_table_context_data()`. Always call this in `get_context_data(**kwargs)` |

## Template resolution cascade (for `form_name = "user"`)

```text
1. <site>/templates/components/form/user.html       ← site override
2. assets/templates/components/form/user.html        ← shared assets
3. django_fusion/comp/templates/.../user-form.html   ← generic
4. django_fusion/comp/routes/templates/routable_components/forms/form.html   ← library
```

`get_*_template_names()` returns this list verbatim; the first matching
path is used.

## Cross-cutting methods

`FormTableMixin.get_form_table_context_data()` de-duplicates keys
(`form` and `table*`) when merging, preferring keys from
`get_table_context_data()` on conflict.

## Anti-patterns

1. **Stack FormMixin on top of CreateModelView** — pick one. Both supply
   `form_class`; the latter takes precedence in practice (last MRO wins)
   and the duplicate form machinery breaks silently.
2. **Use the mixins for non-routed components.** They assume
   `template_name` + `request` are wired up. For a quick render-from-Python
   use `TemplateRenderer.render_component("form/form.html", {...})`
   (see COMPONENT_CASE_STUDIES.md) instead.
3. **Override `get_form_class` *and* `form_class`.** Pick one path;
   both work but the call site is harder to grep.

## Tests guarding this surface

- `tests/test_form_components.py` — basic FormMixin + TableMixin contract
- `tests/test_form_components_stage2.py` — template cascade behaviour
- `tests/test_viewsets.py` — interaction with ModelViewset

If a behaviour breaks, one of these tests will fail.
