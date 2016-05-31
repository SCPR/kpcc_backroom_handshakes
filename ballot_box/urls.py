from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from .views import ResultIndex, BakedResultsIndex

app_name = "ballot_box"

urlpatterns = [
    url(r'ballot-box/results/index.html$', cache_page(60*10)(BakedResultsIndex.as_view()), name="baked-result-index"),
    url(r'ballot-box/results/$', ResultIndex.as_view(), name="result-index"),
    url(r'ballot-box/$', RedirectView.as_view(url="results/", permanent=False), name='index'),
    url(r'', RedirectView.as_view(url="ballot-box/results/", permanent=False), name='index'),
]
