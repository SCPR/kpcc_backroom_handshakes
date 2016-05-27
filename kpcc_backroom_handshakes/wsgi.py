"""
WSGI config for accountability_tracker project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ["CONFIG_PATH"] = "%s_PRODUCTION" % ("kpcc_backroom_handshakes".upper())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kpcc_backroom_handshakes.settings_production")

application = get_wsgi_application()
