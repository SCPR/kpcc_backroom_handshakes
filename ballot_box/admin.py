from __future__ import division
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


class OfficeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "officeid",
        "slug",
    )

    # list_per_page = 15

    list_filter = (
        "name",
        "officeid",
    )

    search_fields = ("name",)

    ordering = ("name",)

    save_on_top = True

    prepopulated_fields = {
        "slug": ("name",)
    }


class ContestAdmin(admin.ModelAdmin):

    def get_candidate_count(self, obj):
        return obj.candidate_set.count()

    def precincts_reporting_pct(self, obj):
        if obj.precinctsreportingpct == None:
            return 0
        else:
            return "{0:.2f}%".format(obj.precinctsreportingpct * 100)
    precincts_reporting_pct.short_description = "Precincts Reporting"

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
        # "get_candidate_count",
        "precincts_reporting_pct",
        # "votersturnout",
        "resultsource",
        "poss_error",
    )

    list_filter = (
        "resultsource",
        "poss_error",
        "is_display_priority",
        "is_homepage_priority",
        "is_ballot_measure",
        "is_judicial",
        "contestname",
    )

    list_per_page = 100

    search_fields = ("contestname",)

    ordering = (
        "-is_display_priority",
        "contestname",
        "-precinctsreportingpct",
    )

    save_on_top = True

    actions = [
        "interested_in_contest",
        "uninterested_in_contest",
        "feature_contest",
        "unfeature_contest",
        "set_possible_error",
        "remove_possible_error",
    ]

    def interested_in_contest(self, request, queryset):
        queryset.update(is_display_priority=True)
    interested_in_contest.short_description = "Interested In"

    def uninterested_in_contest(self, request, queryset):
        queryset.update(is_display_priority=False)
    uninterested_in_contest.short_description = "Uninterested In"

    def feature_contest(self, request, queryset):
        queryset.update(is_homepage_priority=True)
        queryset.update(is_display_priority=True)
    feature_contest.short_description = "Feature"

    def unfeature_contest(self, request, queryset):
        queryset.update(is_homepage_priority=False)
    unfeature_contest.short_description = "Unfeature"

    def set_possible_error(self, request, queryset):
        queryset.update(poss_error=True)
    set_possible_error.short_description = "Set Possible Error"

    def remove_possible_error(self, request, queryset):
        queryset.update(poss_error=False)
    remove_possible_error.short_description = "Remove Possible Error"


class BallotMeasureAdmin(admin.ModelAdmin):

    def yes_percent(self, obj):
        if obj.yespct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.yespct * 100)
    yes_percent.short_description = "Percent Of Yes Votes"

    def no_percent(self, obj):
        if obj.nopct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.nopct * 100)
    no_percent.short_description = "Percent Of No Votes"

    def precincts_reporting_pct(self, obj):
        if obj.contest.precinctsreportingpct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.contest.precinctsreportingpct * 100)
    precincts_reporting_pct.short_description = "Precincts Reporting"

    def get_source(self, obj):
        return obj.contest.resultsource.source_short
    get_source.short_description = "Data Source"

    list_display = (
        "fullname",
        "yescount",
        "yes_percent",
        "nocount",
        "no_percent",
        "precincts_reporting_pct",
        "get_source",
        "poss_error",
    )

    list_per_page = 15

    list_editable = (
        "yescount",
        "nocount",
    )

    list_filter = (
        "poss_error",
        "fullname",
    )

    search_fields = ("fullname",)

    ordering = (
        "-yespct",
        "-fullname",
    )

    save_on_top = True

    actions = [
        "set_possible_error",
        "remove_possible_error",
    ]

    def set_possible_error(self, request, queryset):
        queryset.update(poss_error=True)
    set_possible_error.short_description = "Set Possible Error"

    def remove_possible_error(self, request, queryset):
        queryset.update(poss_error=False)
    remove_possible_error.short_description = "Remove Possible Error"


class CandidateAdmin(admin.ModelAdmin):

    def get_source(self, obj):
        return obj.contest.resultsource.source_short
    get_source.short_description = "Data Source"

    def vote_percent(self, obj):
        if obj.votepct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.votepct * 100)
    vote_percent.short_description = "Percent Of Total Votes"

    def get_total_votes(self, obj):
        candidates = obj.contest.candidate_set.all()
        vote_total = candidates.aggregate(Sum("votecount"))["votecount__sum"]
        return vote_total
    get_total_votes.short_description = "Total Votes in Contest"

    def precincts_reporting_pct(self, obj):
        if obj.contest.precinctsreportingpct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.contest.precinctsreportingpct * 100)
    precincts_reporting_pct.short_description = "Precincts Reporting"

    list_display = (
        "fullname",
        "votecount",
        "vote_percent",
        "get_total_votes",
        "precincts_reporting_pct",
        "party",
        "contest",
        "get_source",
        "poss_error",
    )

    list_per_page = 40

    list_editable = (
        "votecount",
    )

    list_filter = (
        "poss_error",
        "party",
        "contest",
    )

    search_fields = (
        "fullname",
    )

    ordering = (
        "-contest",
        "-votepct",
        "-fullname",
    )

    save_on_top = True

    actions = [
        "set_possible_error",
        "remove_possible_error",
    ]

    def set_possible_error(self, request, queryset):
        queryset.update(poss_error=True)
    set_possible_error.short_description = "Set Possible Error"

    def remove_possible_error(self, request, queryset):
        queryset.update(poss_error=False)
    remove_possible_error.short_description = "Remove Possible Error"


class JudicialCandidateAdmin(admin.ModelAdmin):

    def yes_percent(self, obj):
        if obj.yespct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.yespct * 100)
    yes_percent.short_description = "Percent Of Yes Votes"

    def no_percent(self, obj):
        if obj.nopct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.nopct * 100)
    no_percent.short_description = "Percent Of No Votes"

    def precincts_reporting_pct(self, obj):
        if obj.contest.precinctsreportingpct == None:
            return 0
        else:
            return "{0:.1f}%".format(obj.contest.precinctsreportingpct * 100)
    precincts_reporting_pct.short_description = "Precincts Reporting"

    def get_source(self, obj):
        return obj.contest.resultsource.source_short
    get_source.short_description = "Data Source"

    list_display = (
        "fullname",
        "yescount",
        "yes_percent",
        "nocount",
        "no_percent",
        "precincts_reporting_pct",
        "get_source",
        "poss_error",
    )

    list_per_page = 15

    list_filter = (
        "poss_error",
        "fullname",
    )

    list_editable = (
        "yescount",
        "nocount",
    )

    search_fields = ("fullname",)

    ordering = (
        "contest",
        "fullname",
    )

    save_on_top = True

    actions = [
        "set_possible_error",
        "remove_possible_error",
    ]

    def set_possible_error(self, request, queryset):
        queryset.update(poss_error=True)
    set_possible_error.short_description = "Set Possible Error"

    def remove_possible_error(self, request, queryset):
        queryset.update(poss_error=False)
    remove_possible_error.short_description = "Remove Possible Error"


admin.site.register(BallotMeasure, BallotMeasureAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Contest, ContestAdmin)
admin.site.register(Election, ElectionAdmin)
admin.site.register(JudicialCandidate, JudicialCandidateAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(ResultSource, ResultSourceAdmin)
