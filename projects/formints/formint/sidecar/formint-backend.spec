# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Formint Django sidecar binary.

Builds the Django management entry point (sidecar.py) into a single
executable for Tauri sidecar bundling (externalBin "binaries/formint-backend").

Django discovers apps dynamically (INSTALLED_APPS in configs/__init__.py),
so the spec must collect submodules for every app package plus data files
(templates) for Django/unfold/django-fusion.

Usage:
    .venv/bin/pyinstaller sidecar/formint-backend.spec --clean --noconfirm

Output:
    dist/formint-backend  → copy to src-tauri/binaries/formint-backend-<target-triple>
"""

import os
import sys

from importlib.metadata import distributions

from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

_SPEC_DIR = os.path.abspath(SPECPATH)  # SPECPATH is already the spec's directory
# The spec process's sys.path does NOT include the project source dir, so the
# locally-developed Django app packages (configs/, formint/, models/) must be
# made importable for collect_submodules() and Analysis hidden-import
# resolution. pathex below covers the Analysis subprocess as well.
sys.path.insert(0, _SPEC_DIR)

hiddenimports = []
for pkg in (
    "formint",
    "models",
    "configs",
    "django_fusion",
    "unfold",
    "wagtail",
    "ninja",
    "ninja_extra",
    "django_tasks",  # dynamic backend lookup (django_tasks.backends.*)
    # Django-native sidecar surface (replaces the removed Robyn server/routes)
    "fragments",
    "services",
):
    hiddenimports += collect_submodules(pkg)

# Top-level sidecar modules — signal receivers are registered for their
# @receiver side effects and the Django views replace the Robyn routes.
hiddenimports += [
    "views_django",
    "htmx_views",
    "api_keys_views",
    "fusion_views",
    "bolt_api",
    "consumers",
    "ws_client",
    "ws_sync_signals",
    "sync_signals",
    "signal_handlers",
    "signals",
    "about",
]

# Django app-label modules that must resolve at registry build time.
hiddenimports += [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.core.management",
    "django.core.management.commands.runserver",
    "django.core.management.commands.migrate",
    "django.core.management.commands.check",
]

datas = []
for pkg in (
    "unfold",
    "django_fusion",
    "django.contrib.admin",
    "django.contrib.auth",
    "ninja",  # swagger/redoc docs templates
):
    datas += collect_data_files(pkg)

# Local template trees (Django APP_DIRS cannot reach frozen packages' templates
# unless they are unpacked as real files).
datas += [
    (os.path.join(_SPEC_DIR, "django_templates"), "django_templates"),
    (os.path.join(_SPEC_DIR, "formint", "templates"), "formint/templates"),
]

# Several dependencies (django_tasks, wagtail, django_fusion, ...) call
# importlib.metadata.version() at import time, which fails in frozen apps
# unless the dist-info metadata is bundled. Copy metadata for every
# distribution installed in the build venv (small files, fully robust).
for _dist in distributions():
    try:
        datas += copy_metadata(_dist.metadata["Name"])
    except Exception:
        pass

a = Analysis(
    [os.path.join(_SPEC_DIR, "sidecar.py")],
    pathex=[_SPEC_DIR],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "IPython"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

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
