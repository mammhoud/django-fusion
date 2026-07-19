# VResume Site Template Overrides

Scope: this site template tree.

## Lookup Strategy

Site templates here are resolved before the shared `projects/assets/templates/` layer. Keep files in this tree only when they are intentional site-specific overrides, branded shells, or templates that must shadow shared behavior.

VResume has additional template directories at:
- `projects/portfolio/www/pages/templates/` — page-level templates
- `projects/portfolio/www/pages/connect/templates/` — connect/contact templates
- `projects/portfolio/plugins/accounts/templates/` — account/auth plugins

## Override Rules

- Prefer deleting exact duplicates and allowing Django to load `projects/assets/templates/<relative-path>`.
- Keep thin overrides for branded variations; move reusable repeated markup into shared includes under `projects/assets/templates/components/`.
- Preserve existing template names, include names, block names, and context variables to avoid breaking Wagtail/Django rendering.
- Use `fragment_name` for fragment identifiers and context keys; do not introduce alternate fragment naming.
- When adding or changing a site override, compare the same relative path in `projects/assets/templates/` first.

## Template Structure

Use the shared folder conventions: `home/`, `about/`, `contact/`, `services/`, `events/`,
`layout/`, `components/`, `sections/`, `blocks/`, `fragments/`, `modals/`.

VResume-specific page models:
- **HomePage** — `home/home_page.html`
- **AboutPage** — `about/about_page.html`
- **ResumePage** — `cv/resume_page.html`
- **ContactPage** — `connect/contact_page.html`
- **PortfolioPage** — `portfolio/portfolio_page.html`
- **BlogPage** — `blog/blog_page.html`

## Customization Tips

- Search nearby templates first, then shared templates, before adding a new partial.
- When replacing a component, copy the equivalent data bindings from the old markup to the new include or partial.
- Use BEM-style CSS classes and do not use IDs for styling.
- Use `{% include %}` for reusable components and pass only the required context.
