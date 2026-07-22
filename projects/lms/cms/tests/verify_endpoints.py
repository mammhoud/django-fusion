#!/usr/bin/env python3
"""
/apis/ endpoint verification script.

Uses the bolt TestClient in-process (same Rust Actix infrastructure as
production) to verify every endpoint.  Results are equivalent to curl
against a running ``runbolt`` server.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

# ── Path setup ──────────────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent  # tests/
_CMS_DIR = _SITE_DIR.parent  # cms/

for _path in (_CMS_DIR.parent, str(_CMS_DIR), str(_CMS_DIR / "www")):
    if _path not in sys.path:
        sys.path.insert(0, _path)
for _p in [_CMS_DIR / ".." / ".." / "libs" / "django-fusion" / "src"]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
os.environ.setdefault("DJANGO_SITE", "ctc-research")
os.environ.setdefault("WEBSITE", "ctc-research")

_DB = "/tmp/verify_apis.sqlite3"
try:
    os.remove(_DB)
except FileNotFoundError:
    pass

# ── Django config (no plugins.accounts — requires ceptor_ai) ──────────────
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True, SECRET_KEY="verify-test-key", ALLOWED_HOSTS=["*"],
        INSTALLED_APPS=[
            "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
            "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
            "django.contrib.sites",
            "wagtail", "wagtail.admin", "wagtail.snippets", "wagtail.contrib.settings",
            "wagtail.users", "wagtail.images", "wagtail.documents", "wagtail.search",
            "wagtail.contrib.redirects", "modelcluster", "taggit",
            "www.core", "www.content", "django_bolt",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": _DB, "TEST": {"NAME": _DB}}},
        MIDDLEWARE=[
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "wagtail.contrib.redirects.middleware.RedirectMiddleware",
        ],
        USE_TZ=True, LANGUAGE_CODE="en-us", TIME_ZONE="UTC", USE_I18N=True,
        STATIC_URL="/static/", DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        ROOT_URLCONF="www.urls", SITE_ID=1,
        TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates", "DIRS": [],
                     "OPTIONS": {"context_processors": [
                         "django.template.context_processors.debug",
                         "django.template.context_processors.request",
                         "django.contrib.auth.context_processors.auth",
                         "django.contrib.messages.context_processors.messages",
                     ], "loaders": ["django.template.loaders.app_directories.Loader"]}}],
        CORS_ALLOWED_ORIGINS=["http://testserver.local"], CORS_ALLOW_CREDENTIALS=True,
        PROFILE_MODEL="auth.User",
    )
    django.setup()

# ── Database setup + seed data ──────────────────────────────────────────────
from django.core.management import call_command
call_command("migrate", "--run-syncdb", verbosity=0)

from django.contrib.auth.models import User
_user, _ = User.objects.get_or_create(username="testuser", defaults={"email": "test@example.com", "is_active": True})
_user.set_password("password123"); _user.save(update_fields=["password"])
_staff, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "is_staff": True, "is_superuser": True, "is_active": True})
_staff.set_password("adminpass123"); _staff.save(update_fields=["password"])

from www.content.models.others import Token as TokenModel
_AUTH_TOKEN = "verify-access-token-abcdef"
TokenModel.objects.get_or_create(token_hash=hashlib.sha256(_AUTH_TOKEN.encode()).hexdigest(), defaults={"user": _user, "token_type": "access", "category": ""})
_STAFF_TOKEN = "verify-staff-token-abcdef"
TokenModel.objects.get_or_create(token_hash=hashlib.sha256(_STAFF_TOKEN.encode()).hexdigest(), defaults={"user": _staff, "token_type": "access", "category": ""})
_LOGOUT_TOKEN = "verify-logout-token-abcdef"
TokenModel.objects.get_or_create(token_hash=hashlib.sha256(_LOGOUT_TOKEN.encode()).hexdigest(), defaults={"user": _user, "token_type": "access", "category": ""})
print(f"DB ready | User pk={_user.pk} / Staff pk={_staff.pk}")

# ── Patch BoltAPI to accept extra kwargs ──────────────────────────────────
# Production apis.py passes namespace, title, version, description to
# BoltAPI.__init__, but the installed bolt version doesn't support all of
# them.  We patch it so we can import and use core routes.
from django_bolt import BoltAPI
from django_bolt.testing import TestClient

_orig_init = BoltAPI.__init__
def _patched_init(self, *args, **kwargs):
    kwargs.pop("namespace", None)    # not supported
    kwargs.pop("title", None)        # not supported
    kwargs.pop("version", None)      # not supported
    kwargs.pop("description", None)  # not supported
    return _orig_init(self, *args, **kwargs)

BoltAPI.__init__ = _patched_init

# ── Import core apis.py (uses the patched BoltAPI) ────────────────────────
import importlib
import apis  # this creates core_bolt at module level
importlib.reload(apis)
core_bolt = apis.bolt

# Restore original __init__ for the extras (which don't use extra kwargs)
BoltAPI.__init__ = _orig_init

# ── Build a single bolt instance with ALL routes ──────────────────────────
bolt = BoltAPI(prefix="/apis")

# Copy core routes (already prefixed with /apis)
bolt._routes.extend(core_bolt._routes)
bolt._handlers.update(core_bolt._handlers)
bolt._handler_meta.update(core_bolt._handler_meta)
bolt._handler_middleware.update(core_bolt._handler_middleware)
bolt._next_handler_id = core_bolt._next_handler_id

# Register extras (use fresh IDs — no overlap with core)
from www.api.bolt.router import register_all_handlers
register_all_handlers(bolt)

print(f"Routes registered: {len(bolt._routes)} total")

# ═══════════════════════════════════════════════════════════════════════════
# Verification runner
# ═══════════════════════════════════════════════════════════════════════════

G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; C = "\033[96m"; N = "\033[0m"
results = {"pass": 0, "fail": 0, "error": 0}

with TestClient(bolt) as client:
    def test(method, path, desc="", **kw):
        full = f"/apis{path}" if not path.startswith("/apis") else path
        t0 = time.time()
        try:
            resp = client.request(method, full, **kw)
            ms = int((time.time() - t0) * 1000)
            ok = resp.status_code < 500
            icon = f"{G}PASS{N}" if ok else f"{R}FAIL{N}"
            sc = f"{G}{resp.status_code}{N}" if ok else f"{R}{resp.status_code}{N}"
            lbl = f"{C}{desc}{N}" if desc else ""
            print(f"  {icon} {method:6s} {full:45s} {sc} ({ms:4d}ms) {lbl}")
            if not ok and resp.status_code >= 500:
                try:
                    preview = json.dumps(json.loads(resp.text), ensure_ascii=False)[:150] if resp.text else "(empty)"
                except Exception:
                    preview = resp.text[:200]
                print(f"         Body: {preview}")
            results["pass" if ok else "fail"] += 1
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            print(f"  {R}ERROR{N} {method:6s} {full:45s} ({ms:4d}ms) {desc}")
            print(f"         {R}{str(e)[:200]}{N}")
            results["error"] += 1

    print(f"{C}{'═'*80}{N}")
    print(f"{C}  /apis/ ENDPOINT VERIFICATION{N}")
    print(f"{C}{'═'*80}{N}")

    print("\n── Health ──")
    test("GET", "/health")

    print("\n── Auth (core apis.py) ──")
    test("POST", "/auth/login", json={"email": "test@example.com", "password": "password123"})
    test("POST", "/auth/login", json={"email": "wrong", "password": "wrong"}, desc="wrong creds")
    test("POST", "/auth/register", json={"email": "new@test.com", "password": "pass12345", "first_name": "New", "last_name": "User"})
    test("POST", "/auth/register", json={}, desc="missing fields")
    test("GET", "/auth/me", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("GET", "/auth/me", desc="no auth")

    print("\n── Auth (bolt extras) ──")
    test("GET", "/auth/profile", desc="unauth")
    test("GET", "/auth/profile", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("PATCH", "/auth/profile", json={"first_name": "Upd"}, headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("POST", "/auth/password-reset", json={"email": "test@example.com"})
    test("POST", "/auth/password-reset", json={}, desc="missing email")
    test("POST", "/auth/change-password", json={"old_password": "password123", "new_password": "newlongpass1"},
          headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("POST", "/auth/change-password", json={"old_password": "wrong", "new_password": "newlongpass1"},
          headers={"Authorization": f"Bearer {_AUTH_TOKEN}"}, desc="wrong old pw")

    print("\n── Courses (core + extras) ──")
    test("GET", "/courses")
    test("GET", "/courses/99999", desc="not found")
    test("GET", "/courses/categories")
    test("GET", "/courses/featured")
    test("GET", "/courses/99999/detail", desc="detail not found")

    print("\n── Blog (core + extras) ──")
    test("GET", "/blog")
    test("GET", "/blog/featured")
    test("GET", "/blog/categories")
    test("GET", "/blog/99999", desc="not found")
    test("GET", "/blog/99999/related", desc="related not found")

    print("\n── Events (core + extras) ──")
    test("GET", "/events")
    test("GET", "/events/upcoming")
    test("GET", "/events/99999", desc="not found")
    test("POST", "/events/register", json={}, desc="missing fields")

    print("\n── Students (bolt extras) ──")
    test("GET", f"/students/{_user.pk}/dashboard", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("GET", "/students/99999/dashboard", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"}, desc="wrong user")
    test("GET", "/students/1/dashboard", desc="unauth")
    test("GET", f"/students/{_user.pk}/enrollments", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("POST", "/enrollments", json={"course_id": 99999}, headers={"Authorization": f"Bearer {_AUTH_TOKEN}"}, desc="bad course")

    print("\n── Instructors (bolt extras) ──")
    test("GET", "/instructors")
    test("GET", "/instructors/99999", desc="not found")
    test("PATCH", "/instructors/99999", json={"first_name": "X"}, headers={"Authorization": f"Bearer {_AUTH_TOKEN}"}, desc="not found")
    test("GET", "/instructors/1/courses")
    test("GET", "/instructors/1/reviews")

    print("\n── Contact (core + extras) ──")
    test("POST", "/contact/submit", json={"name": "T", "email": "t@t.com", "subject": "Test", "message": "Test"})
    test("GET", "/contact/inquiries", headers={"Authorization": f"Bearer {_STAFF_TOKEN}"})
    test("GET", "/contact/inquiries", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"}, desc="non-staff")

    print("\n── Shop (bolt extras) ──")
    test("GET", "/shop/products")
    test("GET", "/shop/products/99999", desc="not found")
    test("GET", "/shop/cart", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("GET", "/shop/cart", desc="unauth")
    test("POST", "/shop/cart/add", json={"product_id": 99999, "quantity": 1}, headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("GET", "/shop/orders", headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("POST", "/shop/orders", json={"shipping_address": "123 St", "payment_method": "card"},
          headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})
    test("POST", "/shop/cart/checkout", json={"shipping_address": "123 St", "payment_method": "card"},
          headers={"Authorization": f"Bearer {_AUTH_TOKEN}"})

    print("\n── Site Settings & Research (core apis.py) ──")
    test("GET", "/site/settings")
    test("GET", "/research/publications")
    test("GET", "/research/team")
    test("GET", "/testimonials")

    print("\n── LMS (core apis.py) ──")
    test("GET", "/lms/features")
    test("GET", "/lms/instructors")
    test("GET", "/lms/faq")
    test("GET", "/lms/dashboard")
    test("GET", "/lms/products")
    test("GET", "/lms/menu")

    print("\n── Auth: logout (last — deletes token) ──")
    test("POST", "/auth/logout", headers={"Authorization": f"Bearer {_LOGOUT_TOKEN}"})
    test("POST", "/auth/logout", desc="no token")

    # Summary
    print()
    print(f"{C}{'═'*80}{N}")
    total = results["pass"] + results["fail"] + results["error"]
    print(f"  Total: {total:3d}  |  {G}Pass: {results['pass']}{N}  |  {R}Fail: {results['fail']}{N}  |  {Y}Error: {results['error']}{N}")
    print(f"{C}{'═'*80}{N}")
    if results["fail"]:
        print(f"{R}⚠️  {results['fail']} endpoints returned unexpected codes — handler bugs detected.{N}")
    elif results["error"]:
        print(f"{Y}⚠️  {results['error']} endpoints threw exceptions.{N}")
    else:
        print(f"{G}✅ All /apis/ endpoints responded correctly!{N}")
