"""Website-local Django settings for crm."""
import sys
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"

for _path in (str(_WORKSPACE_DIR), str(_SITE_APP_DIR), str(_SITE_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ============================================================
# Site Configuration
# ============================================================
from configs.site import configure_site_environment

configure_site_environment("crm", module="CMS", default_port=5074)

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "www.urls"

ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "crm"
WEBSITE_IDENTIFIER = "crm"
SITE_ID = 4

# ── Local apps ──────────────────────────────────────────────
LOCAL_APPS = [
    "www.core",
    "plugins.accounts_app.apps.AccountsAppConfig",
    "plugins.inventory.apps.InventoryConfig",
    "plugins.transactions_app.apps.TransactionsAppConfig",
    "plugins.invoice_app.apps.InvoiceAppConfig",
    "plugins.bills_app.apps.BillsAppConfig",
]
INSTALLED_APPS += LOCAL_APPS

# ── CRM-specific allauth settings ───────────────────────────
# Override shared default (plugins.accounts.adapters.*) — CRM has its own adapter
ACCOUNT_ADAPTER = "plugins.accounts_app.adapters.CRMAccountAdapter"
SOCIALACCOUNT_ADAPTER = "allauth.socialaccount.adapter.DefaultSocialAccountAdapter"

LOGIN_REDIRECT_URL = "/crm/dashboard/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"

# ── Migration modules — point sites to www/migrations ───────
# Overrides the shared default which points to ctc-research's www.migrations
MIGRATION_MODULES = {
    "sites": "www.migrations",
    "crm_core": None,     # www.core has no models of its own
}
