# Precis Backend Site-Root Templates — AI Agent Instructions

**Scope:** `projects/precis/main/backend/templates/`

Read `projects/precis/main/backend/AGENTS.md` and the root `AGENTS.md` first. This
folder is for deliberate Precis site-root templates and overrides, not a
replacement for every app template.

## What belongs here

- `base.html`, `base_page.html`, and the site document shell
- `index.html` and root entry templates
- `errors/` site-wide error pages
- `events/` event templates that are intentionally owned by the backend root
- `wagtailadmin/` Wagtail admin overrides
- A narrow project-wide override that must shadow an app/framework template

## What does not belong here

- Learning-specific templates — keep them under the learning app.
- Blog/profile/account/product templates — keep them under the owning
  `backend/apps/pages/<feature>/templates/` tree.
- Reusable framework components — use `libs/django-fusion` or registered local
  components.
- Templates for Landing-Fusion or another product.

## Override process

Before adding an override:

1. Confirm the template is actually resolved from this directory using
   `settings.py` and a targeted search.
2. Compare the same relative path in the owning app and django-fusion.
3. Preserve block names, context variables, translation tags, permissions,
   Wagtail fields, and HTMX attributes.
4. Keep the override thin; move reusable markup to a registered component.
5. Test both full-page and fragment requests when the template is used by both.

Use `{% comp "path" /%}` for registered components, `{% include_block %}` for
StreamField blocks, and `fragment_name` for fragment identifiers. Use BEM
classes and never add IDs solely for styling.
