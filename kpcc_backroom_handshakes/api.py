from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.authentication import ApiKeyAuthentication
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.serializers import Serializer
from tastypie.cache import SimpleCache
from ballot_box.models import Contest, Candidate, BallotMeasure, JudicialCandidate


class CandidateResource(ModelResource):

    class Meta:
        queryset = Candidate.objects.all()
        resource_name = "candidates"
        fields = [
            "contest.contestname",
            "candidateid",
            "ballotorder",
            "firstname",
            "lastname",
            "fullname",
            "party",
            "incumbent",
            "votecount",
            "votepct",
            "poss_error",
            "created",
            "modified",
        ]
        # filtering = {
        #     "calculated_id": ALL,
        # }
        allowed_methods = ["get"]
        serializer = Serializer(formats=["json"])
        limit = 275
        cache = SimpleCache(cache_name="default")
        # authentication = ApiKeyAuthentication()


class MeasureResource(ModelResource):

    class Meta:
        queryset = BallotMeasure.objects.all()
        resource_name = "measures"
        fields = [
            "fullname",
            "yescount",
            "yespct",
            "nocount",
            "nopct",
            "poss_error",
            "created",
            "modified",
        ]
        # filtering = {
        #     "calculated_id": ALL,
        # }
        allowed_methods = ["get"]
        serializer = Serializer(formats=["json"])
        limit = 275
        cache = SimpleCache(cache_name="default")
        # authentication = ApiKeyAuthentication()


class JudicialResource(ModelResource):

    class Meta:
        queryset = JudicialCandidate.objects.all()
        resource_name = "judicial-candidates"
        fields = [
            "fullname",
            "yescount",
            "yespct",
            "nocount",
            "nopct",
            "poss_error",
            "created",
            "modified",
        ]
        # filtering = {
        #     "calculated_id": ALL,
        # }
        allowed_methods = ["get"]
        serializer = Serializer(formats=["json"])
        limit = 275
        cache = SimpleCache(cache_name="default")
        # authentication = ApiKeyAuthentication()


class ContestResource(ModelResource):
    candidates = fields.ToManyField(
        "kpcc_backroom_handshakes.api.CandidateResource", "candidate_set", full=True)
    measures = fields.ToManyField(
        "kpcc_backroom_handshakes.api.MeasureResource", "ballotmeasure_set", full=True)
    judicial_candidates = fields.ToManyField(
        "kpcc_backroom_handshakes.api.JudicialResource", "judicialcandidate_set", full=True)

    class Meta:
        queryset = Contest.objects.filter(is_display_priority=True)
        resource_name = "contests"
        fields = [
            "contestid",
            "contestname",
            "seatnum",
            "contestdescription",
            "is_uncontested",
            "is_national",
            "is_statewide",
            "is_ballot_measure",
            "is_judicial",
            "is_runoff",
            "is_display_priority",
            "is_homepage_priority",
            "reporttype",
            "precinctstotal",
            "precinctsreporting",
            "precinctsreportingpct",
            "votersregistered",
            "votersturnout",
            "poss_error",
            "modified",
        ]
        # filtering = {
        #     "calculated_id": ALL,
        # }
        allowed_methods = ["get"]
        serializer = Serializer(formats=["json"])
        limit = 275
        cache = SimpleCache(cache_name="default")
        # authentication = ApiKeyAuthentication()
