from configs.base import *

# ====================================
# 🧠 Environment Detection
# ====================================
current_env = settings.SERVER_ENV

# ====================================
# 🚀 Load Environment-Specific Settings
# ====================================
if current_env == Environment.PRODUCTION:
    from .production import *  # noqa: F403
else:
    from .core import *  # noqa: F403
