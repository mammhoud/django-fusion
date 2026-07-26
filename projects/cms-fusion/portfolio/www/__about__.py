"""
@author Mahmoud Ezzat
@requires Python 3.12.5 or later

Copyright (c) 2024
All rights reserved.
"""
import logging

logger = logging.getLogger(__name__)

__version__ = "1.0.3"
__version_info__ = tuple(
    [
        int(num) if num.isdigit() else num
        for num in __version__.replace("-", ".", 1).split(".")
    ]
)

__title__ = "VResume"
__description__ = "VResume Personal Portfolio CMS"

"""
hatch version minor
hatch version major,rc
hatch version release
hatch version "0.1.0"
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

uv run hatch version rc,rc,dev,dev

"""
