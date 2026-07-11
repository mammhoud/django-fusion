# Troubleshooting — DF-013

> Source of truth: edge-cases mined from `tests/test_conftest_debug_is_quiet.py`,
> `tests/test_django_settings_configure_contract.py`,
> `tests/test_component_tag.py`, `tests/test_register_include_path_render_equivalence.py`,
> `tests/test_form_components.py`,
> `tests/test_routable_components.py`.

## Component template not found

**Symptom:** `TemplateDoesNotExist: components/foo.html`.

**Cause:** You used `{% comp "foo.html" %}` but the include path was
not registered. Component names without a leading `components/` are
still searched under `/components/`, so `foo.html` resolves to
`components/foo.html`.

**Fix:**

1. Place the file under a registered template directory and ensure
   `register_include_paths([…])` has been called in `AppConfig.ready()`.
2. Or use the literal path: `{% comp "myapp/foo.html" / %}`.

## `fragment_name` rejected as a synonym

**Symptom:** `TemplateSyntaxError: aliasing 'fragment_name' to
'fragment' is forbidden`.

**Cause:** You used `fragment="x"` or `name="x"` on `{% comp %}`.

**Fix:** Replace with the reserved name `fragment_name="x"`. The
aliases are enforced by
`tests/test_routable_components.py:TestFragmentNameConvention`.

## `DJANGO_DEBUG_CONFTEST` does nothing despite being set

**Symptom:** No diagnostic output even after exporting the env var.

**Cause:** The guard is exact-match `== "1"`. Empty strings, numeric
strings (`"true"`), or accidental whitespace don't trigger.

**Fix:** Use `export DJANGO_DEBUG_CONFTEST=1` (not `=true`, not `=yes`,
not `= `).

## `settings.configure()` triggered twice

**Symptom:** `RuntimeError: settings already configured`.

**Cause:** `pytest-django` configured settings via
`DJANGO_SETTINGS_MODULE=tests.settings` *and* the `conftest.py` called
`settings.configure()` itself.

**Fix:** Don't set `DJANGO_SETTINGS_MODULE` for these tests. The
conftest's `settings.configure(...)` is the supported path — see the
comment in `pyproject.toml` under `[tool.pytest.ini_options]` and
`tests/test_django_settings_configure_contract.py`.

## `ComponentMappingCache` falls back unexpectedly

**Symptom:** All requests feel `O(n)` for component lookups; Redis
hits `0`.

**Cause:** Redis backend isn't installed or unreachable, and the
fallback cache is doing all the work — see `src/django_fusion/comp/cache.py`.

**Fix:**

1. Verify `pip install redis` is in your `requirements.txt`.
2. Check `CACHES["default"]["BACKEND"]` resolves to
   `django.core.cache.backends.redis.RedisCache`.
3. Ensure your settings module is the one actually loaded — set
   `DJANGO_DEBUG_CONFTEST=1` and conftest will print the active cache
   configuration.

## `register_include_paths` order matters

**Symptom:** A site-specific template override is silently not picked
up.

**Cause:** `register_default_partials()` registers paths in the
order it finds them; later calls append. If your site-level
`AppConfig.ready()` runs before django-fusion's, your entries are
overwritten.

**Fix:** Put `register_include_paths` in a `CoreExtAppConfig.ready()`
hook or the lowest-priority `AppConfig`, so it runs last. The
COMPONENT_CASE_STUDIES *theming via component directories* recipe
covers this.

## `PaginatedListView` fragment_name falls back incorrectly

**Symptom:** You set `model = Article` and `fragment_name = None`,
expecting `components.<app>.<model>_list`, but you get
`components/items/list`.

**Cause:** The model-derived path requires **explicit** `None`. The
default `fragment_name = "components.paginated_list"` is set on the
base class.

**Fix:** Set `fragment_name = None` *explicitly* on the subclass
(yes, this is the only way to opt in to derivation).

> Reference test: `tests/test_routable_components.py:TestLegacyPaginatorsFragmentName`.

## `{% %}` parse error: "Unknown tag: comp"

**Symptom:** `TemplateSyntaxError: Invalid block tag on line N: 'comp'`.

**Cause:** `django_fusion.comp.templatetags.components` was not added
to `TEMPLATES[0]["OPTIONS"]["builtins"]`.

**Fix:** Either add it to `builtins` (recommended), or
`{% load components %}` at the top of every template.

## `extra_attrs` is rendered as plain text

**Symptom:** You passed `extra_attrs='hx-get="…" hx-target="…"'`, and
the literal string appears in the output.

**Cause:** The component template forgot to mark `extra_attrs` as
`{% load components %}` and use `{{ attrs }}`.

**Fix:** Add `{{ attrs }}` to the relevant element in the component
template, and verify the template has
`{% load components %}` once at the top.

## All pages suddenly 500 after a Wagtail upgrade

**Symptom:** `wagtail.contrib.forms` import errors during deploy.

**Cause:** `django_fusion.wagtail` requires Wagtail 5+; older `wagtail`
versions may break `BaseSnippetViewSet` (see
`src/django_fusion/wagtail/viewsets.py`).

**Fix:** Pin `wagtail>=5` in `pyproject.toml` and rebuild the lock file.

## Health endpoint returns 503 in production

**Symptom:** Load balancer marks the pod unhealthy; logs show 503
on `/health/db/`.

**Cause:** Either DB connection pool exhaustion, or
`ALLOWED_HOSTS` not matching the probe's `Host` header.

**Fix:** Configure your probe's `Host` header to match
`ALLOWED_HOSTS`, and verify Postgres connection limits.

## Cross-references

- [DF-014 FAQ](./14-faq.md) — quick fixes for the most common setup questions
- [DF-007 Configuration](./07-configuration.md) — settings reference
- [DF-009 Health](./09-health.md) — JSON shape and error meanings
