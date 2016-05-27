"""
Django settings for kpcc_backroom_handshakes project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import os
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))

CONFIG_PATH = "%s_CONFIG_PATH" % ("kpcc_backroom_handshakes".upper())

CONFIG_FILE = os.environ.setdefault(CONFIG_PATH, "./development.yml")

CONFIG = yaml.load(open(CONFIG_FILE))

DEBUG = CONFIG.get("debug", False)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))

ADMINS = (
    ("", ""),
)

SEND_BROKEN_LINK_EMAILS = True

MANAGERS = ADMINS

TIME_ZONE = "America/Los_Angeles"

LANGUAGE_CODE = "en-us"

SITE_ID = 1

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

TEMPLATES = [
    {
        # "TEMPLATE_DEBUG": "DEBUG",
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            # insert your TEMPLATE_DIRS here
            os.path.join(PROJECT_ROOT, "templates")
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.core.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    #"django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    #"django.middleware.cache.UpdateCacheMiddleware",
    #"django.middleware.cache.FetchFromCacheMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
)

ROOT_URLCONF = "kpcc_backroom_handshakes.urls"

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.flatpages",
    "django.contrib.redirects",
    "django.contrib.humanize",

    # api & tools
    "django_admin_bootstrapped",
    "django.contrib.admin",
    "django.contrib.admindocs",
)

# TEST_RUNNER = "django.test.simple.DjangoTestSuiteRunner"

AUTH_PROFILE_MODULE = "create_user.UserProfile"

# Honor the "X-Forwarded-Proto" header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

XS_SHARING_ALLOWED_ORIGINS = "*"
XS_SHARING_ALLOWED_METHODS = "GET"
