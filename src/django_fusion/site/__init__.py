"""``django_fusion.site`` — generic site-level authentication utilities.

The historical ``site`` package was largely folded into ``routes`` /
``core`` during the comp/ reorganisation (commit ``fd4663a7``), but the
authentication mixins were removed while three products (structa.cloud,
ctc-research, platform) still import them:

    from django_fusion.site.auth.mixins import AuthConfig, AuthProcessorMixin

This package now exists solely to own those restored mixins. Do not add
new site-level modules here — put framework routing in
``django_fusion.routes`` and cross-cutting helpers in ``django_fusion.core``.
"""
