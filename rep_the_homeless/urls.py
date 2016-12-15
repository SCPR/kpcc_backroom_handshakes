from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.views.decorators.cache import cache_page
from rep_the_homeless.views import IndexView

app_name = "rep_the_homeless"

urlpatterns = [
    url(r"contact/$", IndexView.as_view(), name="contact_index"),
]
