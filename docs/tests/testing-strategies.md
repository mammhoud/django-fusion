# 🧪 Testing Strategies

> Detailed testing strategies — unit, integration, end-to-end, and CI — for all Structa Cloud projects.

---

## Strategy Matrix

| Test Type | Django Sites | POS (Rust) | POS (Vue) | Libs |
|-----------|:---:|:---:|:---:|:---:|
| Unit | ✅ pytest-django | ✅ cargo test | ✅ vitest | ✅ pytest |
| Integration | ✅ pytest-django | ✅ cargo test (db) | ❌ | ✅ pytest |
| Component | ✅ comp equivalence | ❌ | ✅ vitest | ✅ analyzer |
| E2E | ❌ | ❌ | ❌ | ❌ |
| CI | ✅ GitHub Actions | ✅ release.yml | ✅ release.yml | ✅ pytest-core |

---

## Django Testing

### Test Setup Pattern

```python
# tests/settings.py — Workspace-level test settings
import importlib.util
from configs.base.settings import *

# Conditionally include optional apps
OPTIONAL_APPS = [
    "allauth",
    "allauth.account",
    "wagtail",
    "django_fusion",
]

for app in OPTIONAL_APPS:
    spec = importlib.util.find_spec(app)
    if spec is None:
        INSTALLED_APPS.remove(app)
```

### Conftest Pattern

```python
# tests/conftest.py
import pytest
from django.test import RequestFactory

@pytest.fixture
def rf():
    """Django RequestFactory for view testing."""
    return RequestFactory()

@pytest.fixture
def admin_user(db):
    """Create a test admin user."""
    from django.contrib.auth import get_user_model
    return get_user_model().objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="testpass123",
    )

@pytest.fixture
def authenticated_client(client, admin_user):
    """Authenticated Django test client."""
    client.force_login(admin_user)
    return client
```

### View Testing

```python
# Test a Wagtail page serve
def test_course_page_serve(rf):
    from lms.plugins.courses.models import CoursePage
    page = CoursePage.objects.create(
        title="Test Course",
        slug="test-course",
    )
    request = rf.get(f"/courses/{page.slug}/")
    response = page.serve(request)
    assert response.status_code == 200
    assert "Test Course" in response.rendered_content
```

### HTMX Fragment Testing

```python
def test_login_fragment(authenticated_client):
    """HTMX login modal returns a fragment, not full page."""
    response = authenticated_client.get(
        "/account/login/",
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code == 200
    assert "fragment--login" in response.content.decode()
    assert "<html" not in response.content.decode()  # Not a full page
```

### Template Equivalence Testing

```python
# libs/django-fusion/tests/test_register_include_path_render_equivalence.py
def test_include_vs_comp_rendering():
    """{% include %} and {% comp %} produce identical output."""
    template_include = Template('{% include "components/card.html" %}')
    template_comp = Template('{% comp "components.card" /%}')

    context = Context({"title": "Hello", "body": "World"})
    assert template_include.render(context) == template_comp.render(context)
```

---

## Rust Testing (POS)

### Unit Tests (Inline)

```rust
// db/operations/products.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_product() {
        let conn = &mut open_test_conn();
        let product = NewProduct {
            name: "Test Product".into(),
            sku: Some("TST-001".into()),
            price: 9.99,
            category_id: 1,
        };
        let result = create_product(conn, &product);
        assert!(result.is_ok());
        let saved = result.unwrap();
        assert_eq!(saved.name, "Test Product");
        assert_eq!(saved.price, 9.99);
    }

    #[test]
    fn test_duplicate_sku_rejected() {
        let conn = &mut open_test_conn();
        let product = NewProduct {
            name: "Dupe".into(),
            sku: Some("DUP-001".into()),
            price: 5.00,
            category_id: 1,
        };
        create_product(conn, &product).unwrap();
        let result = create_product(conn, &product);
        assert!(result.is_err());
    }
}

fn open_test_conn() -> SqliteConnection {
    let mut conn = SqliteConnection::establish(":memory:").unwrap();
    run_migrations(&mut conn).unwrap();
    conn
}
```

### Database Integration Tests

