# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Formint POS Robyn server server.

Packages the merged server (Robyn async server + Django ORM + Ninja +
ninja-extra + django-fusion + Unfold admin + django-bolt) into a single
executable for the Tauri `externalBin` (`src-tauri/binaries/formint-backend`).

Replaces the legacy `pos-full-server.spec` which referenced the pre-merge
pos-full layout (`shared/`, `models/posapp/`).

Usage (via the server Makefile):
    make server-binary            # pyinstaller formint-server.spec --clean --noconfirm
    make server-install-bin       # copy dist/formint-backend → ../src-tauri/binaries/

Output:
    dist/formint-backend           # copied to src-tauri/binaries/formint-backend-<triple>
"""

import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# NOTE: PyInstaller's SPECPATH is already the directory containing the spec
# file (not the file path) — using dirname() here would walk one level up and
# break pathex resolution for top-level server modules.
if 'SPECPATH' in dir() and SPECPATH:
    _SPEC_DIR = os.path.abspath(SPECPATH)
else:
    _SPEC_DIR = os.getcwd()

# ── Django bootstrap at analysis time ─────────────────────────────────────
# Several INSTALLED_APPS packages (ninja_extra foremost) read Django settings
# at import time via pydantic. Without configured settings, collect_submodules()
# on those packages fails silently and the frozen binary ships without them.
# Configure Django before Analysis so hidden-import collection can import
# every app (app-registry loading does not touch the database).
sys.path.insert(0, _SPEC_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs")
import django  # noqa: E402
from django.conf import settings as _django_settings  # noqa: E402

if not _django_settings.configured:
    django.setup()

# ── Data files (project templates + static) ────────────────────────────────
datas = [
    # Fusion fragment templates + Unfold admin index override
    ("formint/templates", "formint/templates"),
    ("django_templates", "django_templates"),
    # Centralized settings module (server.py bootstraps Django from configs)
    ("configs", "configs"),
    # Managed model package (pos_full app label)
    ("models", "models"),
]

# Site-package data (templates/static for admin UIs)
datas += collect_data_files("unfold")
datas += collect_data_files("django_fusion")
datas += collect_data_files("django", includes=["**/templates/**/*"])
datas += collect_data_files("wagtail", includes=["**/templates/**/*"])

# ── Hidden imports ─────────────────────────────────────────────────────────
# Django app registry is data-driven — PyInstaller cannot see it statically,
# so every INSTALLED_APPS package plus the server's own modules is forced in.
hiddenimports = []

for _pkg in (
    # Django contrib apps used by the admin + auth
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Unfold admin theme
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    # API layer
    "ninja",
    "ninja_extra",
    "django_htmx",
    "django_tables2",
    "django_bolt",
    # CMS dependency of django_fusion.core.models.mixins.display_mode
    "wagtail",
    # django-fusion local library
    "django_fusion",
    # Server app packages
    "formint",
    "models",
    "routes",
    "middleware",
    "signals",
    "streams",
    "fragments",
    # Version metadata (imported lazily inside --version / info routes)
    "about",
    # Server top-level modules (registered for their @receiver side effects)
    "ws_client",
    "ws_sync_signals",
    "sync_signals",
    "signal_handlers",
    "bolt_api",
):
    hiddenimports += collect_submodules(_pkg)

# Django itself must be fully importable (template backends, admin modules)
hiddenimports += collect_submodules("django")

a = Analysis(
    ["server.py"],
    pathex=[_SPEC_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="formint-backend",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
