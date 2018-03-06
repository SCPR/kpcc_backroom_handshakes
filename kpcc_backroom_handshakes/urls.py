from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.contrib import admin
import os
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

admin.autodiscover()

urlpatterns = [
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^admin/", include("massadmin.urls")),
    url(r"^elections/", include("newscast.urls", namespace="newscast")),
    url(r"^elections/", include("ballot_box.urls", namespace="ballot-box")),
    url(r"^elections/", include("measure_finance.urls", namespace="campaign-finance")),
    url(r"^elections/", include("election_registrar.urls", namespace="elections")),
    # url(r"^", RedirectView.as_view(url="elections/", permanent=False)),
]
