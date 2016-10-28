from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from newscast.views import NewscastIndexView, NewscastDetailView

app_name = "newscast"

urlpatterns = [
    url(r"(?P<slug>[-\w]+)/$", NewscastDetailView.as_view(), name="newscast_detail"),
    url(r"$", NewscastIndexView.as_view(), name="newscast_list"),
]
