from django.conf import settings
from django.contrib import admin
from ballot_box.models import *
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")


class CandidateInline(admin.TabularInline):

    model = Candidate
    extra = 0
    fields = (
        "party",
        "votecount",
        "votepct",
        "incumbent",
    )

class JudicialInline(admin.TabularInline):
    model = JudicialCandidate
    extra = 0
    fields = (
        "yescount",
        "yespct",
        "nocount",
        "nopct",
    )

class MeasureInline(admin.TabularInline):
    model = BallotMeasure
    extra = 0
    fields = (
        "yescount",
        "yespct",
        "nocount",
        "nopct",
    )

class BallotMeasureAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource.source_short
    get_source.short_description = "Data Source"

    def get_contest(self, obj):
        return obj.contest.contestname
    get_contest.short_description = "Contest"

    def precincts_reporting_pct(self, obj):
        return obj.contest.precinctsreportingpct
    precincts_reporting_pct.short_description = "Precincts Reporting"
    # precincts_reporting_pct.admin_order_field = 'candidate__contest'

    list_display = (
        "fullname",
        "yespct",
        "nopct",
        "precincts_reporting_pct",
        "get_contest",
        "get_source",
    )

    list_per_page = 15

    list_filter = ("fullname",)

    search_fields = ("fullname",)

    ordering = ("fullname",)

    save_on_top = True


class CandidateAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource.source_short
    get_source.short_description = "Data Source"

    def get_contest(self, obj):
        return obj.contest.contestname
    get_contest.short_description = "Contest"

    def get_total_votes(self, obj):
        candidates = obj.contest.candidate_set.all()
        vote_total = candidates.aggregate(Sum("votecount"))["votecount__sum"]
        return vote_total
    get_total_votes.short_description = "Total Votes in Contest"

    def precincts_reporting_pct(self, obj):
        return obj.contest.precinctsreportingpct
    precincts_reporting_pct.short_description = "Pct Precincts Reporting"

    list_display = (
        "fullname",
        "votecount",
        "votepct",
        "get_total_votes",
        "precincts_reporting_pct",
        "party",
        "contest",
        "get_contest",
        "get_source",
    )

    list_per_page = 15

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

    inlines = [JudicialInline, CandidateInline, MeasureInline]

    def get_inline_instances(self, request, obj=None):
        if obj and obj.is_judicial == True:
            inlines = [JudicialInline]
        elif obj and obj.is_ballot_measure == True:
            inlines = [MeasureInline]
        else:
            inlines = [CandidateInline]
        return [inline(self.model, self.admin_site) for inline in inlines]

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
        "is_display_priority",
        "is_homepage_priority",
        "is_ballot_measure",
        "contestname",
    )

    list_per_page = 15

    search_fields = ("contestname",)

    ordering = (
        "contestname",
        "is_display_priority",
    )

    save_on_top = True


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


class JudicialCandidateAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource.source_short
    get_source.short_description = "Data Source"

    def get_contest(self, obj):
        return obj.contest.contestname
    get_contest.short_description = "Contest"

    def get_total_votes(self, obj):
        candidates = obj.contest.candidate_set.all()
        vote_total = candidates.aggregate(Sum("votecount"))["votecount__sum"]
        return vote_total
    get_total_votes.short_description = "Total Votes in Contest"

    def precincts_reporting_pct(self, obj):
        return obj.contest.precinctsreportingpct
    precincts_reporting_pct.short_description = "Precincts Reporting"

    list_display = (
        "fullname",
        "yespct",
        "nopct",
        "get_total_votes",
        "precincts_reporting_pct",
        "get_contest",
        "get_source",
    )

    list_per_page = 15

    list_filter = ("fullname",)

    search_fields = ("fullname",)

    ordering = (
        "contest",
        "fullname",
    )

    save_on_top = True


class OfficeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    list_per_page = 15

    list_filter = ("name",)

    search_fields = ("name",)

    ordering = ("name",)

    save_on_top = True

    prepopulated_fields = {
        "slug": ("name",)
    }


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
admin.site.register(ResultSource, ResultSourceAdmin)
