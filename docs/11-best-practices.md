# Best Practices — DF-011

> Source of truth: distilled from `docs/COMPONENT_CASE_STUDIES.md`
> (22 components, 9 cross-cutting recipes) and the patterns
> `tests/test_form_components.py`, `tests/test_viewsets.py`,
> `tests/test_routable_components.py` rely on.

## 1. Component naming

- **Kebab or snake in template paths** — `components/cta-banner.html`,
  not `components/CTABanner.html`. Lowercase keeps template resolution
  cross-platform.
- **Dotted `fragment_name`** — `components.blog.post_preview`, not
  `blog_post_preview`. The dot notation matches CSS BEM scoping and
  keeps registry lookups O(1).
- **Reserved kwarg `fragment_name`** — never alias it as
  `fragment`, `name`, `slug`. `RoutableComponent` rejects the aliases
  with `TemplateSyntaxError` (enforced by
  `tests/test_routable_components.py:TestFragmentNameConvention`).

## 2. When to use `FragmentComponent` vs `RoutableComponent`

Use `RoutableComponent` when:

- The URL is meaningful when loaded directly (e.g. `/blog/<slug>/`).
- The full-page template needs a different layout from the fragment.
- You want a permanent, linkable URL.

Use `FragmentComponent` when:

- The URL is only meaningful via `hx-get` swaps.
- There's no value in a non-JS fallback.

For **both**, lean on `FragmentComponent` with a `template_name` that
is the full page — `FragmentComponent` automatically strips layout
when `HX-Request: true`.

## 3. Caching guidance

- **Component-mapping cache** (`django_fusion.comp.cache`) is keyed by
  dotted `fragment_name`. Don't add per-instance cache; you'll only
  slow the registry down.
- **Queryset caching** — use `CachedManager` from
  `django_fusion.core.managers` for querysets heavier than ~5 joins or
  that fire on every page render.
- **HTMX response caching** — keep responses served above ~200 ms out
  of the inner cache and rely on a CDN or reverse proxy.

## 4. Security & the privacy middleware

`PrivacyMiddleware` (`django_fusion.core.middlewares`) is a handling
gateway, not a substitute for consent UX. Pair it with:

- `cookies/cookie-consent.html` template (renders once, cloned into a
  dialog by `cookie-consent.js`)
- `django_fusion.contrib.privacy` consent helpers
- A periodic consent audit through your DPO / counsel

> Remark: never store PII in `{% var %}`. `vars` are scoped to a single
> render — they look like a tempting cache, but they go through the
> template-level scope and are lost on next render.

## 5. Form & table components

- **Use `form/form.html`** for unified rendering — it has 8 block
  hooks for surgical override (`form_actions`,
  `form_cancel_button`, `after_form`, …). Don't reinvent.
- **Add success hints with `field_success` + `success_message`** —
  this gives a non-flickering acknowledgement on HTMX success.
- **Preserve filters in search** — always render
  `extra_filters={...}` hidden inputs into `search.html` so a search
  doesn't reset pages and filters.

## 6. Testing

- **Each component gets at minimum:**
  - a happy-path render test
  - an attrs-passthrough test (extra kwargs land on root element)
  - a props-default test (no kwargs yield sensible defaults)
- **`DJANGO_DEBUG_CONFTEST=1`** when debugging "why is my template not
  being found?" — it prints the active TEMPLATES config.
- **Run `pytest` with `tests/conftest.py` settings.ensure_configured()**
  — the conftest calls `settings.configure()` with minimum Django
  setup if there's no real settings module.

## 7. Anti-patterns

| Don't | Why | Do |
|-------|-----|-----|
| Edit `src/django_fusion/comp/templates/components/*` directly | The package is version-pinned; upgrades overwrite | Override at site via `<site>/templates/components/<name>.html` |
| Hardcode SCSS classes in Python (`css_class="btn--gradient"`) | Bypasses the `variant` prop contract | Pass `variant="gradient"`; the theme owns the SCSS |
| Hardcode Django version checks in code (`if django.VERSION < (5, 0)`) | Branch bloat | Add a `DJANGO_FUSION_DJANGO_MIN_VERSION` setting in `pyproject.toml` |
| Use `comp/forms` mixins for new components | Marked legacy; slated for deprecation in v0.3.0 | Use Django `forms.Form` directly with `RoutableComponent` |
| Mix `ModelViewset` + `CreateModelView` for the same model | Both define form machinery; MRO conflicts break silently | Pick one: `ModelViewset` is the high-level path |

## 8. Linting & style

- Match PEP 8 / `black`-formatted 88-char lines.
- Use `from __future__ import annotations` in modules with import-time
  generics (notably `projects/services.py` and `projects/models.py`).
- Never wrap imports in `try / except`. Lazy imports go in
  `__getattr__` on the module, or in `__init__.py` re-exports.

## 9. Django version compatibility

`pyproject.toml` requires `django >= 4.2` minimum. New code paths
should target Django 5.2 LTS features; 4.2 LTS remains supported.

## 10. Where to look when stuck

| Symptom | Doc |
|---------|-----|
| Component not rendering | DF-013 Troubleshooting |
| URL collision | DF-013 Troubleshooting |
| Settings not picked up | DF-007 Configuration + DF-013 |
| HTMX not working | DF-009 Health + DF-014 FAQ |
