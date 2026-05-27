import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

# Convert to Path objects for consistency
ASSETS_DIR: Path = BASE_DIR / "assets"
CORE_DIR: Path = BASE_DIR / "core"
APPS_DIR: Path = BASE_DIR / "pages"

SRC_DIR: Path = BASE_DIR / "src"
