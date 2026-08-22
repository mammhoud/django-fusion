# MCP-assisted website and webapp enhancement

The django-fusion designer now includes structured, read-only tools for
reviewing and planning website/webapp improvements. The tools encode the
repository's frontend skills, including the anti-slop design checks, responsive
behavior, accessibility, real-asset requirements, interaction states, and
project-specific ownership boundaries.

## Tools

### `designer.website_audit`

Accepts a bounded description of a page or app surface and returns:

- overall score and high-priority count;
- categorized findings for content, composition, responsive behavior,
  accessibility, motion, theme, assets, conversion, and product journeys;
- project guidance for `precis-landing`, `precis`, or `formint`;
- actionable next steps.

The tool does not crawl a URL, fetch external pages, read arbitrary files, or
inspect private application data. The MCP client supplies structured metadata,
which makes the operation deterministic and prevents SSRF and data-leak risks.

### `designer.webapp_enhancement_plan`

Runs the audit and returns four ordered phases:

1. Foundation: tokens, fonts, logos, theme, assets, duplicate paths;
2. Content and structure: value proposition and user journey;
3. Interaction and components: registered django-fusion components, forms,
   tables, Wagtail blocks, loading/error/empty states, keyboard behavior;
4. Verification: project checks, frontend build, accessibility, browser smoke,
   and human review.

The result explicitly returns `apply_required: true` and `deployment_required: true`.
The MCP tool never applies or deploys the plan.

## Design principles encoded by the audit

- Do not default to centered hero + three equal cards + generic gradients.
- Keep the hero concise, with a clear CTA and a real visual asset.
- Vary section layout families instead of repeating the same split/grid pattern.
- Declare mobile behavior for every multi-column section.
- Provide loading, empty, error, success, keyboard, and reduced-motion states.
- Keep one coherent palette and theme strategy.
- Avoid duplicate CTA intent and excessive eyebrows or decorative metadata.
- Use project-owned components, templates, content, and assets.

## Project boundaries

- **Precis Landing:** prioritize content clarity, SEO, catalog discovery,
  newsletter conversion, and social preview assets.
- **Precis:** verify course discovery, course detail, syllabus, enrollment,
  wishlist, progress, lesson navigation, and editorial permissions.
- **Formint:** preserve edition ownership, role-aware authorization, data
  density, offline/online boundaries, and transaction safety.

## MCP integration

Include the existing designer URLs beneath a protected project-owned prefix:

```python
path("fusion/mcp/designer/", include("django_fusion.designer.urls")),
```

The endpoint requires a staff or superuser account. Browser-originated POST
requests must also satisfy the project's normal CSRF policy; an MCP client
should use the project's authenticated session/CSRF flow rather than bypassing
CSRF globally. The two website tools are advertised through standard
`tools/list` metadata with `readOnlyHint: true` and `destructiveHint: false`.

Recommended workflow:

1. Use the repository's design/redesign skills to form a design read.
2. Provide structured page sections and app states to `designer.website_audit`.
3. Use `designer.webapp_enhancement_plan` to order work.
4. Use `designer.component_catalog` and `designer.preview` for registered UI
   primitives with non-sensitive JSON props.
5. Implement changes in the owning project manually.
6. Run project tests/builds/accessibility/browser checks before deployment.

Do not give the MCP client shell, filesystem, migration, or deployment access.
Any future apply capability must be a separately approved, diff-based workflow
with audit logging and rollback.
