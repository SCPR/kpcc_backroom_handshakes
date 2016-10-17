from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from election_registrar.views import ElectionIndexView, ElectionDetailView

app_name = "election_registrar"

urlpatterns = [
    url(r"(?P<slug>[-\w]+)/$", ElectionDetailView.as_view(), name = "detail"),
    url(r"$", ElectionIndexView.as_view(), name = "list"),
]
