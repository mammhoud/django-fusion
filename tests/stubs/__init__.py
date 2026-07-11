"""Stub tag libraries for django-fusion tests.

Provides empty Library() objects for tag libraries (Wagtail, laces, etc.)
that the canonical django-fusion templates load for production use but
that aren't installed in the test environment. This lets get_template()
parse the templates without requiring those packages.
"""
