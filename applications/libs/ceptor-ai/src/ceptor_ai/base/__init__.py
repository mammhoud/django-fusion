"""Base app configuration and cross-cutting integration hooks.

Sub-packages
------------
base.config         App-level settings conf and defaults.
base.core           Core Django app config (apps.py), exception classes, URLs.
base.integration    Wagtail hooks and user signal bindings wired at startup.

Usage::

    INSTALLED_APPS += ["ceptor_ai.base.core.apps.CeptorAIBaseConfig"]
"""
