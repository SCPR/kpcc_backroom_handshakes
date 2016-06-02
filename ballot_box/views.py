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
import os
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class FeaturedIndex(ListView):
    model = Contest
    template_name = "ballot_box/featured.html"

    def get_context_data(self, **kwargs):
        context = super(FeaturedIndex, self).get_context_data(**kwargs)
        queryset = Contest.objects.filter(
            election__electionid="primary-2016-06-07")
        context["featured_list"] = queryset.filter(is_homepage_priority=True)
        return context


class BakedFeaturedIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/featured.html"
    build_path = "featured.html"

    def get_object(self):
        object = super(BakedFeaturedIndex, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(BakedFeaturedIndex, self).get_context_data(**kwargs)
        queryset = Contest.objects.filter(
            election__electionid="primary-2016-06-07")
        context["featured_list"] = queryset.filter(is_homepage_priority=True)
        return context


class ResultIndex(ListView):
    model = Contest
    template_name = "ballot_box/list.html"

    def get_context_data(self, **kwargs):
        context = super(ResultIndex, self).get_context_data(**kwargs)
        queryset = Contest.objects.filter(
            election__electionid="primary-2016-06-07")
        context["featured_list"] = queryset.filter(is_homepage_priority=True)
        context["local_list"] = queryset.filter(
            resultsource__source_short="lac").filter(is_display_priority=True)
        context["house_rep_list"] = queryset.filter(
            contestid__contains="sos-districtwide-us-house-of-representatives")
        context["state_list"] = queryset.filter(
            Q(contestid__contains="sos-districtwide-state-senate") |
            Q(contestid__contains="sos-districtwide-state-assembly")
        ).order_by("contestid")
        return context


class BakedResultsIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/list.html"
    build_path = "all.html"

    def get_object(self):
        object = super(BakedResultsIndex, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(BakedResultsIndex, self).get_context_data(**kwargs)
        queryset = Contest.objects.filter(
            election__electionid="primary-2016-06-07")
        context["featured_list"] = queryset.filter(is_homepage_priority=True)
        context["house_rep_list"] = queryset.filter(
            contestid__contains="sos-districtwide-us-house-of-representatives"
        )
        context["state_list"] = queryset.filter(
            Q(contestid__contains="sos-districtwide-state-senate") |
            Q(contestid__contains="sos-districtwide-state-assembly")
        ).order_by("contestid")
        return context
