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
from newscast.models import *
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
        context["topic_contests"] = Topic.objects.filter(topicslug=context["topicslug"])
        return context
