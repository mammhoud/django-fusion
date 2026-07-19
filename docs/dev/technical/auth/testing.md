# Auth System Testing

## Test Files

| File | Type | Purpose |
|------|------|---------|
| `websites/tests/unit/test_auth_fragments.py` | Property-based | Template structure, HTMX behavior |
| `websites/tests/unit/test_auth_notifications.py` | Unit | Adapter, logout message, deleted templates |
| `websites/tests/unit/test_app_structure.py` | Unit | App location, branding, URL namespaces |
| `websites/tests/integration/test_auth_flows.py` | Integration | End-to-end auth flows against containers |

## Running Tests

```bash
# Unit tests (no running server needed)
pytest websites/tests/unit/test_auth_fragments.py -v
pytest websites/tests/unit/test_auth_notifications.py -v
pytest websites/tests/unit/test_app_structure.py -v

# Integration tests (requires running containers)
CTC_BASE_URL=http://localhost:5070 STRUCTA_BASE_URL=http://localhost:5080 \
    pytest websites/tests/integration/test_auth_flows.py -v

# All auth tests
pytest websites/tests/unit/test_auth_fragments.py \
       websites/tests/unit/test_auth_notifications.py \
       websites/tests/unit/test_app_structure.py \
       websites/tests/integration/test_auth_flows.py -v
```

## Property-Based Tests

Uses [Hypothesis](https://hypothesis.readthedocs.io/) to verify universal properties across all auth templates.

### Properties

| # | Property | Validates |
|---|----------|-----------|
| 1 | All auth/ templates are pure fragments | No `{% extends %}`, outermost = `fragment--form` |
| 2 | No `pipelines:` references remain | URL namespace migration complete |
| 3 | All forms have `strategy` and `supports_sse` inputs | HTMX context fields present |
| 4 | Social buttons use `<a>` not `hx-post` | OAuth redirect compatibility |
| 5 | HTMX requests return bare fragments | `HX-Request: true` → no skeleton |
| 6 | Non-HTMX requests return skeleton | Full-page → `auth-container` + `fragment--form` |
| 7 | Strategy field round-trip | `strategy` value preserved through form submission |
| 8 | Invalid HTMX submissions return 2xx fragments | No redirects on HTMX form errors |
| 9 | Configured providers render buttons | `SOCIALACCOUNT_PROVIDERS` → buttons visible |

### Configuration

```python
from hypothesis import settings
settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")
```

### Example

```python
from hypothesis import given, settings as h_settings, strategies as st

@given(template_path=st.sampled_from(AUTH_TEMPLATE_PATHS))
@h_settings(max_examples=100)
def test_no_pipelines_references(template_path):
    content = Path(template_path).read_text(encoding="utf-8")
    assert "pipelines:" not in content
```

## Integration Tests

End-to-end tests using `requests` against running containers. Tests skip automatically if the site is not reachable.

```python
@pytest.mark.parametrize("site", SITE_CONFIGS, ids=lambda s: s["name"])
def test_htmx_fragment_response(site):
    resp = requests.get(
        f"{site['base_url']}/auth/login/",
        headers={"HX-Request": "true"},
    )
    assert "fragment--form" in resp.text
    assert "auth-container" not in resp.text
```
