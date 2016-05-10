from __future__ import unicode_literals
from django.db import models
from kpcc_backroom_handshakes.custom_fields import ListField


class Election(models.Model):
    """
    describes an election that will have results we want to capture
    """
    PRIMARY = "Primary"
    GENERAL = "General"
    SPECIAL = "Special"

    ELECTION_TYPE_CHOICES = (
        (PRIMARY, "Primary"),
        (GENERAL, "General"),
        (SPECIAL, "Special"),
    )

    type = models.CharField(
        "Type of Election",
        max_length=255,
        choices=ELECTION_TYPE_CHOICES,
        default=PRIMARY,
    )

    electionid = models.CharField(
        "Election ID", max_length=255, null=True, blank=True)
    test_results = models.BooleanField("Are These Test Results", default=False)
    live_results = models.BooleanField("Are These Live Results", default=False)
    election_date = models.DateField(
        "Date of the Election", null=True, blank=True)
    poll_close_at = models.DateTimeField(
        "Time the Polls Close", null=True, blank=True)
    national = models.BooleanField(
        "Is this a National Election?", default=False)
    # parsed_json
    # next_request
    # datafile
    # results_level
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.electionid

    def save(self, *args, **kwargs):
        if not self.electionid:
            self.election_date_str = self.election_date.strftime("%Y-%m-%d")
            self.electionid = "%s-%s" % (self.type.lower(),
                                         self.election_date_str)
        super(Election, self).save(*args, **kwargs)


class ResultSource(models.Model):
    """
    describes a source of data for election results
    """
    election = models.ForeignKey(Election)
    source_name = models.CharField(
        "Name Of Data Source", db_index=True, unique=True, max_length=255)
    source_short = models.CharField("Shortname Of Data Source", max_length=5)
    source_slug = models.SlugField(
        "Slugged Data Soure", db_index=True, unique=True, max_length=255, null=True, blank=True)
    source_url = models.URLField(
        "Url To Data Source", max_length=1024, null=True, blank=True)
    source_active = models.BooleanField("Active Data Source?", default=False)
    source_type = models.CharField(
        "Ext Of File Or Type Of Source", max_length=255, null=False, blank=False)
    source_files = ListField("Results Files We Want", null=True, blank=True)
    source_created = models.DateTimeField("Date Created", auto_now_add=True)
    source_modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.source_name

    def save(self, *args, **kwargs):
        super(ResultSource, self).save(*args, **kwargs)

