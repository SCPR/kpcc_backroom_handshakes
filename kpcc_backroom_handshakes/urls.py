from django.conf import settings
from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic import RedirectView
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
    url(r"^elections/", include("rep_the_people.urls", namespace="rep-the-people")),
    url(r"^elections/", include("rep_stance.urls", namespace="rep-stance")),
    # url(r"^elections/", include("cali_cali_congress.urls", namespace="cali-cali-congress")),
    url(r"^elections/", include("newscast.urls", namespace="newscast")),
    url(r"^elections/", include("ballot_box.urls", namespace="ballot-box")),
    url(r"^elections/", include("measure_finance.urls", namespace="campaign-finance")),
    url(r"^elections/", include("election_registrar.urls", namespace="elections")),
    url(r"^", RedirectView.as_view(url="elections/", permanent=False)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
