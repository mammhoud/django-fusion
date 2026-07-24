"""
@author Mahmoud Ezzat
@requires Python 3.12.5 or later

Copyright (c) 2024
All rights reserved.
"""
from structlog import getLogger

logger = getLogger()

__version__ = "1.0.0"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)

__name__ = "cms-full"
__description__ = "Unified CMS Full — merged CTC Research + LMS. Part of Structa Cloud workspace."
