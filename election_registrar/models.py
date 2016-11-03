from django.db import models
from kpcc_backroom_handshakes.custom_fields import ListField
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

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

    electionid = models.CharField("Election ID", max_length=255, null=True, blank=True)
    test_results = models.BooleanField("Are These Test Results", default=False)
    live_results = models.BooleanField("Are These Live Results", default=False)
    election_date = models.DateField("Date of the Election", null=True, blank=True)
    poll_close_at = models.DateTimeField("Time Polls Close", null=True, blank=True)
    election_caveats = models.TextField("Audience-facing display of election status", null=True, blank=True)
    national = models.BooleanField("Is National Election?", default=False)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.electionid

    def save(self, *args, **kwargs):
        # if self.pk is None and not self.electionid:
            # create self.electionid
        # elif not self.electionid:
            # create self.electionid
        super(Election, self).save(*args, **kwargs)


class ResultSource(models.Model):
    """
    describes a source of data for election results
    """
    election = models.ForeignKey(Election)
    source_name = models.CharField("Data Source Name", db_index=True, unique=True, max_length=255)
    source_short = models.CharField("Data Source Shortname", max_length=5)
    source_slug = models.SlugField("Slugged Data Source", db_index=True, unique=True, max_length=255, null=True, blank=True)
    source_url = models.URLField("Url To Data Source", max_length=1024, null=True, blank=True)
    source_active = models.BooleanField("Active Data Source?", default=False)
    source_type = models.CharField("Ext Of File Or Type Of Source", max_length=255, null=False, blank=False)
    source_files = ListField("Results Files We Want", null=True, blank=True)
    source_latest = models.DateTimeField("Latest Results From", null=True, blank=True)
    ready_to_build = models.BooleanField("Build This Source", default=False)
    source_created = models.DateTimeField("Date Created", auto_now_add=True)
    source_modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.source_name

    def save(self, *args, **kwargs):
        super(ResultSource, self).save(*args, **kwargs)
