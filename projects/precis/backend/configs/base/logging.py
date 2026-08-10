from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "%(levelname)s %(message)s",
        },
        "console": {
            "format": "[%(asctime)s] %(levelname)-8s %(name)s:%(lineno)d  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
            "level": "DEBUG",
        },
        "file_debug": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "debug.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "verbose",
            "level": "DEBUG",
            "filters": ["require_debug_true"],
        },
        "file_app": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "application.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
            "level": "INFO",
        },
        "file_error": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "error.log",
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 10,
            "formatter": "verbose",
            "level": "ERROR",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console", "file_error"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console", "file_error"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console", "file_debug"],
            "level": "DEBUG",
            "propagate": False,
            "filters": ["require_debug_true"],
        },
        "wagtail": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console", "file_app", "file_error"],
        "level": "INFO",
    },
}
