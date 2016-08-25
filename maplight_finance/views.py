import os
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response, render
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.core.urlresolvers import reverse
from django.core import serializers
from django.template import RequestContext, Context, loader
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
from django.db.models import Q, Avg, Max, Min, Sum, Count
from maplight_finance.models import Measure, MeasureContributor, MeasureTotal
from bakery.views import BuildableListView, BuildableDetailView
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

# Create your views here.
@xframe_options_sameorigin
def index(request):
    contributions = MeasureContributor.objects.all()
    supporting_contributions = MeasureTotal.objects.filter(support="Yes")
    opposing_contributions = MeasureTotal.objects.filter(support="No")
    logger.debug(opposing_contributions)


    # total_sum = contributions.values("initiative_identifier").annotate(total=Sum("amount"))
    # supporting_sum = supporting_contributions.values("initiative_identifier").annotate(total=Sum("amount"))
    # opposing_sum = opposing_contributions.values("initiative_identifier").annotate(total=Sum("amount"))
    # return render_to_response("maplight_finance/index.html", {
    #     "total_sum": total_sum,
    #     "supporting_sum": supporting_sum,
    #     "opposing_sum": opposing_sum
    # })


# class InitialListView(BuildableListView):
    """ """
    # build_path = "maplight-finance/index.html"
    # model = Initiative
    #queryset = InitiativeContributor.objects.values("initiative_identifier").annotate(total=Sum("amount"))
    # template_name = "maplight_finance/index.html"


class InitialDetailView(BuildableDetailView):
    """ """
    model = Measure
    template_name = "maplight_finance/detail.html"
    build_path = "maplight-finance/charts/index.html"
    slug_field = "official_identifier_slug"
    sub_directory = "region/"

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
        context["last_updated"] = aggregate_contribs.first().finance_timestamp
        context["total_support"] = aggregate_contribs.filter(support="Yes").first()
        if context["total_support"] == None:
            context["total_support"] = 0
        else:
            context["total_support"] = context["total_support"].total_amount
        context["total_opposition"] = aggregate_contribs.filter(support="No").first()
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
