from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from .views import FeaturedIndex, ResultIndex, BakedFeaturedIndex, BakedResultsIndex

app_name = "ballot_box"

urlpatterns = [
    url(r'ballot-box/results/featured/index.html$', cache_page(60*10)(BakedFeaturedIndex.as_view()), name="baked-featured"),
    url(r'ballot-box/results/featured/$', FeaturedIndex.as_view(), name="featured-index"),
    url(r'ballot-box/results/all/index.html$', cache_page(60*10)(BakedResultsIndex.as_view()), name="baked-results"),
    url(r'ballot-box/results/all/$', ResultIndex.as_view(), name="result-index"),
    # url(r'ballot-box/results$', RedirectView.as_view(url="all/", permanent=False), name='index'),
    url(r'ballot-box/$', RedirectView.as_view(url="results/all/", permanent=False), name='index'),
    url(r'', RedirectView.as_view(url="ballot-box/results/all/", permanent=False), name='index'),
]
