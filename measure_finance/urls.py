from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from measure_finance.views import InitialDetailView

app_name = "measure_finance"

cache_timer = 60 * 1440

urlpatterns = [

    url(
        r"(?P<electionid>[-\w]+)/measure-finance/(?P<slug>[-\w]+)/?$",
        cache_page(cache_timer)(InitialDetailView.as_view()),
        name = "measure-detail"
    ),

    url(
        r"latest/measure-finance/(?P<slug>[-\w]+)/index.html$",
        cache_page(cache_timer)(InitialDetailView.as_view()),
        name = "measure-detail"
    ),

]
