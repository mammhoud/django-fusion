# 📐 Best Practices — Code Conventions

> Language-specific conventions and documentation standards for the Structa Cloud monorepo.

---

## Python (Django)

```python
# PEP 8, Black 88-char line length
from django_fusion.comp.routes import Viewset  # Canonical import paths

class MyViewset(ModelViewset):  # Class-based views
    """One-line docstring."""
    model = MyModel
```

- Use type hints for new functions
- No `try/except` import wrapping
- Business logic in services, not views
- `fragment_name` for HTMX fragment identifiers

## Rust (POS Backend)

```rust
/// One-line summary.
pub fn get_products(db_path: &str) -> Result<Vec<Product>, String> {
    let mut conn = establish_connection(db_path);
    // Diesel ORM queries
}
```

- ALL Tauri commands return `Result<T, String>`
- Operation modules follow: CRUD + soft delete pattern

## TypeScript (POS Frontend)

```typescript
/** Brief description. */
function MyComponent({ data }: Props): JSX.Element {
  const { t } = useTranslation();
  return <div>{t('common.save')}</div>;
}
```

- React 19 + TypeScript 5.8
- Functional components with hooks
- JSDoc for exported functions

## Documentation Standards

| Element | Convention |
|---------|-----------|
| Headings | `# H1` page title, `## H2` sections, `### H3` sub-sections |
| Code | Backticks for paths/commands, fenced blocks with language |
| Links | Relative paths from source file |
| Emoji | Consistent: 🏠 nav, 🟢 customizable, ⚠️ warning, 💡 tip |

## Customization Tags

| Tag | Meaning |
|-----|---------|
| 🟢 `customizable` | Safe to modify, extend, override |
| 🔴 `not-customizable` | Core framework — modify at own risk |
| 🟡 `delegate` | Extend through hooks/delegation |
| 🔵 `template` | Template-level only |
| ⚪ `config` | Configure via env vars/settings |

## Related

| Resource | Path |
|----------|------|
| AI agents | [`../ai/`](../ai/) |
| Customization | [`../customization/`](../customization/) |
| Guides | [`../guides/`](../guides/) |
