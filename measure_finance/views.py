import os
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from django.db.models import Q, Avg, Max, Min, Sum, Count
from measure_finance.models import Measure, MeasureContributor, MeasureTotal
from bakery.views import BuildableListView, BuildableDetailView
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

class InitialListView(BuildableListView):
    """ """
    model = Measure
    template_name = "measure_finance/index.html"

@method_decorator(xframe_options_exempt, name='get_object')
class InitialDetailView(BuildableDetailView):
    """ """
    model = Measure
    template_name = "measure_finance/detail.html"
    slug_field = "official_identifier_slug"
    sub_directory = "measure-finance/"

    def get_object(self):
        object = super(InitialDetailView, self).get_object()
        return object

    def get_url(self, obj):
        """
        the url at which the detail page should appear.
        """
        return "/%s" % (obj.official_identifier_slug)

    def get_build_path(self, obj):
        """
        used to determine where to build the detail page. override this if you
        would like your detail page at a different location. by default it
        will be built at get_url() + "index.html"
        """
        path = os.path.join(settings.BUILD_DIR, self.sub_directory, self.get_url(obj)[1:])
        os.path.exists(path) or os.makedirs(path)
        return os.path.join(path, "index.html")

    def get_context_data(self, **kwargs):
        context = super(InitialDetailView, self).get_context_data(**kwargs)
        aggregate_contribs = MeasureTotal.objects.filter(measure_id=self.object.id)
        context["total_support"] = aggregate_contribs.filter(support="Yes").first()
        if context["total_support"]:
            context["support_unitemized"] = context["total_support"].total_unitemized
        else:
            context["support_unitemized"] = None
        if context["total_support"]:
            context["support_itemized"] = context["total_support"].total_itemized
        else:
            context["support_itemized"] = None
        if context["total_support"] == None:
            context["total_support"] = 0
        else:
            context["total_support"] = context["total_support"].total_amount
        context["total_opposition"] = aggregate_contribs.filter(support="No").first()
        if context["total_opposition"]:
            context["opposition_unitemized"] = context["total_opposition"].total_unitemized
        else:
            context["opposition_unitemized"] = None
        if context["total_opposition"]:
            context["opposition_itemized"] = context["total_opposition"].total_itemized
        else:
            context["opposition_itemized"] = None
        if context["total_opposition"] == None:
            context["total_opposition"] = 0
        else:
            context["total_opposition"] = context["total_opposition"].total_amount
        context["total_contributions"] = context["total_support"] + context["total_opposition"]
        support_percent = round((context["total_support"] / context["total_contributions"]) * 100, 2)
        oppose_percent = round((context["total_opposition"] / context["total_contributions"]) * 100, 2)
        if support_percent > oppose_percent:
            start_angle = -90
            end_angle = 90
        elif support_percent < oppose_percent:
            start_angle = 90
            end_angle = -90
        context["chart_config"] = {
            "support_percent": support_percent,
            "oppose_percent": oppose_percent,
            "start_angle": start_angle,
            "end_angle": end_angle,
        }
        individual_contribs = MeasureContributor.objects.filter(measure_id=self.object.id)
        context["supporting_contributions"] = individual_contribs.values("name").filter(support="Yes", top_type="D").annotate(total=Sum("total_amount")).order_by("-total")[0:5]
        context["opposing_contributions"] = individual_contribs.values("name").filter(support="No", top_type="D").annotate(total=Sum("total_amount")).order_by("-total")[0:5]
        return context
