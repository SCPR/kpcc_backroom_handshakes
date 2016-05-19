from django.conf import settings
from django.contrib import admin
from ballot_box.models import *
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class CandidateInline(admin.StackedInline):
    model = Candidate
    extra = 0


class BallotMeasureAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource
    get_source.short_description = "Data Source"
    get_source.admin_order_field = "contest__resultsource"

    def precincts_reporting_pct(self, obj):
        return obj.contest.precinctsreportingpct
    precincts_reporting_pct.short_description = "Precincts Reporting"
    precincts_reporting_pct.admin_order_field = 'candidate__contest'

    list_display = (
        "fullname",
        "yespct",
        "nopct",
        "precincts_reporting_pct",
        "get_source",
    )

    list_filter = ("fullname",)

    search_fields = ("fullname",)

    ordering = ("fullname",)

    save_on_top = True


class CandidateAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource
    get_source.short_description = "Data Source"
    get_source.admin_order_field = "contest__resultsource"

    def precincts_reporting_pct(self, obj):
        return obj.contest.precinctsreportingpct
    precincts_reporting_pct.short_description = "Pct Precincts Reporting"
    precincts_reporting_pct.admin_order_field = "contest__candidate"

    list_display = (
        "fullname",
        "votecount",
        "votepct",
        "precincts_reporting_pct",
        "party",
        "contest",
        "get_source",
    )

    list_editable = (
        "votecount",
        "votepct",
        # "precincts_reporting_pct",
    )

    list_filter = ("contest",)

    search_fields = ("fullname",)

    ordering = (
        "contest",
        "fullname",
    )

    save_on_top = True


class ContestAdmin(admin.ModelAdmin):

    def get_candidate_count(self, obj):
        return obj.candidate_set.count()

    get_candidate_count.short_description = "Number of Candidates"
    get_candidate_count.admin_order_field = "candidate__contest"

    list_display = (
        "contestname",
        "is_display_priority",
        "is_homepage_priority",
        "get_candidate_count",
        "precinctsreporting",
        "votersturnout",
        "resultsource",
    )

    list_filter = (
        "contestname",
        "is_display_priority",
        "is_homepage_priority"
    )

    search_fields = ("contestname",)

    ordering = (
        "contestname",
        "is_display_priority",
    )

    save_on_top = True

    inlines = (CandidateInline,)


class ElectionAdmin(admin.ModelAdmin):

    def get_contest_count(self, obj):
        return obj.contest_set.count()
    get_contest_count.short_description = "Number of Races"
    get_contest_count.admin_order_field = "contest__election"

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


class JudicialCandidateAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource
    get_source.short_description = "Data Source"
    get_source.admin_order_field = "contest__resultsource"

    def precincts_reporting_pct(self, obj):
        return obj.contest.precinctsreportingpct
    precincts_reporting_pct.short_description = "Precincts Reporting"
    precincts_reporting_pct.admin_order_field = "judicialcandidate__contest"

    list_display = (
        "fullname",
        "yespct",
        "nopct",
        "precincts_reporting_pct",
        "get_source",
    )

    list_filter = ("fullname",)

    search_fields = ("fullname",)

    ordering = (
        "contest",
        "fullname",
    )

    save_on_top = True


class OfficeAdmin(admin.ModelAdmin):

    list_filter = ("name",)

    search_fields = ("name",)

    ordering = ("name",)

    save_on_top = True

    prepopulated_fields = {
        "slug": ("name",)
    }


# class ReportingUnitAdmin(admin.ModelAdmin):
#     save_on_top = True
#     prepopulated_fields = {
#         "reportingunitslug": ("reportingunitname",)
#     }


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

    prepopulated_fields = {
        "source_slug": ("source_name",)
    }


admin.site.register(BallotMeasure, BallotMeasureAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(JudicialCandidate, JudicialCandidateAdmin)
admin.site.register(Office, OfficeAdmin)
# admin.site.register(ReportingUnit, ReportingUnitAdmin)
admin.site.register(ResultSource, ResultSourceAdmin)
