# project_relaease

## What happened to deleted filter templates

The following templates were intentionally removed:

- `pages/templates/blog/sections/filter.html`
- `pages/templates/portfolio/sections/filter.html`

They are replaced by the shared component:

- `pages/templates/components/search/filter_form.html`

and wired from:

- `pages/templates/blog/fragment.html`
- `pages/templates/portfolio/fragment.html`

This removes duplicated filter markup and keeps one source of truth for:
- search input
- tag toggle buttons
- HTMX request target/indicator behavior

## Infinite scroll flow (HTMX)

### Blog
1. Initial tab render uses `blog/sections/posts.html`.
2. `posts.html` includes `blog/sections/posts_items.html`.
3. `posts_items.html` renders cards and a sentinel `<li>` with `hx-trigger="revealed"` when `page_obj.has_next`.
4. Sentinel requests `blog/search/?...&page=N&append=1`.
5. View returns only `posts_items.html` for append mode, replacing the sentinel and appending more items.

### Portfolio
Same pattern as blog:
1. `portfolio/sections/projects.html`
2. includes `portfolio/sections/projects_items.html`
3. sentinel with `revealed`
4. append request with `append=1`
5. append-only response for incremental loading

## Template/model consistency checks

- Blog modal uses `{% include_block post.body %}` for StreamField content, matching `BlogPost.body` type.
- Portfolio modal keeps rich text rendering from snippet `Project.body`.
- Tag filters default to **show all** when no tags selected.
- Tag filters apply only when `tags` query parameter is provided.
- Tag sections in preview modals render conditionally and are hidden when no tags exist.

## Translation and BEM notes

- Existing BEM class naming was preserved in blog/portfolio item partials.
- Added/retained translated strings only where user-facing text is present (`Loading more...`, empty states).
- No hardcoded replacement of translated headings in existing templates.

## Background/email task notes

- Celery worker/beat runtime flags were tuned to reduce CPU pressure.
- Newsletter and campaign task routing remains unchanged.
- No queue-name changes were introduced, preserving compatibility with current broker routing.

