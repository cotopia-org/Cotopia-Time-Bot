import logging  # noqa: F401
import os
from logging.config import dictConfig

from dotenv import load_dotenv

load_dotenv()

# DISCORD_API_SECRET = os.getenv("DISCORD_API_TOKEN")


# DISCORD_API_SECRET = 'MTIxNDUyODIzNDQ4MjMxMTE4OA.GUeQOK.y6aGzmlKBp1IyUyPVguXn87O0DAalYOudQguQY'
DISCORD_API_SECRET = 'MTEyNzQ3MzQzMzg4MjY3MzI2Mw.GIF-ZA.yNj9icp1DGzEkd4DOztjkjbMpuCToNz4lVhYRg'

DATABASE = os.getenv("DATABASE", 'postgres')
DATABASE_USER = os.getenv("DATABASE_USER", 'postgres')
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", 'secret')
DATABASE_HOST = os.getenv("DATABASE_HOST", 'localhost')
DATABASE_PORT = os.getenv("DATABASE_PORT", '5432')

LOGGING_CONFIG = {
    "version": 1,
    "disabled_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "console2": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "discord": {
            "handlers": ["console2", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

dictConfig(LOGGING_CONFIG)
