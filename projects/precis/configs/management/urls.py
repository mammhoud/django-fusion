"""Minimal URLconf for the shared task-worker sentinel.

The shared-worker / shared-scheduler run background tasks only — they never
serve HTTP.  ``rundramatiq`` still runs Django's system checks (which import
``ROOT_URLCONF``), so the sentinel needs a URLconf that does NOT import the
site-specific ``apps.urls`` tree.  Importing that tree instantiates ``LMSApp``
and its per-site model graph — models that are deliberately absent from this
site-agnostic ``INSTALLED_APPS`` — and crashes the worker at boot.
"""

urlpatterns = []
