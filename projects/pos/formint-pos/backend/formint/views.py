from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from django_fusion.fragments import FragmentRequestRenderer

from .fusion_components import BranchSummaryFragment

# ── django-fusion data components (tables + forms) ─────────────────────────
from .components import FORM_COMPONENTS, TABLE_COMPONENTS


def health(request: HttpRequest) -> JsonResponse:
    return JsonResponse({'status': 'ok', 'product': 'formint-pos', 'phase': 2})


def branch_summary(request: HttpRequest) -> HttpResponse:
    """Render the branch section through Fusion first, then data-only HTMX.

    ``X-Fusion-Render-First: true`` is the explicit migration proof path. The
    normal Astro section uses the lean response and owns its shell/skeleton.
    Both paths share the same component context and therefore the same domain
    contract; only presentation transport differs.
    """
    if request.headers.get('HX-Request') != 'true':
        return JsonResponse(
            {
                'detail': 'This endpoint is an HTMX data fragment.',
                'product': 'formint-pos',
            },
            status=406,
        )

    component = BranchSummaryFragment()
    component.setup(request)
    if request.headers.get('X-Fusion-Render-First') == 'true':
        response = component.render_fragment_response(component.get_fragment_context())
        response['X-Formint-Response-Mode'] = 'django-fusion-fragment'
    else:
        context = component.get_fragment_context()
        response = render(request, 'formint/branch_summary.html', context)
        response['X-Formint-Response-Mode'] = 'htmx-data-only'

    response['Cache-Control'] = 'no-store'
    return response


def fusion_branch_summary(request: HttpRequest) -> HttpResponse:
    """Expose the shared django-fusion renderer for an explicit first-load test."""
    if request.headers.get('HX-Request') != 'true':
        return JsonResponse({'detail': 'HTMX required'}, status=406)

    renderer = FragmentRequestRenderer(request, context={
        'branches': 0,
        'orders_today': 0,
        'sync_status': 'Planned',
    })
    response = renderer.render('formint.branch_summary')
    response['X-Formint-Response-Mode'] = 'django-fusion-fragment'
    return response


def table_fragment(request: HttpRequest, resource: str) -> HttpResponse:
    """GET /htmx/tables/<resource>/ — server-rendered data table fragment.

    Uses the django-fusion ``TableMixin`` + ``RowGenerator`` data component.
    Returns the table region only; Astro owns the surrounding shell.
    """
    component_cls = TABLE_COMPONENTS.get(resource)
    if component_cls is None:
        return JsonResponse(
            {'detail': f'Unknown table resource: {resource}',
             'available': sorted(TABLE_COMPONENTS)},
            status=404,
        )

    component = component_cls()
    if request.headers.get('HX-Request') == 'true' and request.headers.get('X-Fusion-Render-First') == 'true':
        # django-fusion render-first path — reuse the fusion renderer.
        from django_fusion.routes.rendering.renderers import fusion_json_response
        context = component.get_table_context_data()
        return fusion_json_response(data=context, status=200)

    context = component.get_table_context_data()
    context['resource'] = resource
    context['product'] = 'formint-pos'
    # Resource names use hyphens; template files use underscores.
    template = f'formint/tables/{resource.replace("-", "_")}.html'
    response = render(request, template, context)
    response['X-Formint-Response-Mode'] = 'htmx-data-only'
    response['X-Formint-Table-Resource'] = resource
    response['Cache-Control'] = 'no-store'
    return response


def form_fragment(request: HttpRequest, resource: str) -> HttpResponse:
    """GET/POST /htmx/forms/<resource>/ — data component form fragment.

    GET renders the django-fusion ``FormMixin`` model form; POST saves the
    record and returns the matching table fragment (CRUD loop for HTMX).
    """
    component_cls = FORM_COMPONENTS.get(resource)
    if component_cls is None:
        return JsonResponse(
            {'detail': f'Unknown form resource: {resource}',
             'available': sorted(FORM_COMPONENTS)},
            status=404,
        )

    component = component_cls()

    if request.method == 'POST':
        # FormMixin builds form kwargs from form_kwargs (django-fusion API).
        component.form_kwargs = {
            'data': request.POST or None,
            'files': request.FILES or None,
        }
        form = component.get_form()
        if form.is_valid():
            form.save()
            return HttpResponse(
                status=200,
                headers={'HX-Trigger': 'formint-table-refresh',
                         'X-Formint-Saved': 'true'},
            )
        # Invalid → re-render form with errors
        context = {'form': form, 'resource': resource, 'product': 'formint-pos'}
        template = f'formint/forms/{resource.replace("-", "_")}.html'
        response = render(request, template, context)
        response['X-Formint-Response-Mode'] = 'htmx-form-errors'
        response['Cache-Control'] = 'no-store'
        return response

    form = component.get_form()
    context = {'form': form, 'resource': resource, 'product': 'formint-pos'}
    template = f'formint/forms/{resource.replace("-", "_")}.html'
    response = render(request, template, context)
    response['X-Formint-Response-Mode'] = 'htmx-data-only'
    response['Cache-Control'] = 'no-store'
    return response


def _form_to_table_resource(form_resource: str) -> str:
    """Map a form resource to its companion table resource."""
    mapping = {
        'product': 'products',
        'category': 'categories',
        'customer': 'customers',
        'client-category': 'client-categories',
        'supplier': 'suppliers',
    }
    return mapping.get(form_resource, 'products')
