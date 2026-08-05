import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'formint-phase-1-development-only')
DEBUG = os.environ.get('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'testserver']

INSTALLED_APPS = [
    # Unfold — modern admin theme (must come before django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django admin (themed by Unfold)
    'django.contrib.admin',
    'django_fusion',
    'ninja',
    'ninja_extra',
    'django_htmx',
    'django_tables2',
    'formint',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'formint-phase1.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR.parent / 'assets' / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ROOT_URLCONF = 'config.urls'

# ── Unfold Admin Theme Settings ──
UNFOLD = {
    'SITE_TITLE': 'Formint POS — Professional',
    'SITE_HEADER': 'Formint POS Admin',
    'SITE_SUBHEADER': 'Merged Master Manager · Loyalty & Settings',
    'SITE_URL': '/',
    'SITE_SYMBOL': 'storefront',
    # Modern unfold (>= 0.80) dashboard callback — injects KPI/charts/tables
    'DASHBOARD_CALLBACK': 'formint.dashboard.formint_dashboard_callback',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': False,
    'LOGIN': {
        'image': 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1200&q=80',
    },
    'THEME': 'dark',  # dark | light
    'COLORS': {
        'primary': {
            '50': '239 246 255',
            '100': '219 234 254',
            '200': '191 219 254',
            '300': '147 197 253',
            '400': '96 165 250',
            '500': '59 130 246',
            '600': '37 99 235',
            '700': '29 78 216',
            '800': '30 64 175',
            '900': '30 58 138',
            '950': '23 37 84',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {'title': 'POS Core', 'items': [
                {'title': 'Products', 'icon': 'inventory_2', 'link': '/admin/formint/product/'},
                {'title': 'Categories', 'icon': 'category', 'link': '/admin/formint/category/'},
                {'title': 'Customers', 'icon': 'people', 'link': '/admin/formint/customer/'},
                {'title': 'Sales', 'icon': 'shopping_cart', 'link': '/admin/formint/sale/'},
                {'title': 'Employees', 'icon': 'badge', 'link': '/admin/formint/employee/'},
                {'title': 'Inventory', 'icon': 'warehouse', 'link': '/admin/formint/inventorytransaction/'},
            ]},
            {'title': 'Operations', 'items': [
                {'title': 'Suppliers', 'icon': 'local_shipping', 'link': '/admin/formint/supplier/'},
                {'title': 'Purchase Orders', 'icon': 'receipt_long', 'link': '/admin/formint/purchaseorder/'},
                {'title': 'Kitchen Tickets', 'icon': 'restaurant', 'link': '/admin/formint/kitchenticket/'},
                {'title': 'Support Tickets', 'icon': 'support', 'link': '/admin/formint/supportticket/'},
                {'title': 'Menu', 'icon': 'menu_book', 'link': '/admin/formint/menu/'},
            ]},
            {'title': 'Loyalty & Clients', 'items': [
                {'title': 'Client Categories', 'icon': 'workspace_premium', 'link': '/admin/formint/clientcategory/'},
                {'title': 'Loyalty Transactions', 'icon': 'stars', 'link': '/admin/formint/loyaltytransaction/'},
                {'title': 'Customers (People)', 'icon': 'people_alt', 'link': '/admin/formint/customer/'},
            ]},
            {'title': 'Nodes & Sync', 'items': [
                {'title': 'Nodes', 'icon': 'dns', 'link': '/admin/formint/node/'},
                {'title': 'Sync Logs', 'icon': 'sync', 'link': '/admin/formint/synclog/'},
                {'title': 'Device Configs', 'icon': 'settings', 'link': '/admin/formint/deviceconfig/'},
                {'title': 'Cloud Links', 'icon': 'cloud', 'link': '/admin/formint/cloudlink/'},
            ]},
            {'title': 'Settings', 'items': [
                {'title': 'User Settings', 'icon': 'manage_accounts', 'link': '/admin/formint/usersettings/'},
                {'title': 'Users', 'icon': 'person', 'link': '/admin/auth/user/'},
                {'title': 'Groups', 'icon': 'groups', 'link': '/admin/auth/group/'},
            ]},
        ],
    },
}

# ── Superuser bootstrap (used by manage.py --ensure-superuser) ──
FORMINT_ADMIN_EMAIL = os.environ.get('FORMINT_ADMIN_EMAIL', 'admin@formint.local')
FORMINT_ADMIN_PASSWORD = os.environ.get('FORMINT_ADMIN_PASSWORD', 'admin123')
FORMINT_ADMIN_NAME = os.environ.get('FORMINT_ADMIN_NAME', 'Formint Admin')

# django-fusion is the server-rendered component boundary. Formint only
# enables the component and fragment settings it actually uses; it does not
# delegate page layout, loading UI, or business ownership to the library.
COMPONENTS_DIR_NAMES = ('components', 'partials', 'tags')

# ── Fusion Render Mode (django-fusion dual-mode contract) ────────────────
# Mirrors landing-fusion's settings contract. Two content-delivery modes:
#
#   True  → "fusion render first" — Django serves finished server-rendered
#           HTML (or fusion-encoded JSON) as the source of truth.
#   False → "data APIs" — the Astro client renders from /api/v1/* JSON.
#
# Per-request override with the ``X-Fusion-Render-First: true|false`` header
# (see formint/fusion.py get_effective_render_first). Env: FUSION_RENDER_FIRST=1|0
FUSION_RENDER_FIRST_DEFAULT = os.environ.get('FUSION_RENDER_FIRST', '1') == '1'
COMPONENTS_FUSION_RENDER_FIRST_DEFAULT = FUSION_RENDER_FIRST_DEFAULT

# ── Fusion Assets (frontend bundle parity) ────────────────────────────────
# Mirrors the Astro frontend bundler output so Django template tags and the
# Astro build emit the same URLs. Served via: GET /api/v1/assets/ and
# GET /fusion/assets/ (see formint/fusion.py assets_api).
FUSION_ASSETS = {
    'top': {
        'preconnect': [],
        'fonts': [],
        'css': [],
    },
    'bottom': {
        'js': [],
    },
}

FUSION_ASSET_PIPELINE = {
    'enabled': True,
    'webpack': {'enabled': False},
    'components': {
        'enabled': True,
        'manifest_path': str(BASE_DIR / 'staticfiles' / 'components' / 'manifest.json'),
    },
    'static_url': STATIC_URL,
}
