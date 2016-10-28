from __future__ import division
from django.conf import settings
from django.contrib import admin
from election_registrar.models import *
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class ElectionAdmin(admin.ModelAdmin):

    def get_contest_count(self, obj):
        return obj.contest_set.count()
    get_contest_count.short_description = "Number of Races"

    list_display = (
        "type",
        "election_date",
        "get_contest_count",
        "test_results",
        "live_results"
    )

    list_per_page = 15

    list_filter = ("election_date",)

    ordering = ("election_date",)

    save_on_top = True

    save_as = True

    prepopulated_fields = {
        "electionid": ("type", "election_date",)
    }

    fields = (
        "type",
        "election_date",
        "electionid",
        "poll_close_at",
        "election_caveats",
        "test_results",
        "live_results",
        "national",
    )


class ResultSourceAdmin(admin.ModelAdmin):
    list_display = (
        "source_name",
        "source_active",
        "source_created"
    )

    list_per_page = 15

    list_filter = ("source_name",)

    ordering = ("source_name",)

    save_on_top = True

    save_as = True

    prepopulated_fields = {
        "source_slug": ("source_name",)
    }

    actions = [
        "set_active",
        "set_not_active",
    ]

    def set_active(self, request, queryset):
        queryset.update(source_active=True)
    set_active.short_description = "Activate Source"

    def set_not_active(self, request, queryset):
        queryset.update(source_active=False)
    set_not_active.short_description = "Deactivate Source"

admin.site.register(Election, ElectionAdmin)
admin.site.register(ResultSource, ResultSourceAdmin)
