from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from .views import FeaturedIndex, ResultIndex, BakedFeaturedIndex, BakedResultsIndex, RedesignIndex

app_name = "ballot_box"

cache_timer = 60 * 5

urlpatterns = [

    url(
        r"(?P<electionid>[-\w]+)/results/featured/?$",
        cache_page(cache_timer)(FeaturedIndex.as_view()),
        name="featured-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/featured/redesign/?$",
        cache_page(cache_timer)(RedesignIndex.as_view()),
        name="redesign-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/featured/index.html$",
        cache_page(cache_timer)(BakedFeaturedIndex.as_view()),
        name="baked-featured"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/all/?$",
        cache_page(cache_timer)(ResultIndex.as_view()),
        name="result-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/all/index.html$",
        cache_page(cache_timer)(BakedResultsIndex.as_view()),
        name="baked-results"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results$",
        RedirectView.as_view(url="results/all/", permanent=False),
        name="result-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/$",
        RedirectView.as_view(url="all/", permanent=False),
        name="result-index"
    ),

]
