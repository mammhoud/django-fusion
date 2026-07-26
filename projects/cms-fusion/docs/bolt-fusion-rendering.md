# Bolt API + Fusion Fragment Rendering Recommendation

## Goal

Enable LMS page components to be rendered by the Django/Bolt server and
displayed inside the Next.js frontend, using Fusion fragments as a
fallback when JSON-only rendering is impractical.

## Background

The LMS currently uses two rendering layers:

1. **Bolt JSON APIs** (`projects/lms/cms/www/api/`) return structured data
   consumed by the Next.js frontend.
2. **Fusion fragments** (`django_fusion.fragments`) render HTML fragments
   from Django templates on demand.

Some page components (complex dashboards, legacy forms, `TableMixin`/Form
viewsets, heavily context-dependent widgets) are faster to keep on the
Django side than to rebuild in React. We therefore need a clean bridge
between the two layers.

## Recommended Strategy: `fusion_render_first`

Each routable page component can declare whether it prefers server-side
Fusion rendering. The new context field `fusion_render_first` on
`RoutableComponent`/`FragmentComponent` signals this to the Next.js
frontend.

### Default behavior

```json
{
  "status": "success",
  "data": { ... }
}
```

Next.js receives JSON and renders React components as usual.

### Fallback behavior (`fusion_render_first: true`)

The Bolt API returns a pointer to the Fusion fragment:

```json
{
  "status": "success",
  "component": "Dashboard",
  "fusion_render_first": true,
  "fragment_name": "lms.dashboard",
  "fragment_url": "/fragments/lms.dashboard/"
}
```

Next.js then fetches the rendered HTML from Django and injects it into the
page.

## Implementation Steps

### 1. Django: enable the fragment

In your `RoutableComponent` or `FragmentComponent` subclass, set
`fusion_render_first = True` and provide a `fragment_name`:

```python
from django_fusion.routes import RoutableComponent


class InstructorDashboardComponent(RoutableComponent):
    route_name = "instructor-dashboard"
    route_path = "instructor/dashboard/"
    template_name = "lms/instructor_dashboard.html"
    fragment_name = "lms.instructor_dashboard"
    fusion_render_first = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["courses"] = Course.objects.filter(instructor=self.request.user)
        return context
```

`RoutableComponent.get_context_data()` now exposes:

- `fusion_render_first` — boolean flag
- `fragment_name` — dotted fragment identifier

### 2. Bolt API: expose the fragment pointer

In your bolt view, return the component context instead of serializing
everything to JSON:

```python
from www.api.data_adapter import bolt_view
from django_fusion.routes import RoutableComponent


@bolt_view
def instructor_dashboard_view(request):
    component = InstructorDashboardComponent()
    component.setup(request)
    context = component.get_context_data()

    return {
        "component": "InstructorDashboard",
        "fusion_render_first": context["fusion_render_first"],
        "fragment_name": context["fragment_name"],
        "fragment_url": f"/fragments/{context['fragment_name'].replace('.', '/')}/",
    }
```

### 3. Next.js: consume the fallback

Create a wrapper component that decides between JSON rendering and Fusion
proxy rendering:

```tsx
// components/FusionProxy.tsx
import { useEffect, useRef, useState } from "react";

interface FusionProxyProps {
  fragmentUrl: string;
  fallback?: React.ReactNode;
}

export function FusionProxy({ fragmentUrl, fallback }: FusionProxyProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [html, setHtml] = useState<string | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(fragmentUrl, { headers: { Accept: "text/html" } })
      .then((res) => res.text())
      .then(setHtml)
      .catch(setError);
  }, [fragmentUrl]);

  if (error) return <>{fallback}</>;
  if (html === null) return <>{fallback}</>;

  return <div ref={ref} dangerouslySetInnerHTML={{ __html: html }} />;
}
```

Use it in a page:

```tsx
// pages/dashboard.tsx
export default function DashboardPage({ data }) {
  if (data.fusion_render_first) {
    return <FusionProxy fragmentUrl={data.fragment_url} />;
  }

  return <Dashboard data={data} />;
}
```

### 4. Preserve interactivity

To keep HTMX behaviors (pagination, forms, lazy loading) inside the injected
fragment, include HTMX on the Next.js side:

```tsx
// pages/_app.tsx
import { useEffect } from "react";

export default function App({ Component, pageProps }) {
  useEffect(() => {
    if (typeof window !== "undefined") {
      require("htmx.org");
    }
  }, []);

  return <Component {...pageProps} />;
}
```

Fusion fragments already emit `HX-*` headers and `hx-*` attributes, so the
injected HTML will continue to work against the Django/Bolt server.

## URL wiring

Ensure the fragment endpoints are mounted in the root URL configuration:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    path("fragments/", include("django_fusion.fragments.urls")),
    # ... other paths
]
```

Bolt API endpoints remain under `/apis/` (or your chosen prefix) and return
the fragment pointer.

## Security & CORS

The Next.js frontend must be able to fetch fragments from Django. Either:

- Run both on the same origin and proxy `/fragments/` through Next.js.
- Configure Django CORS to allow the Next.js origin for `/fragments/`
  requests.

`dangerouslySetInnerHTML` is safe here only because the HTML originates
from the trusted Django/Fusion server. Do not use this pattern to inject
third-party HTML. Sanitize any user-generated content before it reaches
Fusion templates, and ensure fragment endpoints are protected by the same
authentication/authorization as the corresponding Bolt API views.

## When to use `fusion_render_first`

Use it for:

- Complex Django forms with heavy validation logic.
- `TableMixin` / `FormTableMixin` views.
- Components that rely on Wagtail page context.
- Legacy views that would be expensive to rewrite in React.

Avoid it for:

- Simple, static content blocks.
- Highly interactive React-only UI elements.
- SEO-critical pages where server-side React rendering is preferred.

## Migration path

1. Identify components that are painful to maintain as JSON + React.
2. Convert them to `RoutableComponent` or `FragmentComponent`.
3. Set `fusion_render_first = True` on each.
4. Add Bolt endpoints that return the fragment pointer.
5. Replace React page components with the `FusionProxy` wrapper.
6. Gradually migrate back to React where the JSON-first approach is
   simpler.

## Benefits

- **Incremental migration**: keep complex Django views alive while the
  frontend moves to Next.js.
- **Single source of truth**: routing and business logic stay in Django.
- **Progressive enhancement**: HTMX inside injected fragments keeps the UI
  interactive without additional React code.
- **Clear fallback contract**: `fusion_render_first` makes the rendering
  strategy explicit in both the backend response and the component context.

## See also

- `django_fusion.fragments.FragmentRequestView`
- `django_fusion.routes.RoutableComponent`
- `django_fusion.routes.FragmentComponent`
