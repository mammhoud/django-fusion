def test_public_imports():
    from django_osoul.handlers import ErrorTrackerMiddleware
    from django_osoul.middlewares.error_tracker import ErrorTrackerMiddleware as Middleware
    from django_osoul.wagtail.snippets import BaseSnippetViewSet, export_to_csv

    assert ErrorTrackerMiddleware is Middleware
    assert BaseSnippetViewSet is not None
    assert export_to_csv is not None
