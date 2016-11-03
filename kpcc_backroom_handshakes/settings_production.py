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

# twitter api though should change this
TWITTER_CONSUMER_KEY = CONFIG["api"]["twitter"]["consumer_key"]
TWITTER_CONSUMER_SECRET = CONFIG["api"]["twitter"]["consumer_secret"]
TWITTER_ACCESS_TOKEN = CONFIG["api"]["twitter"]["access_token"]
TWITTER_ACCESS_TOKEN_SECRET = CONFIG["api"]["twitter"]["access_token_secret"]
LOCAL_TWITTER_TIMEZONE = pytz.timezone("US/Pacific")
TWITTER_TIMEZONE = timezone("UTC")

SLACK_TOKEN = CONFIG["api"]["slack"]["token"]
SLACK_API_KEY = CONFIG["api"]["slack"]["api_key"]

# maplight api key
MAP_LIGHT_API_KEY = CONFIG["api"]["maplight"]["api_key"]

REQUEST_HEADERS = {
    "From": CONFIG["api"]["headers"]["from"],
    "User-agent": CONFIG["api"]["headers"]["user_agent"]
}

# assethost api token
ASSETHOST_TOKEN_SECRET = CONFIG["api"]["assethost"]["token_secret"]

# key for the public insight network
PIN_NETWORK_API_KEY = CONFIG["api"]["pin_network"]["api_key"]

# keys for the instagram
INSTAGRAM_CLIENT_ID = CONFIG["api"]["instagram"]["instagram_client_id"]
INSTAGRAM_CLIENT_SECRET = CONFIG["api"]["instagram"]["instagram_client_secret"]

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

# # django debug toolbar configuration
# if DEBUG_TOOLBAR == True:

#     # debugging toolbar middleware
#     MIDDLEWARE_CLASSES += (
#         "debug_toolbar.middleware.DebugToolbarMiddleware",
#     )

#     # javascript panels for the development debugging toolbar
#     DEBUG_TOOLBAR_PANELS = (
#         "debug_toolbar.panels.versions.VersionsPanel",
#         "debug_toolbar.panels.timer.TimerPanel",
#         "debug_toolbar.panels.settings.SettingsPanel",
#         "debug_toolbar.panels.headers.HeadersPanel",
#         "debug_toolbar.panels.request.RequestPanel",
#         "debug_toolbar.panels.profiling.ProfilingPanel",
#         "debug_toolbar.panels.sql.SQLPanel",
#         "debug_toolbar.panels.staticfiles.StaticFilesPanel",
#         "debug_toolbar.panels.templates.TemplatesPanel",
#         "debug_toolbar.panels.cache.CachePanel",
#         "debug_toolbar.panels.signals.SignalsPanel",
#         "debug_toolbar.panels.logging.LoggingPanel",
#         "debug_toolbar.panels.redirects.RedirectsPanel",
#     )

#     # Debug toolbar app
#     INSTALLED_APPS += ("debug_toolbar",)

#     CONFIG_DEFAULTS = {
#         "SHOW_COLLAPSED": False,
#         "SQL_WARNING_THRESHOLD": 500,
#         "INTERCEPT_REDIRECTS": False,
#         "SHOW_TOOLBAR_CONFIG": (lambda: DEBUG)
#     }

#     CACHES = {
#         "default": {
#             "BACKEND": "django.core.cache.backends.dummy.DummyCache",
#         }
#     }

# else:
#     CACHES = {
#         "default": {
#             "BACKEND": "redis_cache.cache.RedisCache",
#             "LOCATION": "%s:%s:%s" % (
#                 CONFIG["cache"]["host"],
#                 CONFIG["cache"]["port"],
#                 CONFIG["cache"]["db"]
#             ),
#             "OPTIONS": {
#                 "CLIENT_CLASS": "redis_cache.client.DefaultClient",
#             }
#         }
#     }

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

# CACHE_MIDDLEWARE_ALIAS = "default"
# CACHE_MIDDLEWARE_SECONDS = (60 * 10)
# CACHE_MIDDLEWARE_KEY_PREFIX = ""

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
                # "slack-error",
                # "slack-debug",


                # slack-info used to log to slack
                # "slack-info",


            ],
            "level": "DEBUG",
            "propagate": False,
        },
    }
}
