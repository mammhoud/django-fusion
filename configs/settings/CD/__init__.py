from configs.settings.conf import settings

# ====================================
# 🧠 Environment Detection
# ====================================
current_env = settings.SERVER_ENV

# ====================================
# 🚀 Load Environment-Specific Settings
# ====================================
if current_env in (Environment.PRODUCTION, Environment.STAGING):
    from .production import *  # noqa: F403
elif current_env in (Environment.DEMO, Environment.DEVELOPMENT):
    from .demo import *  # noqa: F403
else:
    from .core import *  # noqa: F403

# ====================================
# 🎯 CLI Descriptor for Fire
# ====================================
class CLIDescriptor:
    """Descriptor for CLI commands with documentation."""

    def __init__(self, func, doc=None):
        self.func = func
        self.__doc__ = doc or func.__doc__

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return self.func.__get__(obj, objtype)


def cli_command(doc=None):
    """Decorator for CLI commands."""

    def decorator(func):
        return CLIDescriptor(func, doc)

    return decorator
