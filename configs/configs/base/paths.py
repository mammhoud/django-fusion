import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
SRC_DIR: Path = os.path.join(BASE_DIR, "src")
ASSETS_DIR: Path = os.path.join(BASE_DIR, "assets")
CORE_DIR: Path = Path(os.path.join(BASE_DIR, "core"))
APPS_DIR: Path = Path(os.path.join(BASE_DIR, "apps"))
