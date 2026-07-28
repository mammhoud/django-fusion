# Routable Site URLs

The `lms-demo` and `ctc-research` websites mount the shared routable
component site from `www.core.routes` at the `/fusion/` prefix:

```python
from www.core.routes import site

urlpatterns += [path("fusion/", include(site.urls))]
```

Mounting the site before Wagtail's catch-all URL patterns keeps these generated
component routes available at a stable prefix on both websites.

## Generated routes

| URL | App | Purpose | Access |
| --- | --- | --- | --- |
| `/fusion/lms/dashboard/` | LMS | Staff LMS dashboard page. | Authenticated staff users only. |
| `/fusion/lms/courses/list-fragment/` | LMS | HTMX course-list fragment rendered inside the LMS dashboard. | Authenticated staff users only. |
| `/fusion/blog/posts/list-fragment/` | Blog | HTMX blog-post list fragment. | Public read access. |
| `/fusion/blog/posts/create-fragment/` | Blog | HTMX blog-post creation fragment. | Public route visibility follows `BlogApp.has_view_permission`; write actions should still be restricted by the underlying viewset/form permissions. |

## Permission behavior

- `LMSApp.has_view_permission` requires both `user.is_authenticated` and
  `user.is_staff`, so all generated LMS routes under `/fusion/lms/` are intended
  for authenticated staff users.
- `BlogApp.has_view_permission` returns `True`, so generated blog routes under
  `/fusion/blog/` are publicly visible for read use. Mutating blog operations
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
    hx-get="/fusion/lms/courses/list-fragment/"
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
