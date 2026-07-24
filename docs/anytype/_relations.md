# AnyType Relations — Object Linking Guide

> **Import Instruction:** Use these Relations in AnyType to link related documentation objects.
> Apply the "Object" property type with the specified relation name.

---

## Relation Definitions

| Name | Type | Source → Target | Description |
|------|------|-----------------|-------------|
| `Related Architecture` | Object → Architecture | Any → Architecture | Links features/guides to architectural docs |
| `Related Feature` | Object → Feature | Any → Feature | Links architectures/guides to feature docs |
| `Related Guide` | Object → Guide | Any → Guide | Links features/architectures to guides |
| `Related Reference` | Object → Reference | Any → Reference | Links features/guides to API/command refs |
| `Depends On` | Object → Task/Feature | Task → Task/Feature | Dependency chain for implementation |
| `Implements` | Object → Architecture | Guide → Architecture | A guide that implements an architecture |
| `See Also` | Object → Any | Any → Any | General cross-reference |

---

## Graph View Connections

```
                    Architecture
                   /     |      \
                  ▼      ▼       ▼
             Features  Guides  References
                  \      |      /
                   ▼     ▼     ▼
                   Relations Hub
                   (Backlinks)
```

---

## Usage in Files

Each markdown file ends with a `Related Docs` section using → arrows:

```markdown
## Related Docs
- → `architecture/editions-overview.md` — Edition comparison
- → `features/pos-mini.md` — pos-mini features
- → `guides/setup.md` — Setup guide
```

In AnyType, convert these → links to Object Relations by:
1. Opening the target document
2. Adding a "Related Architecture" or "Related Feature" property
3. Linking it back to the source document
