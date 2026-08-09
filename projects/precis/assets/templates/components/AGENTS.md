# Precis Asset Components — AI Agent Instructions

**Scope:** `projects/precis/assets/templates/components/`

These are Precis-owned templates. They are not automatically shared across the
monorepo. Read `projects/precis/backend/AGENTS.md`, then
`libs/django-fusion/AGENTS.md`, before changing a component.

## Component ownership

- Use a local template here for Precis-specific presentation or a deliberate
  product override.
- Use `libs/django-fusion/src/django_fusion/templates/` for framework-level
  components and generic form/table/navigation behavior.
- Use `projects/assets/` only when the component is genuinely shared by active
  products and its context contract is stable.
- Do not duplicate a django-fusion component under a new name just to change
  markup; use the framework's override/registry mechanisms or a clearly named
  Precis component.

## Conventions

- Prefer `{% comp "path" /%}` for registered components.
- Pass only required context and preserve existing context names.
- Use `fragment_name` for HTMX fragment identifiers and context keys.
- Preserve Wagtail fields, translations, permissions, errors, and loading
  states.
- Use BEM classes and no IDs for styling.
- Keep reusable components presentational; put data access and mutations in
  views/services/handlers.

Before editing, search callers, template tags, and the same relative path in
app/framework templates. Test both a normal render and an HTMX fragment when
the component is used on both roads.
