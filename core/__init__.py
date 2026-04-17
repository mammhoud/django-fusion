import os

from structlog import get_logger

# Re-exports for compatibility
from django_osoul.comp import *
from django_rseal.pipelines import *

from .CI import *

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
logger = get_logger(__name__)
