#!/usr/bin/env python3
"""Standalone Dynaconf smoke test — verifies YAML values are loaded from
configs/Env/default/_core.yml, _development.yml, and per-project _site.yml."""

import os
import sys
from pathlib import Path

# Ensure the Precis backend's local config package is importable.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_PROJECTS_DIR = _REPO_ROOT / "projects"
_PRECIS_BACKEND = _PROJECTS_DIR / "precis" / "backend"
sys.path.insert(0, str(_PRECIS_BACKEND))

os.environ.setdefault("SERVER_ENV", "development")
os.environ.setdefault("WEBSITE_NAME", "lms-fusion")
os.environ.setdefault("WEBSITE_DIR", str(_PRECIS_BACKEND.parent))

from configs.settings.conf import MainSettings


def check(condition, msg):
    if condition:
        print(f"  ✅ {msg}")
    else:
        print(f"  ❌ FAIL: {msg}")
        sys.exit(1)


print("\n=== Dynaconf Smoke Test ===\n")

# ── Shared _core.yml ──
print("Shared _core.yml:")
s = MainSettings(SERVER_ENV="development", WEBSITE_NAME="lms-fusion",
                 WEBSITE_DIR=str(_PRECIS_BACKEND.parent))
check(s.get("STATIC_URL") == "/static/",
      "STATIC_URL = '/static/' from _core.yml [default]")
check(s.get("MEDIA_URL") == "/media/",
      "MEDIA_URL = '/media/' from _core.yml [default]")
check(s.get("TEMPLATE_DEBUG") is True,
      "TEMPLATE_DEBUG = True from _core.yml [development]")

# ── Shared _development.yml ──
print("\nShared _development.yml:")
check(s.get("EMAIL_STRATEGY") == "console",
      "EMAIL_STRATEGY = 'console' from _development.yml [development]")
check(s.get("DEBUG") is True,
      "DEBUG = True from _development.yml [development]")

# ── Environment switching ──
print("\nEnvironment switching:")
s_test = MainSettings(SERVER_ENV="testing", WEBSITE_NAME="lms-fusion",
                      WEBSITE_DIR=str(_PRECIS_BACKEND.parent))
check(s_test.get("EMAIL_STRATEGY") == "console",
      "testing env: EMAIL_STRATEGY = 'console' from _testing.yml")

s_demo = MainSettings(SERVER_ENV="demo", WEBSITE_NAME="lms-fusion",
                      WEBSITE_DIR=str(_PRECIS_BACKEND.parent))
check(s_demo.get("EMAIL_STRATEGY") == "mailtrap",
      "demo env: EMAIL_STRATEGY = 'mailtrap' from _demo.yml")

s_staging = MainSettings(SERVER_ENV="staging", WEBSITE_NAME="lms-fusion",
                         WEBSITE_DIR=str(_PRECIS_BACKEND.parent))
check(s_staging.get("DEBUG") is False,
      "staging env: DEBUG = False from _staging.yml")

# ── Per-project _site.yml (LMS) ──
print("\nPer-project _site.yml (lms-fusion):")
s_lms = MainSettings(SERVER_ENV="development", WEBSITE_NAME="lms-fusion",
                     WEBSITE_DIR=str(_PRECIS_BACKEND.parent))
check(s_lms.get("FUSION_SITE_NAME") == "Fusion LMS",
      "FUSION_SITE_NAME = 'Fusion LMS'")
check(s_lms.get("FUSION_PRIMARY_COLOR") == "#00a1b3",
      "FUSION_PRIMARY_COLOR = '#00a1b3' (teal)")
check(s_lms.get("FUSION_RENDER_FIRST_DEFAULT") is False,
      "FUSION_RENDER_FIRST_DEFAULT = False")
origins = s_lms.get("CORS_ORIGINS")
check(isinstance(origins, list) and "http://localhost:3458" in origins,
      "CORS_ORIGINS includes localhost:3458")

# ── Per-project _site.yml (CMS — purple, render-first True) ──
print("\nPer-project _site.yml (cms-fusion):")
s_cms = MainSettings(SERVER_ENV="development", WEBSITE_NAME="cms-fusion",
                     WEBSITE_DIR=str(_PROJECTS_DIR / "cms-fusion"))
check(s_cms.get("FUSION_SITE_NAME") == "Fusion CMS",
      "FUSION_SITE_NAME = 'Fusion CMS'")
check(s_cms.get("FUSION_PRIMARY_COLOR") == "#7c3aed",
      "FUSION_PRIMARY_COLOR = '#7c3aed' (purple)")
check(s_cms.get("FUSION_RENDER_FIRST_DEFAULT") is True,
      "FUSION_RENDER_FIRST_DEFAULT = True")

# ── Cross-site uniqueness ──
print("\nCross-site uniqueness:")
lms_color = s_lms.get("FUSION_PRIMARY_COLOR")
cms_color = s_cms.get("FUSION_PRIMARY_COLOR")
check(lms_color != cms_color,
      f"LMS ({lms_color}) ≠ CMS ({cms_color}) — per-project override works")

# ── Edge cases ──
print("\nEdge cases:")
s_unknown = MainSettings(SERVER_ENV="nonexistent", WEBSITE_NAME="lms-fusion",
                         WEBSITE_DIR=str(_PRECIS_BACKEND.parent))
check(s_unknown.get("STATIC_URL") == "/static/",
      "Unknown SERVER_ENV falls back to _core.yml [default]")

# Verify Dynaconf actually loaded files (not just Python defaults).
# Note: _loaded_files is internal and may not be available in all Dynaconf versions.
if s.dynaconf_settings is not None:
    files = getattr(s.dynaconf_settings, "_loaded_files", None) or []
    loaded = [str(f) for f in files]
    core_loaded = any("_core.yml" in f for f in loaded)
    if core_loaded:
        print(f"  ✅ Dynaconf loaded _core.yml — {len(loaded)} total files")
    else:
        print(f"  ⚠️  Dynaconf _loaded_files not populated ({len(loaded)} files) — values verified via assertions above")

print(f"\n{'='*40}")
print("✅ All Dynaconf smoke tests passed!")
print("=" * 40)
