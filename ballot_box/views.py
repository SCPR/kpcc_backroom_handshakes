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
from ballot_box.models import *
from election_registrar.models import *
import os
import time
import datetime
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class EmbeddedDetail(DetailView):
    model = Contest
    template_name = "ballot_box/embedded_race.html"
    slug_field = "contestid"

    def get_object(self):
        object = super(EmbeddedDetail, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(EmbeddedDetail, self).get_context_data(**kwargs)
        context["electionid"] = self.kwargs["electionid"]
        context["contestid"] = self.kwargs["slug"]
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["contest"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(contestid=context["contestid"]).first()
        return context


class FeaturedIndex(ListView):
    model = Contest
    template_name = "ballot_box/featured_races.html"

    def get_object(self):
        object = super(FeaturedIndex, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(FeaturedIndex, self).get_context_data(**kwargs)
        context["electionid"] = self.kwargs["electionid"]
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        queryset = Contest.objects.filter(election__electionid=context["electionid"]).filter(is_homepage_priority=True)
        context["featured_races"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=False)
        context["featured_measures"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=True)
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).filter(source_short="sos").first()
        return context


class BakedFeaturedIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/featured_races.html"
    build_path = "results/featured.html"

    def get_object(self):
        object = super(BakedFeaturedIndex, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(BakedFeaturedIndex, self).get_context_data(**kwargs)
        context["electionid"] = self.kwargs["electionid"]
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        queryset = Contest.objects.filter(election__electionid=context["electionid"]).filter(is_homepage_priority=True)
        context["featured_races"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=False)
        context["featured_measures"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=True)
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).filter(source_short="sos").first()
        return context


class ResultIndex(ListView):
    model = Contest
    template_name = "ballot_box/list_races.html"

    def get_object(self):
        object = super(ResultIndex, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(ResultIndex, self).get_context_data(**kwargs)
        context["electionid"] = self.kwargs["electionid"]
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        queryset = Contest.objects.filter(election__electionid=context["electionid"]).filter(is_display_priority=True)
        context["national_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(contestid__contains="sos-statewide-president") |
                Q(contestid__contains="sos-statewide-us-senate") |
                Q(contestid__contains="sos-districtwide-united-states-representative")
        ).order_by("contestname")
        context["state_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(contestid__contains="sos-districtwide-state-senate") |
                Q(contestid__contains="sos-districtwide-state-assembly")
        ).order_by("contestname")
        context["local_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="lac") |
                Q(resultsource__source_short="oc")
        ).order_by("contestname")
        context["state_measures"] = queryset.filter(is_ballot_measure=True).filter(resultsource__source_short="sos").order_by("contestname")
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(resultsource__source_short="lac") |
            Q(resultsource__source_short="oc")
        ).order_by("contestname")
        return context


class BakedResultsIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/list_races.html"
    build_path = "results/all.html"

    def get_object(self):
        object = super(BakedResultsIndex, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(BakedResultsIndex, self).get_context_data(**kwargs)
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        queryset = Contest.objects.filter(election__electionid="primary-2016-06-07")
        context["dem_pres"] = queryset.filter(contestid="primary-2016-06-07-sos-statewide-president-democratic").first()
        context["gop_pres"] = queryset.filter(contestid="primary-2016-06-07-sos-statewide-president-republican").first()
        context["senate_primary"] = queryset.filter(contestid="primary-2016-06-07-sos-statewide-us-senate").first()
        context["additional_list"] = queryset.filter(
            Q(contestid="primary-2016-06-07-sos-california-proposition-50") |
            Q(contestid="primary-2016-06-07-sos-statewide-president-green") |
            Q(contestid="primary-2016-06-07-sos-statewide-president-american-independent") |
            Q(contestid="primary-2016-06-07-sos-statewide-president-libertarian") |
            Q(contestid="primary-2016-06-07-sos-statewide-president-peace-and-freedom")
        )
        context["local_list"] = queryset.filter(is_display_priority=True).filter(
            Q(resultsource__source_short="lac") |
            Q(resultsource__source_short="oc")

        )
        context["state_list"] = queryset.filter(
            Q(contestid__contains="sos-districtwide-state-senate") |
            Q(contestid__contains="sos-districtwide-state-assembly")
        )
        context["house_rep_list"] = queryset.filter(contestid__contains="sos-districtwide-us-house-of-representatives")
        return context