```rust
#[test]
fn test_order_workflow() {
    let conn = &mut open_test_conn();
    seed_test_data(conn);

    // Create an order
    let order = create_order(conn, NewOrder {
        customer_id: Some(1),
        register_id: 1,
        user_id: 1,
    }).unwrap();

    // Add items
    add_item(conn, NewOrderItem {
        order_id: order.id,
        product_id: 1,
        quantity: 2.0,
        unit_price: 9.99,
    }).unwrap();

    // Complete payment
    let payment = process_payment(conn, NewPayment {
        order_id: order.id,
        method_id: 1,
        amount: 19.98,
    }).unwrap();

    assert_eq!(payment.status, "completed");

    // Verify inventory reduced
    let inventory = get_inventory(conn, 1, 1).unwrap();
    assert_eq!(inventory.quantity, 98.0); // 100 - 2
}
```

---

## Vue Testing (POS Client)

### Setup

```typescript
// pos-client/src/test/setup.ts
import { vi } from 'vitest';

// Mock Tauri invoke
vi.mock('@tauri-apps/api', () => ({
  invoke: vi.fn(async (cmd: string, args?: any) => {
    const mockData: Record<string, any> = {
      get_products: [{ id: 1, name: 'Water', price: 1.0 }],
      create_order: { id: 1, order_number: 'ORD-001' },
    };
    return mockData[cmd] ?? null;
  }),
}));

// Polyfill window.matchMedia for component tests
Object.defineProperty(window, 'matchMedia', {
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  })),
});
```

### Component Test

```typescript
// pos-client/src/components/__tests__/ProductCard.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import ProductCard from '../ProductCard.vue';

describe('ProductCard', () => {
  it('renders product name and price', () => {
    const wrapper = mount(ProductCard, {
      props: {
        product: { id: 1, name: 'Water', price: 1.00 },
      },
    });
    expect(wrapper.text()).toContain('Water');
    expect(wrapper.text()).toContain('1.00');
  });

  it('emits add-to-cart on button click', async () => {
    const wrapper = mount(ProductCard, {
      props: {
        product: { id: 1, name: 'Water', price: 1.00 },
      },
    });
    await wrapper.find('[data-test="add-to-cart"]').trigger('click');
    expect(wrapper.emitted('add-to-cart')).toBeTruthy();
    expect(wrapper.emitted('add-to-cart')![0]).toEqual([{ id: 1, quantity: 1 }]);
  });

  it('shows discount badge when applicable', () => {
    const wrapper = mount(ProductCard, {
      props: {
        product: { id: 1, name: 'Water', price: 1.00, discount: 0.20 },
      },
    });
    expect(wrapper.find('.badge--discount').exists()).toBe(true);
    expect(wrapper.find('.badge--discount').text()).toContain('20%');
  });
});
```

---

## CI Integration

### pytest-core Workflow

```yaml
# .github/workflows/pytest-core.yml
name: pytest-core
on:
  pull_request:
    paths: ['tests/**', 'projects/**', 'libs/**']
jobs:
  pytest:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    defaults:
      run:
        working-directory: projects
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install uv
      - run: uv sync
      - run: uv run pytest
```

### POS Release Testing

```yaml
# projects/pos/pos-full/.github/workflows/release.yml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - run: cargo test --locked
      - run: cargo clippy -- -D warnings
```

---

## Running Tests

```bash
# All workspace tests
uv run pytest

# Specific test file
uv run pytest tests/test_template_equivalence.py -v

# Django site tests
cd projects && make test WEBSITE=lms

# Rust tests
cd projects/pos/pos-full && cargo test

# Vue component tests
cd projects/pos/pos-client && npx vitest run

# With coverage (Python)
uv run pytest --cov=tests --cov=libs/django-fusion

# With coverage (Rust)
cargo tarpaulin --out Html
```

---

## Related

| Topic | Path |
|-------|------|
| Testing overview | [`README.md`](README.md) |
| django-fusion tests | [`../libs/django-fusion.md`](../libs/django-fusion.md) |
| CI/CD pipeline | [`../publish/ci-cd.md`](../publish/ci-cd.md) |
| Best practices | [`../guides/08-best-practices.md`](../guides/08-best-practices.md) |
