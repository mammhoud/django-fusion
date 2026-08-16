# Routable Site URLs

The `precis-lms` (Precis main) and `precis-ctc` websites mount the shared routable
component site from `apps.core.routes` at the `/components/` prefix:

```python
from apps.core.routes import module

urlpatterns += [path("components/", include((module.urls[0], module.urls[1]), namespace=module.urls[2]))]
```

Mounting the site before Wagtail's catch-all URL patterns keeps these generated
component routes available at a stable prefix on both websites.

## Generated routes

| URL | App | Purpose | Access |
| --- | --- | --- | --- |
| `/components/lms/dashboard/` | LMS | Staff LMS dashboard page. | Authenticated staff users only. |
| `/components/lms/courses/list-fragment/` | LMS | HTMX course-list fragment rendered inside the LMS dashboard. | Authenticated staff users only. |
| `/components/blog/posts/list-fragment/` | Blog | HTMX blog-post list fragment. | Public read access. |
| `/components/blog/posts/create-fragment/` | Blog | HTMX blog-post creation fragment. | Public route visibility follows `BlogApp.has_view_permission`; write actions should still be restricted by the underlying viewset/form permissions. |

## Permission behavior

- `LMSApp.has_view_permission` requires both `user.is_authenticated` and
  `user.is_staff`, so all generated LMS routes under `/components/lms/` are intended
  for authenticated staff users.
- `BlogApp.has_view_permission` returns `True`, so generated blog routes under
  `/components/blog/` are publicly visible for read use. Mutating blog operations
  should continue to rely on the blog component or viewset permission checks.

## HTMX fragment expectations

The fragment routes are designed to be requested by HTMX and inserted into an
already-rendered page shell. They should not be treated as standalone pages.

- Pages should render the layout, navigation, headings, and any initial loading
  placeholder in the normal full-page template.
- Use `hx-get` with the generated fragment URL to load the fragment into a
  dedicated container, for example:

  ```html
  <div
    hx-get="/components/lms/courses/list-fragment/"
    hx-trigger="load"
    hx-target="this"
    hx-swap="outerHTML"
  >
    Loading courses…
  </div>
  ```

- Fragment responses should include only the replaceable component markup needed
  for the target container, not the surrounding `<html>`, `<head>`, or global
  layout.
- Client-side filters, pagination, or create flows should keep using HTMX
  requests against the documented fragment URLs so the page shell remains stable
  while the component content changes.
