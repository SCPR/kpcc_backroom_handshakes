from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.contrib import admin
from tastypie.api import Api
from kpcc_backroom_handshakes.api import CandidateResource, MeasureResource, JudicialResource, ContestResource
import os
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

# invoke the api
v1_api = Api(api_name='v1')
v1_api.register(CandidateResource())
v1_api.register(MeasureResource())
v1_api.register(JudicialResource())
v1_api.register(ContestResource())

admin.autodiscover()

urlpatterns = [
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^admin/", include("massadmin.urls")),
    url(r"^api/?", include(v1_api.urls)),
    url(r"^campaign-finance/?", include("maplight_finance.urls", namespace="campaign-finance")),
    url(r"^ballot-box/?", include("ballot_box.urls", namespace="ballot-box")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )

if settings.DEBUG and settings.MEDIA_ROOT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
