# Customizer Template Guidance

Scope: `applications/customizer/templates/`.

- Build templates as customization surfaces for Structa Cloud sites, not as site-specific replacements.
- Show available apps first, then template sections/components discovered from each selected site.
- Prefer `{% comp %}` tags where a django-osoul component exists; otherwise use narrow `{% include %}` calls with only required context.
- Preserve `fragment_name` for fragment identifiers and context keys.
- Keep static demo text isolated from CMS or model-provided content.
