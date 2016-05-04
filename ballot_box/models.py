from __future__ import unicode_literals
from django.db import models
import logging

class ResultSource(models.Model):
    """
    describes a source of data for election results
    """
    source_name = models.CharField("Name of data source", db_index=True, unique=True, max_length=255)
    source_short = models.CharField("Shortname of data source", max_length=5)
    source_slug = models.SlugField("Slugged data soure", db_index=True, unique=True, max_length=255, null=True, blank=True)
    source_url = models.URLField("URL to data source", max_length=1024, null=True, blank=True)
    source_election_date = models.DateTimeField("Date of election for this source", null=True, blank=True)
    source_active = models.BooleanField("Active data source?", default=False)
    source_type = models.CharField("Ext of file or type of source", max_length=255, null=False, blank=False)
    source_created = models.DateTimeField("Date Created", auto_now_add=True)
    source_modified = models.DateTimeField("Date Modified", auto_now=True)


    def __unicode__(self):
        return self.source_name


    def save(self, *args, **kwargs):
        super(ResultSource, self).save(*args, **kwargs)
