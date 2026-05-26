import os

from structlog import get_logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
logger = get_logger(__name__)
