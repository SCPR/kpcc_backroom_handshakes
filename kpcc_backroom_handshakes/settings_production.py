# Django settings for kpcc_backroom_handshakes project.

# -*- coding: utf-8 -*-
import os
from os.path import expanduser
from kpcc_backroom_handshakes.settings_common import *
import pytz
from pytz import timezone

DEBUG_TOOLBAR_PATCH_SETTINGS = False

DEBUG_TOOLBAR = DEBUG

INTERNAL_IPS = CONFIG.get("internal_ips", None)

DATABASES = {
    "default": {
        "ENGINE" : "django.db.backends.mysql",
        "NAME" : CONFIG["database"]["database"],
        "USER" : CONFIG["database"]["username"],
        "PASSWORD" : CONFIG["database"]["password"],
        "HOST" : CONFIG["database"]["host"],
        "PORT" : CONFIG["database"]["port"]
    }
}

SECRET_KEY = CONFIG["secret_key"]

if "twitter" in CONFIG["api"]:
    TWITTER_CONSUMER_KEY = CONFIG["api"]["twitter"]["consumer_key"]
    TWITTER_CONSUMER_SECRET = CONFIG["api"]["twitter"]["consumer_secret"]
    TWITTER_ACCESS_TOKEN = CONFIG["api"]["twitter"]["access_token"]
    TWITTER_ACCESS_TOKEN_SECRET = CONFIG["api"]["twitter"]["access_token_secret"]
    LOCAL_TWITTER_TIMEZONE = pytz.timezone("US/Pacific")
    TWITTER_TIMEZONE = timezone("UTC")

if "slack" in CONFIG["api"]:
    SLACK_TOKEN = CONFIG["api"]["slack"]["token"]
    SLACK_API_KEY = CONFIG["api"]["slack"]["api_key"]

if "maplight" in CONFIG["api"]:
    MAP_LIGHT_API_KEY = CONFIG["api"]["maplight"]["api_key"]

if "propublica" in CONFIG["api"]:
    PRO_PUBLICA_API_KEY = CONFIG["api"]["propublica"]["api_key"]

REQUEST_HEADERS = {
    "From": CONFIG["api"]["headers"]["from"],
    "User-agent": CONFIG["api"]["headers"]["user_agent"]
}

# auth to send out emails when models change
if "email" in CONFIG:
    EMAIL_HOST = CONFIG["email"]["host"]
    EMAIL_HOST_USER = CONFIG["email"]["user"]
    EMAIL_HOST_PASSWORD = CONFIG["email"]["password"]
    EMAIL_PORT = CONFIG["email"]["port"]
    EMAIL_USE_TLS = CONFIG["email"]["use_tls"]

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if CONFIG["installed_apps"]:
    INSTALLED_APPS += tuple(CONFIG["installed_apps"])
else:
    pass

if DEBUG == True:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": "handshakes_cache",
            "TIMEOUT": 600,
            "OPTIONS": {
                "MAX_ENTRIES": 500
            }
        }
    }

# Python dotted path to the WSGI application used by Django"s runserver.
WSGI_APPLICATION = "kpcc_backroom_handshakes.wsgi.application"

ADMIN_MEDIA_PREFIX = "/media/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ""

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ""

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

SITE_URL = CONFIG["site_url"]

# Additional locations of static files
STATICFILES_DIRS = (

)

# build paths inside the project like this: os.path.join(base_dir, ...)
if "build" in CONFIG:
    STAGING = CONFIG["build"]["staging"]
    STAGING_PREFIX = CONFIG["build"]["staging_prefix"]
    LIVE_PREFIX = CONFIG["build"]["live_prefix"]
    DEPLOY_DIR = CONFIG["build"]["deploy_dir"]
    STATIC_DIR = STATIC_URL
    BUILD_DIR = os.path.join(STATIC_ROOT, CONFIG["build"]["build_dir"])
    BAKERY_VIEWS = tuple(CONFIG["build"]["views"])
    URL_PATH = ""
    AWS_BUCKET_NAME = CONFIG["build"]["aws_bucket_name"]
    AWS_ACCESS_KEY_ID = CONFIG["build"]["aws_access_key_id"]
    AWS_SECRET_ACCESS_KEY = CONFIG["build"]["aws_secret_access_key"]
    AWS_S3_HOST = CONFIG["build"]["aws_s3_host"]
    BAKERY_CACHE_CONTROL = {
        'text/html': CONFIG["build"]["bakery_cache_control"]["html"],
        'application/javascript': CONFIG["build"]["bakery_cache_control"]["javascript"]
    }

    STATIC_TO_IGNORE = tuple(CONFIG["build"]["static_to_ignore"])

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

LOGGING = {
    "version": 1,

    "disable_existing_loggers": True,

    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },

    "formatters": {
        "verbose": {
            "format" : "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
            "datefmt" : "%d/%b/%Y %H:%M:%S"
        },
        "simple": {
            "format": "\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s"
        },
    },

    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        "slack-error": {
            "level": "ERROR",
            "api_key": SLACK_API_KEY,
            "username": "ElexLogger",
            "icon_url": "https://pbs.twimg.com/media/CSWMwztWoAAYoxC.jpg",
            "class": "slacker_log_handler.SlackerLogHandler",
            "channel": "#logging-2016-election"
        },
        "slack-debug": {
            "level": "DEBUG",
            "username": "ElexLogger",
            "icon_url": "https://pbs.twimg.com/media/CSWMwztWoAAYoxC.jpg",
            "api_key": SLACK_API_KEY,
            "class": "slacker_log_handler.SlackerLogHandler",
            "channel": "#logging-2016-election"
        },
        "slack-info": {
            "level": "INFO",
            "username": "ElexLogger",
            "icon_url": "https://pbs.twimg.com/media/CSWMwztWoAAYoxC.jpg",
            "api_key": SLACK_API_KEY,
            "class": "slacker_log_handler.SlackerLogHandler",
            "channel": "#logging-2016-election"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "mysite.log",
            "formatter": "verbose"
        },
    },

    "loggers": {
        "kpcc_backroom_handshakes": {
            "handlers": [
                "console",
                "mail_admins",
                "slack-info",
            ],
            "level": "DEBUG",
            "propagate": False,
        },
    }
}
