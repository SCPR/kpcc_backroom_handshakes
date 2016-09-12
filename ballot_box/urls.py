from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from .views import FeaturedIndex, ResultIndex, BakedFeaturedIndex, BakedResultsIndex

app_name = "ballot_box"

urlpatterns = [

    url(
        r"(?P<electionid>[-\w]+)/results/featured/?$",
        FeaturedIndex.as_view(),
        name="featured-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/featured/index.html$",
        cache_page(60*10)(BakedFeaturedIndex.as_view()),
        name="baked-featured"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/all/?$",
        ResultIndex.as_view(),
        name="result-index"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/all/index.html$",
        cache_page(60*10)(BakedResultsIndex.as_view()),
        name="baked-results"
    ),

    url(
        r"(?P<electionid>[-\w]+)/results/?$",
        RedirectView.as_view(url="all/", permanent=False),
        name="result-index"
    ),

    url(
        r"latest-results/featured/?$",
        FeaturedIndex.as_view(),
        name="featured-index"
    ),

    url(
        r"latest-results/all/?$",
        ResultIndex.as_view(),
        name="result-index"
    ),

]
