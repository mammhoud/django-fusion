# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

__all__ = ("BASE_DIR", "settings")

