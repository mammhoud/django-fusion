"""API configuration for ctc-research — CORS origins + FUSION_BOLT.

CORS origins resolve from ``_site.yml`` (YAML key: CORS_ORIGINS). FUSION_BOLT
is a complex nested config kept inline (not in YAML).
"""

from configs.default import *  # noqa: E402,F401,F403
from corsheaders.defaults import default_headers  # noqa: E402

__all__ = [
    "CORS_ALLOWED_ORIGINS",
    "CORS_ALLOW_HEADERS",
    "FUSION_BOLT",
]

# ═══════════════════════════════════════════════════════════════════
# CORS Origins — resolved from _site.yml (YAML key: CORS_ORIGINS)
# ═══════════════════════════════════════════════════════════════════
CORS_ALLOWED_ORIGINS = cfg("CORS_ORIGINS", [
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://localhost:3458",
    "http://127.0.0.1:3458",
    "https://ctc-research.com",
    "https://www.ctc-research.com",
    "https://arch.ctc-research.com",
    "https://precis-lms.com",
    "https://www.precis-lms.com",
])

# Allow custom fusion headers for render-first negotiation.
CORS_ALLOW_HEADERS = [*default_headers, "x-fusion-render-first"]


# ═══════════════════════════════════════════════════════════════════
# Bolt API — complex nested config, kept inline (not in YAML)
# ═══════════════════════════════════════════════════════════════════
FUSION_BOLT = {
    "enabled": True,
    "prefix": "/api",
    "openapi_title": "CTC Research API",
    "openapi_version": "1.0.0",
    "auth_backends": ["jwt"],
    "serializer_format": "dict",
    "cors_origins": [
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "https://ctc-research.com",
        "https://www.ctc-research.com",
        "https://arch.ctc-research.com",
        "https://precis-lms.com",
        "https://www.precis-lms.com",
    ],
    "component_auto_register": True,
}
