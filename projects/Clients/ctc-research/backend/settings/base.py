"""Base security defaults for ctc-research.

Extends the shared ``configs.default`` security layer with the site-specific
ALLOWED_HOSTS/testserver entry and production TLS hardening (Traefik
terminates TLS; Django trusts the forwarded scheme and keeps health probes on
plain HTTP).
"""

from configs.default import *  # noqa: E402,F401,F403

__all__ = [
    "ALLOWED_HOSTS",
    "SECURE_PROXY_SSL_HEADER",
    "SECURE_SSL_REDIRECT",
    "SECURE_REDIRECT_EXEMPT",
    "SECURE_HSTS_SECONDS",
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    "SECURE_HSTS_PRELOAD",
]

# ═══════════════════════════════════════════════════════════════════
# ALLOWED_HOSTS — the Django test client connects as ``testserver``
# ═══════════════════════════════════════════════════════════════════
if "testserver" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, "testserver"]

# TLS terminates at Traefik in production. Tell Django which forwarded scheme
# is authoritative, enforce HTTPS for normal requests, and keep the internal
# container health probes reachable over plain HTTP. Names are defined
# unconditionally (so ``__all__`` exports stay stable); the production values
# only apply when DEBUG is off.
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SECURE_REDIRECT_EXEMPT = ()
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SECURE_REDIRECT_EXEMPT = (r"^health/$", r"^assets/health/$")
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ── APPEND_SLASH — kept at the Django default (True).
#
#    Note: the allauth headless URL patterns (e.g. /api/auth/browser/v1/auth/login)
#    are registered WITHOUT trailing slashes, and CommonMiddleware only appends
#    a slash when the slash-less URL does not match. Exact headless requests
#    therefore resolve directly with no redirect (verified in tests); disabling
#    APPEND_SLASH here would turn the public /api/* 301 redirects into 404s.
