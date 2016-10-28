from __future__ import division
from django.conf import settings
from django.contrib import admin
from django import forms
from ballot_box.models import *
from newscast.models import *
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

class ContestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContestForm, self).__init__(*args, **kwargs)
        contests = Contest.objects.filter(election__electionid="general-2016-11-08").filter(is_display_priority=True)
        w = self.fields['contest'].widget
        choices = []
        for item in contests:
            choices.append((item.id, item.contestname))
        w.choices = choices


class TopicAdmin(admin.ModelAdmin):

    list_display = (
        "topicname",
        "election",
        "created",
    )

    list_per_page = 15

    list_filter = ("topicname",)

    ordering = ("topicname",)

    save_on_top = True

    save_as = True

    filter_horizontal = ("contest",)

    form = ContestForm

    prepopulated_fields = {
        "topicslug": ("topicname",)
    }

    fields = (
        "election",
        "contest",
        "topicname",
        "topicslug",
        "description",
    )

admin.site.register(Topic, TopicAdmin)
