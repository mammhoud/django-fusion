# Test Fixtures

Django JSON fixtures for the blog test suite.

## Files

| File | Contents |
|------|----------|
| `blog_users.json` | Staff author (pk=1), regular user (pk=2), commenter (pk=3) |
| `blog_categories.json` | Technology, Research, News, Tutorial (pk=1–4) |
| `blog_tags.json` | Python, Django, JavaScript, API, Unused (pk=1–5) |
| `blog_posts.json` | 5 published + 1 draft post (pk=1–6), depends on users/categories/tags |
| `blog_comments.json` | 3 comments on posts (pk=1–3), depends on posts/users |
| `blog_full.json` | Self-contained set (pk=10+) — users, categories, tags, posts |

## Usage in tests

```python
# Load a single fixture
@pytest.fixture
def blog_data(db, django_db_setup, django_test_environment):
    from django.test.utils import setup_test_environment
    call_command("loaddata", "tests/assets/fixtures/blog_full.json")

# Or use pytest-django's fixtures marker
@pytest.mark.django_db
class TestSomething:
    fixtures = ["tests/assets/fixtures/blog_full.json"]
```

## Notes

- Fixtures use high PKs (10+) in `blog_full.json` to avoid conflicts with
  programmatically created objects in the same test session.
- `blog_posts.json` depends on `blog_users.json`, `blog_categories.json`,
  and `blog_tags.json` — load them together.
- Passwords in fixtures are unusable hashes; use `client.force_login()` in tests.
