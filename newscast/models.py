from __future__ import division
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, F
from kpcc_backroom_handshakes.custom_fields import ListField
from ballot_box.utils_data import Framer, Checker
from election_registrar import models as registrar
from ballot_box import models as ballot_box
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

framer = Framer()
checker = Checker()

# Create your models here.
class Topic(models.Model):
    election = models.ForeignKey(registrar.Election)
    contest = models.ManyToManyField(ballot_box.Contest)
    topicname = models.CharField("Topic Name", db_index=True, unique=True, max_length=255, null=True, blank=True)
    topicslug = models.SlugField("Topic Slug", db_index=True, unique=True, max_length=255, null=True, blank=True)
    description = models.TextField("About This Topic", null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.topicname

    def save(self, *args, **kwargs):
        super(Topic, self).save(*args, **kwargs)


class ContestContext(models.Model):
    election = models.ForeignKey(registrar.Election)
    local_interest = models.BooleanField("We're Interested In This?", default=False)
    contestid = models.CharField("Contest ID", max_length=255, null=True, blank=True)
    cities_counties_list = ListField("Cities and Counties", null=True, blank=True)
    description = models.TextField("About This Contest", null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.contestid

    def save(self, *args, **kwargs):
        super(ContestContext, self).save(*args, **kwargs)


class CompareTurnout(models.Model):
    election = models.ForeignKey(registrar.Election)
    scope = models.CharField("State or the County", max_length=255, null=True, blank=True)
    election_type = models.CharField("Election Type", max_length=255, null=True, blank=True)
    formal_date = models.DateField("Election Date", auto_now_add=True)
    year = models.IntegerField("Election Year", null=True, blank=True)
    registered_voters = models.IntegerField("Registered Voters", null=True, blank=True)
    ballots_cast = models.IntegerField("Ballots Cast", null=True, blank=True)
    turnout = models.FloatField("Turnout", null=True, blank=True)
    vote_by_mail_ballots = models.IntegerField("Vote By Mail Ballots", null=True, blank=True)
    vote_by_mail_percent = models.FloatField("Vote By Mail Percent", null=True, blank=True)
    data_source = models.URLField("URL To Turnout Data", max_length=1024, null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return "%s %s" % (self.election_type, self.year)

    def save(self, *args, **kwargs):
        super(CompareTurnout, self).save(*args, **kwargs)


class DataNugget(models.Model):
    election = models.ForeignKey(registrar.Election)
    scope = models.CharField("State or the County the nugget came from", max_length=255, null=True, blank=True)
    nugget_text = models.TextField("Latest Update", null=True, blank=True)
    nugget_date = models.DateField("Date of this Information")
    nugget_source = models.CharField("Name of the Sources", max_length=255, null=True, blank=True)
    nugget_link = models.URLField("URL To Source", max_length=1024, null=True, blank=True)
    nugget_tags = ListField("Topic Tags", null=True, blank=True)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.nugget_source

    def save(self, *args, **kwargs):
        super(DataNugget, self).save(*args, **kwargs)
