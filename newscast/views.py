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
from newscast.models import *
from ballot_box.models import *
import os
import time
import datetime
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class NewscastIndexView(BuildableListView):
    queryset = Topic.objects.all()
    template_name = "newscast/index.html"


class NewscastDetailView(BuildableDetailView):
    """ """
    model = Topic
    template_name = "newscast/detail.html"
    slug_field = "topicslug"

    def get_object(self):
        object = super(NewscastDetailView, self).get_object()
        return object

    def get_context_data(self, **kwargs):
        context = super(NewscastDetailView, self).get_context_data(**kwargs)
        context["topicslug"] = self.kwargs["slug"]
        context["topic"] = Topic.objects.filter(topicslug=context["topicslug"]).first()
        context["contests"] = context["topic"].contest.all()
        for contest in context["contests"]:
            try:
                contextualize = ContestContext.objects.filter(contestid=contest.contestid).first()
                contest.geography = contextualize.cities_counties_list
            except:
                contest.geography = None
        return context


class NewscastCloseRacesView(BuildableListView):
    """ """
    queryset = Contest.objects.filter(is_display_priority=True)
    template_name = "newscast/close_races.html"
    electionid = "general-2016-11-08"

    def get_context_data(self, **kwargs):
        context = super(NewscastCloseRacesView, self).get_context_data(**kwargs)
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.electionid
        context["close_races"] = []
        context["target_races"] = self.queryset
        for contest in context["target_races"]:
            if contest.is_ballot_measure == False:
                candidates = contest.candidate_set.all().order_by("-votepct")
                if len(candidates) >= 2:
                    if candidates[0].votepct == None or candidates[1].votepct == None:
                        contest.close_race = False
                    else:
                        margin_points = (candidates[0].votepct - candidates[1].votepct) * 100
                        if margin_points <= 2.5:
                            contest.close_race = True
                            context["close_races"].append(contest)
                        else:
                            contest.close_race = False
                else:
                    contest.close_race = False
            try:
                contextualize = ContestContext.objects.filter(contestid=contest.contestid).first()
                contest.geography = contextualize.cities_counties_list
            except:
                contest.geography = None
        context["number_of_close_races"] = len(context["close_races"])
        return context


class NewscastCloseMeasuresView(BuildableListView):
    """ """
    queryset = Contest.objects.filter(is_display_priority=True)
    template_name = "newscast/close_measures.html"
    electionid = "general-2016-11-08"

    def get_context_data(self, **kwargs):
        context = super(NewscastCloseMeasuresView, self).get_context_data(**kwargs)
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.electionid
        context["close_measures"] = []
        context["target_measures"] = self.queryset
        for contest in context["target_measures"]:
            if contest.is_ballot_measure == True:
                measures = contest.ballotmeasure_set.all()
                for measure in measures:
                    if measure.yespct == None or measure.nopct == None:
                        measure.close_measure = False
                    else:
                        margin_points = (measure.yespct - measure.nopct) * 100
                        if abs(margin_points) <= 2.5:
                            measure.precinctsreportingpct = contest.precinctsreportingpct
                            measure.contestname = contest.contestname
                            measure.close_race = True
                            context["close_measures"].append(measure)
                        else:
                            measure.close_race = False
        context["number_of_close_measures"] = len(context["close_measures"])
        return context
