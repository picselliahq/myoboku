import logging
import os
from pathlib import Path

from django.utils.log import DEFAULT_LOGGING
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(override=True)
_bool_values = ("1", "on", "true")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", False).lower() in _bool_values

allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = allowed_hosts_env.split(",") if allowed_hosts_env else []

AUTHENTICATION_TOKEN = os.getenv("AUTHENTICATION_TOKEN")
if not AUTHENTICATION_TOKEN:
    raise ValueError("AUTHENTICATION_TOKEN must be defined")

# Application
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "myoboku",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
CONN_MAX_AGE = 60
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

MAXIMUM_RUNNING_CONTAINER = int(os.getenv("MAXIMUM_RUNNING_CONTAINERS", 1))
INSTANCE_NAME = os.getenv("INSTANCE_NAME")

# ================================================================================
# Logging
# ================================================================================


# Copying the default logging value first so that it can use default filters and handlers
LOGGING = DEFAULT_LOGGING
loglevel = os.getenv("DJANGO_LOGLEVEL", "INFO")
loggers_debug = os.getenv("LOGGERS_DEBUG", "")
handlers_loglevel = loglevel if not loggers_debug else "DEBUG"

# Setting simple formatter for all loggers
LOGGING["formatters"]["default"] = {"format": logging.BASIC_FORMAT}
LOGGING["handlers"]["default"] = {
    "class": "logging.StreamHandler",
    "formatter": "default",
}
LOGGING["loggers"]["root"] = {
    "level": loglevel,
    "handlers": ["default"],
}

# Setting default console log level by env variable
LOGGING["handlers"]["console"]["level"] = handlers_loglevel

# Adding console handler when debug is false
LOGGING["handlers"]["console_debug_false"] = {
    "level": handlers_loglevel,
    "filters": ["require_debug_false"],
    "class": "logging.StreamHandler",
}

# Setting default logger log level by env variable
LOGGING["loggers"]["django"]["level"] = loglevel

# Make logger always log on console
LOGGING["loggers"]["django"]["handlers"] = ["console", "console_debug_false"]

# Override template logger so that it stops logging stacktrace on debug
LOGGING["loggers"]["django.template"] = {
    "handlers": ["console", "console_debug_false"],
    "level": loglevel if loglevel != "DEBUG" else "INFO",
}

# Channels server behaves the sames as django server
LOGGING["loggers"]["django.channels.server"] = LOGGING["loggers"]["django.server"]

# Set specified loggers to DEBUG level
for logger in loggers_debug.split(",") if loggers_debug else []:
    if logger not in LOGGING["loggers"]:
        LOGGING["loggers"][logger] = {
            "handlers": ["console", "console_debug_false"],
            "propagate": False,
        }
    LOGGING["loggers"][logger]["level"] = "DEBUG"
