# Site Template Overrides

Scope: this site template tree.

## Lookup Strategy

Site templates here are resolved before the django-fusion framework template layer. Keep files in this tree only when they are intentional site-specific overrides, branded shells, or templates that must shadow django-fusion/framework behavior.

## Override Rules

- Prefer deleting exact duplicates and allowing Django to load the django-fusion or project-local equivalent.
- Keep thin overrides for branded variations; move reusable repeated markup into shared includes under `libs/django-fusion/src/django_fusion/templates/components/`.
- Preserve existing template names, include names, block names, and context variables to avoid breaking Wagtail/Django rendering.
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate fragment naming.
- When adding or changing a site override, compare the same relative path in `libs/django-fusion/src/django_fusion/templates/` first.
