from django.conf import settings
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.shortcuts import get_object_or_404
from election_registrar import models as registrar
import logging
import time
import datetime

logger = logging.getLogger("kpcc_backroom_handshakes")


class Measure(models.Model):
    election = models.ForeignKey(registrar.Election, null=True)
    measure_id = models.IntegerField("", null=True, blank=True)
    official_identifier =  models.CharField("official_identifier", max_length=255, null=True, blank=True)
    official_identifier_slug = models.SlugField("official_identifier_slug", max_length=140, null=True, blank=True)
    topic = models.CharField("", max_length=255, null=True, blank=True)
    official_title = models.CharField("", max_length=255, null=True, blank=True)
    official_short_summary = models.TextField(" ", null=True, blank=True)
    official_summary = models.TextField(" ", null=True, blank=True)
    official_summary_author = models.CharField("", max_length=255, null=True, blank=True)
    official_yes_vote_means = models.TextField(" ", null=True, blank=True)
    official_no_vote_means = models.TextField(" ", null=True, blank=True)
    official_vote_means_source = models.CharField("", max_length=255, null=True, blank=True)
    official_financial_effect = models.TextField(" ", null=True, blank=True)
    official_financial_effect_author = models.CharField("", max_length=255, null=True, blank=True)
    official_impartial_analysis = models.TextField(" ", null=True, blank=True)
    official_impartial_analysis_author = models.CharField("", max_length=255, null=True, blank=True)
    # official_background = models.TextField(" ", null=True, blank=True)
    # official_background_author = models.CharField("", max_length=255, null=True, blank=True)
    official_tax_rate = models.CharField("", max_length=255, null=True, blank=True)
    official_tax_rate_author = models.CharField("", max_length=255, null=True, blank=True)
    official_short_arguments_yes = models.TextField(" ", null=True, blank=True)
    official_short_arguments_no = models.TextField(" ", null=True, blank=True)
    official_short_arguments_source = models.CharField("", max_length=255, null=True, blank=True)
    # official_arguments_yes = models.TextField(" ", null=True, blank=True)
    # official_arguments_no = models.TextField(" ", null=True, blank=True)
    # official_arguments_source = models.CharField("", max_length=255, null=True, blank=True)
    official_rebuttal_yes = models.TextField(" ", null=True, blank=True)
    official_rebuttal_no = models.TextField(" ", null=True, blank=True)
    measure_type = models.CharField("", max_length=255, null=True, blank=True)
    passage_requirements = models.CharField("", max_length=255, null=True, blank=True)
    fulltext_link = models.URLField("fulltext_link", max_length=1024, null=True, blank=True)
    # full_text = models.TextField(" ", null=True, blank=True)
    # simplified_title = models.CharField("", max_length=255, null=True, blank=True)
    # way_it_is = models.TextField(" ", null=True, blank=True)
    # what_if_pass = models.TextField(" ", null=True, blank=True)
    # budget_effect = models.TextField(" ", null=True, blank=True)
    # people_for_say = models.TextField(" ", null=True, blank=True)
    # people_against_say = models.TextField(" ", null=True, blank=True)
    # evg_source = models.CharField("", max_length=255, null=True, blank=True)
    # lwv_question = models.TextField(" ", null=True, blank=True)
    # lwv_situation = models.TextField(" ", null=True, blank=True)
    # lwv_proposal = models.TextField(" ", null=True, blank=True)
    # lwv_fiscal_effects = models.TextField(" ", null=True, blank=True)
    # lwv_supporters_say = models.TextField(" ", null=True, blank=True)
    # lwv_opponents_say = models.TextField(" ", null=True, blank=True)
    # lwv_source = models.CharField("", max_length=255, null=True, blank=True)
    # status = models.CharField("", max_length=255, null=True, blank=True)
    # votes_for = models.CharField("", max_length=255, null=True, blank=True)
    # votes_against = models.CharField("", max_length=255, null=True, blank=True)
    # weight = models.CharField("", max_length=255, null=True, blank=True)
    published = models.CharField("", max_length=255, null=True, blank=True)
    disable_finance_data = models.CharField("", max_length=255, null=True, blank=True)
    deleted = models.CharField("", max_length=255, null=True, blank=True)
    entity_type = models.CharField("", max_length=255, null=True, blank=True)
    measure_timestamp = models.DateTimeField("", null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.official_identifier

    def get_absolute_url(self):
        return ("measure-detail")

class MeasureContributor(models.Model):
    measure = models.ForeignKey(Measure)
    finance_top_id = models.IntegerField("", null=True, blank=True)
    top_type = models.CharField("", max_length=255, null=True, blank=True)
    support = models.CharField("", max_length=255, null=True, blank=True)
    name = models.CharField("", max_length=255, null=True, blank=True)
    total_amount = models.FloatField("", null=True, blank=True)
    total_individual = models.FloatField("", null=True, blank=True)
    total_organization = models.FloatField("", null=True, blank=True)
    percentage_total = models.FloatField("", null=True, blank=True)
    percentage_individual = models.FloatField("", null=True, blank=True)
    percentage_organization = models.FloatField("", null=True, blank=True)
    updated_date = models.DateField("", null=True, blank=True)
    entity_type = models.IntegerField("", null=True, blank=True)
    finance_top_timestamp = models.DateTimeField("", null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.name


class MeasureTotal(models.Model):
    measure = models.ForeignKey(Measure)
    finance_id = models.IntegerField("", null=True, blank=True)
    support = models.CharField("", max_length=255, null=True, blank=True)
    total_amount = models.FloatField("", null=True, blank=True)
    total_individual = models.FloatField("", null=True, blank=True)
    total_unitemized = models.FloatField("", null=True, blank=True)
    total_itemized = models.FloatField("", null=True, blank=True)
    total_organization = models.FloatField("", null=True, blank=True)
    percentage_individual = models.FloatField("", null=True, blank=True)
    percentage_organization = models.FloatField("", null=True, blank=True)
    percentage_unitemized = models.FloatField("", null=True, blank=True)
    percentage_itemized = models.FloatField("", null=True, blank=True)
    updated_date = models.DateField("", null=True, blank=True)
    entity_type = models.IntegerField("", null=True, blank=True)
    finance_timestamp = models.DateTimeField("", null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.support
