from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template import RequestContext, Context, loader
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.utils.decorators import method_decorator
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

# ELECTIONID = "general-2016-11-08"
ELECTIONID = "primary-2018-06-05"

class EmbeddedDetail(DetailView):
    model = Contest
    template_name = "ballot_box/embedded_race.html"
    slug_field = "contestid"


    def get_object(self):
        object = super(EmbeddedDetail, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(EmbeddedDetail, self).get_context_data(**kwargs)
        context["is_homepage"] = False
        context["is_featured"] = False
        context["is_all"] = False
        context["baked"] = False
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.kwargs["electionid"]
        context["election_meta"] = Election.objects.filter(electionid=context["electionid"]).first()
        context["contestid"] = self.kwargs["slug"]
        context["contest"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(contestid=context["contestid"]).first()
        return context


@method_decorator(xframe_options_exempt, name='dispatch')
class BakedEmbeddedDetail(BuildableDetailView):
    template_name = "ballot_box/embedded_race.html"
    slug_field = "contestid"
    electionid = ELECTIONID
    sub_directory = "%s/results/" % (electionid)


    def get_object(self):
        object = super(BakedEmbeddedDetail, self).get_object()
        return object


    def get_url(self, obj):
        return "/%s" % (obj.contestid)


    def get_build_path(self, obj):
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")


    def dispatch(self, *args, **kwargs):
        return super(BakedEmbeddedDetail, self).dispatch(*args, **kwargs)


    def get_queryset(self):
        return Contest.objects.filter(election__electionid=self.electionid).filter(is_display_priority=True)


    def get_context_data(self, **kwargs):
        context = super(BakedEmbeddedDetail, self).get_context_data(**kwargs)
        context["is_homepage"] = False
        context["is_featured"] = False
        context["is_all"] = False
        context["baked"] = True
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.electionid
        context["election_meta"] = Election.objects.filter(electionid=context["electionid"]).first()
        return context


class HomepageIndex(ListView):
    model = Contest
    template_name = "ballot_box/featured_races.html"


    def get_object(self):
        object = super(HomepageIndex, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(HomepageIndex, self).get_context_data(**kwargs)
        context["is_homepage"] = True
        context["is_featured"] = False
        context["is_all"] = False
        context["baked"] = False
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.kwargs["electionid"]
        context["title"] = Election.objects.filter(electionid=context["electionid"]).first().election_title
        context["caveat"] = Election.objects.filter(electionid=context["electionid"]).first().election_caveats
        context["kpcc_page"] = Election.objects.filter(electionid=context["electionid"]).first().election_kpcc_page
        queryset = Contest.objects.filter(election__electionid=context["electionid"])
        context["featured_races"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=False)
        context["featured_measures"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=True)
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(contestid__contains="lac-county-los-angeles-countywide") |
            Q(contestid__contains="lac-county-los-angeles-city-special-municipal")
        )
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).first()
        return context


class BakedHomepageIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/featured_races.html"
    electionid = ELECTIONID
    build_path = "%s/results/homepage.html" % (electionid)


    def get_object(self):
        object = super(BakedHomepageIndex, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(BakedHomepageIndex, self).get_context_data(**kwargs)
        context["is_homepage"] = True
        context["is_featured"] = False
        context["is_all"] = False
        context["baked"] = True
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.electionid
        context["title"] = Election.objects.filter(electionid=context["electionid"]).first().election_title
        context["caveat"] = Election.objects.filter(electionid=context["electionid"]).first().election_caveats
        context["kpcc_page"] = Election.objects.filter(electionid=context["electionid"]).first().election_kpcc_page
        queryset = Contest.objects.filter(election__electionid=context["electionid"])
        context["featured_races"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=False)
        context["featured_measures"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=True)
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(contestid__contains="lac-county-los-angeles-countywide") |
            Q(contestid__contains="lac-county-los-angeles-city-special-municipal")
        )
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).first()
        return context


class FeaturedIndex(ListView):
    model = Contest
    template_name = "ballot_box/featured_races.html"


    def get_object(self):
        object = super(FeaturedIndex, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(FeaturedIndex, self).get_context_data(**kwargs)
        context["is_homepage"] = False
        context["is_featured"] = True
        context["is_all"] = False
        context["baked"] = False
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.kwargs["electionid"]
        context["title"] = Election.objects.filter(electionid=context["electionid"]).first().election_title
        context["caveat"] = Election.objects.filter(electionid=context["electionid"]).first().election_caveats
        context["kpcc_page"] = Election.objects.filter(electionid=context["electionid"]).first().election_kpcc_page
        queryset = Contest.objects.filter(election__electionid=context["electionid"])
        context["featured_races"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=False)
        context["featured_measures"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=True)
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(contestid__contains="lac-county-los-angeles-countywide") |
            Q(contestid__contains="lac-county-los-angeles-city-special-municipal")
        )
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).first()
        return context


class BakedFeaturedIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/featured_races.html"
    electionid = ELECTIONID
    build_path = "%s/results/featured.html" % (electionid)


    def get_object(self):
        object = super(BakedFeaturedIndex, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(BakedFeaturedIndex, self).get_context_data(**kwargs)
        context["is_homepage"] = False
        context["is_featured"] = True
        context["is_all"] = False
        context["baked"] = True
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.electionid
        context["title"] = Election.objects.filter(electionid=context["electionid"]).first().election_title
        context["caveat"] = Election.objects.filter(electionid=context["electionid"]).first().election_caveats
        context["kpcc_page"] = Election.objects.filter(electionid=context["electionid"]).first().election_kpcc_page
        queryset = Contest.objects.filter(election__electionid=context["electionid"])
        context["featured_races"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=False)
        context["featured_measures"] = queryset.filter(is_homepage_priority=True).filter(is_ballot_measure=True)
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(contestid__contains="lac-county-los-angeles-countywide") |
            Q(contestid__contains="lac-county-los-angeles-city-special-municipal")
        )
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).first()
        return context


class ResultIndex(ListView):
    model = Contest
    template_name = "ballot_box/all_races.html"


    def get_object(self):
        object = super(ResultIndex, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(ResultIndex, self).get_context_data(**kwargs)
        context["is_homepage"] = False
        context["is_featured"] = False
        context["is_all"] = True
        context["baked"] = False
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.kwargs["electionid"]
        context["title"] = Election.objects.filter(electionid=context["electionid"]).first().election_title
        context["caveat"] = Election.objects.filter(electionid=context["electionid"]).first().election_caveats
        context["kpcc_page"] = Election.objects.filter(electionid=context["electionid"]).first().election_kpcc_page
        queryset = Contest.objects.filter(election__electionid=context["electionid"]).filter(is_display_priority=True)
        context["national_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(contestid__contains="sos-statewide-president") |
                Q(contestid__contains="sos-statewide-us-senate") |
                Q(contestid__contains="sos-districtwide-us-house-of-representatives")
        )
        context["state_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(contestid__contains="sos-districtwide-state-senate") |
                Q(contestid__contains="sos-districtwide-state-assembly")
        )
        context["lac_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="lac")
        ).order_by("contestname")
        context["oc_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="oc")
        ).order_by("contestname")
        context["sbc_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="sbc")
        ).order_by("contestname")
        context["state_measures"] = queryset.filter(is_ballot_measure=True).filter(resultsource__source_short="sos").order_by("contestname")
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(resultsource__source_short="lac") |
            Q(resultsource__source_short="oc")|
            Q(resultsource__source_short="sbc")
        ).order_by("contestname")
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).first()
        return context


class BakedResultsIndex(BuildableListView):
    model = Contest
    template_name = "ballot_box/all_races.html"
    electionid = ELECTIONID
    build_path = "%s/results/all.html" % (electionid)


    def get_object(self):
        object = super(BakedResultsIndex, self).get_object()
        return object


    def get_context_data(self, **kwargs):
        context = super(BakedResultsIndex, self).get_context_data(**kwargs)
        context["is_homepage"] = False
        context["is_featured"] = False
        context["is_all"] = True
        context["baked"] = True
        context["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        context["electionid"] = self.electionid
        context["title"] = Election.objects.filter(electionid=context["electionid"]).first().election_title
        context["caveat"] = Election.objects.filter(electionid=context["electionid"]).first().election_caveats
        context["kpcc_page"] = Election.objects.filter(electionid=context["electionid"]).first().election_kpcc_page
        queryset = Contest.objects.filter(election__electionid=context["electionid"]).filter(is_display_priority=True)
        context["national_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(contestid__contains="sos-statewide-president") |
                Q(contestid__contains="sos-statewide-us-senate") |
                Q(contestid__contains="sos-districtwide-us-house-of-representatives")
        ).order_by("contestname")
        context["state_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(contestid__contains="sos-districtwide-state-senate") |
                Q(contestid__contains="sos-districtwide-state-assembly")
        )
        context["lac_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="lac")
        ).order_by("contestname")
        context["oc_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="oc")
        ).order_by("contestname")
        context["sbc_races"] = Contest.objects.filter(election__electionid=context["electionid"]).filter(
            is_display_priority=True).filter(is_ballot_measure=False).filter(
                Q(resultsource__source_short="sbc")
        ).order_by("contestname")
        context["state_measures"] = queryset.filter(is_ballot_measure=True).filter(resultsource__source_short="sos").order_by("contestname")
        context["local_measures"] = queryset.filter(is_ballot_measure=True).filter(
            Q(resultsource__source_short="lac") |
            Q(resultsource__source_short="oc")
        ).order_by("contestname")
        context["results_meta"] = ResultSource.objects.filter(election__electionid=context["electionid"]).first()
        return context
