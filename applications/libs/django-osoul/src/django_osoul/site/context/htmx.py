def CONTEXT(request):
    return {
        'htmx_target': getattr(request.htmx, 'target', None) if hasattr(request, 'htmx') else None,
    }
