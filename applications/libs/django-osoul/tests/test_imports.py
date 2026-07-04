def test_public_imports():
    from django_osoul.core.middlewares.error_tracker import ErrorTrackerMiddleware
    from django_osoul.core.middlewares import ErrorTrackerMiddleware as Middleware
    from django_osoul.wagtail.snippets import BaseSnippetViewSet, export_to_csv

    assert ErrorTrackerMiddleware is Middleware
    assert BaseSnippetViewSet is not None
    assert export_to_csv is not None
