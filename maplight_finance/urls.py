from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from maplight_finance.views import InitialDetailView

app_name = "maplight_finance"

urlpatterns = [
    url(r"(?P<slug>[-\w]+)/$", InitialDetailView.as_view(), name = "measure-detail"),
]
