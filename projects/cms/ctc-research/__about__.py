"""
@author Mahmoud Ezzat
@requires Python 3.12.5 or later

Copyright (c) 2024
All rights reserved.
"""
from structlog import getLogger

logger = getLogger()

__version__ = "1.0.3"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)
# __version_info__ = tuple(
# 	[int(num) if num.isdigit() else num for num in __version__.replace("-", ".", 1).split(".")]
# )

# logger.info(
# 	version=__version__,
# 	published=__version_info__[0],
# 	compiled=__version_info__[1],
# 	dev=__version_info__[2],
# 	event="logging",
# )

__name__ = "Version"
__description__ = "A Python package for creating and managing new projects."

"""
hatch version minor
hatch version major,rc
hatch version release
hatch version "0.1.0"

uv run hatch version rc,rc,dev,dev

"""
