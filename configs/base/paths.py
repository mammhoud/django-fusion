import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
SRC_DIR: Path = os.path.join(BASE_DIR, "src")
ASSETS_DIR: Path = os.path.join(BASE_DIR, "assets")
TEMPLATES_DIR: Path = os.path.join(BASE_DIR, "templates")
CORE_DIR: Path = Path(os.path.join(BASE_DIR, "www", "core"))
APPS_DIR: Path = Path(os.path.join(BASE_DIR, "www"))
