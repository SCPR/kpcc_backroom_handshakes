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


class ElectionDetailView(BuildableDetailView):
    model = Election
    template_name = "election_registrar/detail.html"
    slug_field = "electionid"

    def get_object(self):
        object = super(ElectionDetailView, self).get_object()
        return object

    def get_url(self, obj):
        return "/%s" % (obj.electionid)

    def get_context_data(self, **kwargs):
        context = super(ElectionDetailView, self).get_context_data(**kwargs)
        context["result_sources"] = ResultSource.objects.filter(election__id=context["election"].id)
        context["contests"] = Contest.objects.filter(election__id=context["election"].id).filter(
            is_display_priority=True).order_by("contestname")
        return context
