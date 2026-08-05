# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the POS Full Robyn server.

Packages the Robyn async server with Django ORM into a single executable
for Tauri sidecar bundling.

Usage:
    pyinstaller sidecar/pos-full-server.spec --clean --noconfirm

Output:
    src-tauri/binaries/pos-full-server-<target-triple>

Dependencies bundled:
    - robyn (Rust-powered async Python server)
    - Django ORM (SQLite backend)
    - All route handlers (routes/ package)
    - All Django models (models/ + posapp/)
    - All shared modules (shared/)
"""

import os
import sys

_SPEC_DIR = os.path.dirname(os.path.abspath(SPECPATH if SPECPATH else __file__ if '__file__' in dir() else os.getcwd()))
# Shared modules live at projects/pos/shared (1 level up from pos-full/)
_SHARED_DIR = os.path.normpath(os.path.join(_SPEC_DIR, "..", "shared"))

# Validate the path exists before PyInstaller tries to use it
if not os.path.isdir(_SHARED_DIR):
    raise FileNotFoundError(f"Shared module directory not found: {_SHARED_DIR} (SPEC_DIR={_SPEC_DIR})")

block_cipher = None

a = Analysis(
    ["server.py"],
    pathex=[_SPEC_DIR],
    binaries=[],
    datas=[
        # Route handlers
        ("routes", "routes"),
        # Django models (managed + posapp Rust-mirror)
        ("models", "models"),
        # Server modules (standalone .py files beside server.py)
        ("handlers.py", "."),
        ("streams.py", "."),
        # Shared modules (signals, models, services, middleware)
        (_SHARED_DIR, "shared"),
    ],
    hiddenimports=[
        # Robyn server framework
        "robyn",
        "robyn.router",
        "robyn.types",
        "robyn.ws",
        "robyn.argument_parser",
        # Django ORM
        "django",
        "django.db",
        "django.db.backends.sqlite3",
        "django.db.migrations",
        "django.core.management",
        "django.apps",
        "django.conf",
        "django.dispatch",
        # Async support
        "asgiref",
        "asgiref.sync",
        # Pydantic validation
        "pydantic",
        # Runtime deps (PyInstaller may miss these)
        "appdirs",
        "packaging",
        # Server modules (extracted from routes/state.py)
        "handlers",
        "streams",
        # Shared modules
        "shared",
        "shared.models",
        "shared.models.audit",
        "shared.models.approval",
        "shared.models.token",
        "shared.models.crm",
        "shared.signals",
        "shared.handlers",
        "shared.handlers.signal",
        "shared.services",
        "shared.services.sync",
        "shared.middleware",
        "shared.middleware.auth",
        "shared.api",
        "shared.api.crud",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="pos-full-server",
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
