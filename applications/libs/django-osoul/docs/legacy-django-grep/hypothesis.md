# Hypothesis — Property-Based Testing

[Hypothesis](https://hypothesis.readthedocs.io/) generates test cases automatically to find edge cases.

## Installation

```bash
pip install hypothesis
```

## Basic Pattern

```python
from hypothesis import given, settings, strategies as st

@given(value=st.sampled_from(["htmx", "document"]))
@settings(max_examples=100)
def test_strategy_round_trip(value):
    assert value in ("htmx", "document")
```

## Auth Template Tests

The auth system uses Hypothesis to verify properties across all templates:

```python
from pathlib import Path
from hypothesis import given, settings as h_settings, strategies as st

AUTH_TEMPLATE_PATHS = [str(p) for p in Path("websites").rglob("auth/*.html")]

@given(template_path=st.sampled_from(AUTH_TEMPLATE_PATHS))
@h_settings(max_examples=100)
def test_no_pipelines_references(template_path):
    content = Path(template_path).read_text(encoding="utf-8")
    assert "pipelines:" not in content
```

## CI Configuration

```python
# conftest.py
from hypothesis import settings
settings.register_profile("ci", max_examples=100)
settings.load_profile("ci")
```

## Key Strategies

| Strategy | Use case |
|----------|----------|
| `st.sampled_from(list)` | Pick from known values (template paths, strategy values) |
| `st.text()` | Generate arbitrary strings |
| `st.emails()` | Generate valid email addresses |
| `st.integers()` | Generate integers |

(Full auth-template test patterns are described in the project's test suite.)
