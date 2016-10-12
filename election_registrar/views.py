from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext, Context, loader
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.views.generic import View, ListView, DetailView
from bakery.views import BuildableListView, BuildableDetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django import forms
from .models import *
from ballot_box.models import *
import os
import time
import datetime
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class ElectionIndexView(BuildableListView):
    queryset = Election.objects.order_by("-election_date")
    template_name = "election_registrar/index.html"

    # def get_context_data(self, **kwargs):
        # context = super(ElectionIndexView, self).get_context_data(**kwargs)
        # return context


class ElectionDetailView(BuildableDetailView):
    """ """
    model = Election
    template_name = "election_registrar/detail.html"
    slug_field = "electionid"

    def get_object(self):
        object = super(ElectionDetailView, self).get_object()
        return object

    # def get_url(self, obj):
    #     """
    #     the url at which the detail page should appear.
    #     """
    #     return "/%s" % (obj.official_identifier_slug)

    # def get_build_path(self, obj):
    #     """
    #     used to determine where to build the detail page. override this if you
    #     would like your detail page at a different location. by default it
    #     will be built at get_url() + "index.html"
    #     """
    #     path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
    #     os.path.exists(path) or os.makedirs(path)
    #     return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):
        context = super(ElectionDetailView, self).get_context_data(**kwargs)
        context["result_sources"] = ResultSource.objects.filter(election__id=context["election"].id)
        context["contests"] = Contest.objects.filter(election__id=context["election"].id)
        return context
