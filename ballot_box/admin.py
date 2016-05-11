from django.conf import settings
from django.contrib import admin
from ballot_box.models import *
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class BallotMeasureAdmin(admin.ModelAdmin):
    save_on_top = True


class CandidateAdmin(admin.ModelAdmin):
    save_on_top = True


class ContestAdmin(admin.ModelAdmin):
    save_on_top = True


class ElectionAdmin(admin.ModelAdmin):
    list_display = ("type", "election_date", "test_results", "live_results")
    list_per_page = 15
    # list_filter = ["source_name"]
    # ordering = ["source_name"]
    save_on_top = True


class JudicialCandidateAdmin(admin.ModelAdmin):
    save_on_top = True


class OfficeAdmin(admin.ModelAdmin):
    save_on_top = True
    prepopulated_fields = {
        "slug": ("name",)
    }


class ReportingUnitAdmin(admin.ModelAdmin):
    save_on_top = True
    prepopulated_fields = {
        "reportingunitslug": ("reportingunitname",)
    }


class ResultSourceAdmin(admin.ModelAdmin):
    list_display = ("source_name", "source_active", "source_created")
    list_per_page = 15
    list_filter = ["source_name"]
    ordering = ["source_name"]
    save_on_top = True
    prepopulated_fields = {
        "source_slug": ("source_name",)
    }


admin.site.register(BallotMeasure, BallotMeasureAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(JudicialCandidate, JudicialCandidateAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(ReportingUnit, ReportingUnitAdmin)
admin.site.register(ResultSource, ResultSourceAdmin)
