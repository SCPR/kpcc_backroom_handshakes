from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from newscast.views import NewscastIndexView, NewscastDetailView, NewscastCloseMeasuresView, NewscastCloseRacesView

app_name = "newscast"

urlpatterns = [
    url(r"(?P<electionid>[-\w]+)/playlist/close-measures/$", NewscastCloseMeasuresView.as_view(), name="newscast_close_measures"),
    url(r"(?P<electionid>[-\w]+)/playlist/close-races/$", NewscastCloseRacesView.as_view(), name="newscast_close"),
    url(r"(?P<electionid>[-\w]+)/playlist/(?P<slug>[-\w]+)/$", NewscastDetailView.as_view(), name="newscast_detail"),
    url(r"(?P<electionid>[-\w]+)/playlist/$", NewscastIndexView.as_view(), name="newscast_list"),
]
