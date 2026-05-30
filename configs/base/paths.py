import os
from pathlib import Path

from configs.site import WORKSPACE_DIR, active_site_dir, active_website_name

BASE_DIR = active_site_dir()
WORKSPACE_BASE_DIR = WORKSPACE_DIR
SITE_NAME = active_website_name()

# Convert to Path objects for consistency
ASSETS_DIR: Path = BASE_DIR / "assets"
CORE_DIR: Path = BASE_DIR / "core"
APPS_DIR: Path = BASE_DIR / "pages"
WWW_DIR: Path = BASE_DIR / "www"
PLUGINS_DIR: Path = BASE_DIR / "plugins"

SRC_DIR: Path = BASE_DIR / "src"

# Backwards-compatible string paths used by a few older integrations.
os.environ.setdefault("DJANGO_WEBSITE_DIR", str(BASE_DIR))
os.environ.setdefault("WEBSITE_DIR", str(BASE_DIR))
os.environ.setdefault("DJANGO_WEBSITE", SITE_NAME)
