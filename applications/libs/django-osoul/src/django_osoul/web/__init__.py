"""Web layer — allauth adapters, auth backends, view mixins, and rendering.

Sub-packages
------------
web.adapters    django-allauth account and social auth adapters.
web.backends    Custom Django authentication backends.
web.routes      URL route helpers for the web layer.
web.views       View mixins: FilterMixin, SearchMixin for class-based views.

Primary exports::

    from django_osoul.web.views.mixins import FilterMixin, SearchMixin
    from django_osoul.web.adapters.account import AccountAdapter
    from django_osoul.web.backends.auth import AuthBackend
"""
