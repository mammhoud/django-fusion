# Site Asset Template Overrides — LMS Demo

**Path:** `projects/lms/assets/templates/` — Site asset template overrides

## Lookup Strategy
Site asset templates here are resolved before the shared `projects/assets/templates/` layer but after site-specific templates. Keep files in this tree when they are site-branded variations of shared components.

## Resolution Context
```
1. Site templates (projects/lms/templates/)            ← highest priority
2. Plugin templates (projects/lms/plugins/**/templates/)
3. Site asset templates (this directory)                ← you are here
4. Shared templates (projects/assets/templates/)        ← fallback
```

## Override Rules
- Prefer deleting exact duplicates and letting Django load the shared version
- Keep thin overrides for branded/monogrammed variations
- Move reusable repeated markup into shared includes under `projects/assets/templates/components/`
- Preserve existing template names, include names, block names, and context variables
- Use `fragment_name` for fragment identifiers and context keys

## Quick Reference

### Common Override Patterns
| Scenario | Approach |
|----------|----------|
| Branded logo | Override `layout/landing/header.html` with site logo |
| Custom colors | Use CSS custom properties in site-specific SCSS |
| Footer content | Override `base/footer.html` with site links |
| Error pages | Override `errors/404.html`, `errors/500.html` |

## Conventions
- Use BEM classes: `block__element--modifier`
- No IDs for styling
- Prefer `{% comp "path" /%}` over `{% include %}`

## Customization Tips
1. Always check if the shared template component already exists before creating a site override
2. When removing a site override, verify the shared fallback template works correctly
3. Compare same relative paths in `projects/assets/templates/` first
