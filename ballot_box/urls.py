from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from .views import EmbeddedDetail, BakedEmbeddedDetail, ResultIndex, BakedResultsIndex, FeaturedIndex, BakedFeaturedIndex

app_name = "ballot_box"

cache_timer = 60 * 5

urlpatterns = [

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
        r"(?P<electionid>[-\w]+)/results/featured/?$",
        cache_page(cache_timer)(FeaturedIndex.as_view()),
        name="featured-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/featured/index.html$",
        cache_page(cache_timer)(BakedFeaturedIndex.as_view()),
        name="baked-featured"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/(?P<slug>[-\w]+)/?$",
        cache_page(cache_timer)(EmbeddedDetail.as_view()),
        name="embedded_detail"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/(?P<slug>[-\w]+)/index.html$",
        cache_page(cache_timer)(BakedEmbeddedDetail.as_view()),
        name="baked-embedded_detail"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results$",
        RedirectView.as_view(url="results/all/", permanent=False),
        name="result-index-redirect"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/$",
        RedirectView.as_view(url="all/", permanent=False),
        name="result-index-redirect"
    ),

]
