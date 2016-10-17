from __future__ import division
from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, F
from kpcc_backroom_handshakes.custom_fields import ListField
from ballot_box.utils_data import Framer, Checker
from election_registrar import models as registrar
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

framer = Framer()
checker = Checker()

class Office(models.Model):
    """
    describes the thing that a candidate is campaigning for
    """
    name = models.CharField("Name Of The Office", max_length=255, null=False, blank=False)
    slug = models.SlugField("Slug Of The Office", db_index=True, max_length=255, null=True, blank=True)
    officeid = models.CharField("Office ID", max_length=255, null=True, blank=True)
    active = models.BooleanField("Is This Office Active?", default=False)
    poss_error = models.BooleanField("Possible Error", default=False)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Office, self).save(*args, **kwargs)


class Contest(models.Model):
    """
    describes the thing that the electorate is casting votes for
    """
    election = models.ForeignKey(registrar.Election)
    resultsource = models.ForeignKey(registrar.ResultSource)
    office = models.ForeignKey(Office)
    contestid = models.CharField("Contest ID", max_length=255, null=True, blank=True)
    contestname = models.CharField("Contest", max_length=255, null=False, blank=False)
    seatnum = models.IntegerField("Number of district or seat up for grabs", null=True, blank=True)
    contestdescription = models.TextField("Description Of This Contest", null=True, blank=True)
    is_uncontested = models.BooleanField("Uncontested Contest?", default=False)
    is_national = models.BooleanField("National Contest?", default=False)
    is_statewide = models.BooleanField("Statewide Contest?", default=False)
    is_ballot_measure = models.BooleanField("Is A Measure?", default=False)
    is_judicial = models.BooleanField("Is Judicial Contest?", default=False)
    is_runoff = models.BooleanField("Is A Runoff Contest?", default=False)
    is_display_priority = models.BooleanField("Interested In?", default=False)
    is_homepage_priority = models.BooleanField("Feature This?", default=False)
    reporttype = models.CharField("Status of Results", max_length=255, null=True, blank=True)
    precinctstotal = models.IntegerField("Total Number Of Precincts", null=True, blank=True)
    precinctsreporting = models.IntegerField("Precincts Reporting", null=True, blank=True)
    precinctsreportingpct = models.FloatField("Percent Of Precincts Reporting", null=True, blank=True)
    votersregistered = models.IntegerField("Number of Registered Voters", null=True, blank=True, default=0)
    votersturnout = models.FloatField("Percent Voters Who Cast Ballots", null=True, blank=True)
    poss_error = models.BooleanField("Possible Error", default=False)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.contestname

    def save(self, *args, **kwargs):
        # if self.pk is None and not self.contestid:
            # create self.contestid
        # elif not self.contestid:
            # create self.contestid
        super(Contest, self).save(*args, **kwargs)


# @receiver(post_save, sender=Contest)
def contest_post_save(sender, **kwargs):
    instance = kwargs.get("instance")
    created = kwargs.get("created")
    if created == False:
        if instance.precinctsreporting == instance.precinctstotal and instance.precinctsreportingpct != 1.0:
            Contest.objects.filter(id=instance.id).update(precinctsreportingpct=1.0, poss_error=True)
        else:
            precinctsreportingpct = instance.precinctsreporting / instance.precinctstotal
            Contest.objects.filter(id=instance.id).update(precinctsreportingpct=precinctsreportingpct, poss_error=False)
        poss_error = checker._return_sanity_checks(instance)
        Contest.objects.filter(id=instance.id).update(poss_error=poss_error)
post_save.connect(contest_post_save, Contest, weak=False,
                  dispatch_uid="contest_post_save")


class Candidate(models.Model):
    """
    describes a person running for office
    """
    contest = models.ForeignKey(Contest)
    candidateid = models.CharField("Candidate ID", max_length=255, null=True, blank=True)
    ballotorder = models.IntegerField("Numerical Position On The Ballot", null=True, blank=True)
    firstname = models.CharField("Candidate's First Name", max_length=255, null=True, blank=True)
    lastname = models.CharField("Candidate's Last Name", max_length=255, null=True, blank=True)
    fullname = models.CharField("Candidate's Full Name", max_length=255, null=True, blank=True)
    party = models.CharField("Political Party", max_length=255, null=True, blank=True)
    incumbent = models.BooleanField("Is Candidate An Incumbent?", default=False)
    votecount = models.IntegerField("Votes Received", null=True, blank=True)
    votepct = models.FloatField("Percent Of Total Votes", null=True, blank=True)
    poss_error = models.BooleanField("Possible Error", default=False)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        # if self.pk is None and not self.candidateid:
            # create self.candidateid
        # elif not self.candidateid:
            # create self.candidateid
        super(Candidate, self).save(*args, **kwargs)


# @receiver(post_save, sender=Candidate)
def candidate_post_save(sender, **kwargs):
    instance = kwargs.get("instance")
    created = kwargs.get("created")
    if created == False:
        candidates = instance.contest.candidate_set.all()
        tvs = candidates.aggregate(Sum("votecount"))["votecount__sum"]
        for candidate in candidates:
            if candidate.votecount == 0 and tvs == 0:
                Candidate.objects.filter(id=candidate.id).update(votepct=0, poss_error=False)
            elif framer._calc_pct(candidate.votecount, tvs):
                votepct = framer._calc_pct(candidate.votecount, tvs)
                Candidate.objects.filter(id=candidate.id).update(votepct=votepct, poss_error=False)
            else:
                Candidate.objects.filter(id=candidate.id).update(votepct=None, poss_error=True)
            poss_error = checker._return_sanity_checks(candidate, totalvotes=tvs)
            Candidate.objects.filter(id=candidate.id).update(poss_error=poss_error)
post_save.connect(candidate_post_save, Candidate, weak=False, dispatch_uid="candidate_post_save")


class BallotMeasure(models.Model):
    """
    describes a measure that can be voted on
    """
    contest = models.ForeignKey(Contest)
    measureid = models.CharField("Measure ID", max_length=255, null=False, blank=False)
    ballotorder = models.IntegerField("Numerical Position On The Ballot", null=True, blank=True)
    fullname = models.CharField("Name of Ballot Measure", max_length=255, null=False, blank=False)
    description = models.TextField("Description Of Ballot Measure", null=True, blank=True)
    yescount = models.IntegerField("Number Of Yes Votes Received", null=True, blank=True)
    yespct = models.FloatField("Percent Of Yes Votes Received", null=True, blank=True)
    nocount = models.IntegerField("Number Of No Votes Received", null=True, blank=True)
    nopct = models.FloatField("Percent Of No Votes Received", null=True, blank=True)
    poss_error = models.BooleanField("Possible Error", default=False)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        # if self.pk is None and not self.measureid:
            # create self.measureid
        # elif not self.measureid:
            # create self.measureid
        super(BallotMeasure, self).save(*args, **kwargs)


# @receiver(post_save, sender=BallotMeasure)
def measure_post_save(sender, **kwargs):
    instance = kwargs.get("instance")
    created = kwargs.get("created")
    if created == False:
        tvs = instance.yescount + instance.nocount
        if instance.yescount == 0 and instance.nocount == 0:
            BallotMeasure.objects.filter(id=instance.id).update(yespct=0, nopct=0, poss_error=False)
        elif instance.yescount > 0 and instance.nocount > 0:
            yespct = framer._calc_pct(instance.yescount, tvs)
            nopct = framer._calc_pct(instance.nocount, tvs)
            BallotMeasure.objects.filter(id=instance.id).update(yespct=yespct, nopct=nopct, poss_error=False)
        else:
            BallotMeasure.objects.filter(id=instance.id).update(yespct=None, nopct=None, poss_error=True)
        poss_error = checker._return_sanity_checks(instance, totalvotes=tvs)
        BallotMeasure.objects.filter(id=instance.id).update(poss_error=poss_error)
post_save.connect(measure_post_save, BallotMeasure, weak=False, dispatch_uid="measure_post_save")


class JudicialCandidate(models.Model):
    """
    describes a measure that can be voted on
    """
    contest = models.ForeignKey(Contest)
    judgeid = models.CharField("Judicial Candidate ID", max_length=255, null=False, blank=False)
    ballotorder = models.IntegerField("Numerical Position On The Ballot", null=True, blank=True)
    firstname = models.CharField("Candidate's First Name", max_length=255, null=True, blank=True)
    lastname = models.CharField("Candidate's Last Name", max_length=255, null=True, blank=True)
    fullname = models.CharField("Candidate's Last Name", max_length=255, null=False, blank=False)
    yescount = models.IntegerField("Number Of Yes Votes Received", null=True, blank=True)
    yespct = models.FloatField("Percent Of Yes Votes Received", null=True, blank=True)
    nocount = models.IntegerField("Number Of No Votes Received", null=True, blank=True)
    nopct = models.FloatField("Percent Of No Votes Received", null=True, blank=True)
    poss_error = models.BooleanField("Possible Error", default=False)
    created = models.DateTimeField("Date Created", auto_now_add=True)
    modified = models.DateTimeField("Date Modified", auto_now=True)

    def __unicode__(self):
        return self.fullname

    def save(self, *args, **kwargs):
        # if self.pk is None and not self.judgeid:
            # create self.judgeid
        # elif not self.judgeid:
            # create self.judgeid
        super(JudicialCandidate, self).save(*args, **kwargs)


# @receiver(post_save, sender=JudicialCandidate)
def judicial_post_save(sender, **kwargs):
    instance = kwargs.get("instance")
    created = kwargs.get("created")
    if created == False:
        tvs = instance.yescount + instance.nocount
        if instance.yescount == 0 and instance.nocount == 0:
            JudicialCandidate.objects.filter(id=instance.id).update(yespct=0, nopct=0, poss_error=False)
        elif instance.yescount > 0 and instance.nocount > 0:
            yespct = framer._calc_pct(instance.yescount, tvs)
            nopct = framer._calc_pct(instance.nocount, tvs)
            JudicialCandidate.objects.filter(id=instance.id).update(yespct=yespct, nopct=nopct, poss_error=False)
        else:
            JudicialCandidate.objects.filter(id=instance.id).update(yespct=None, nopct=None, poss_error=True)
        poss_error = checker._return_sanity_checks(instance, totalvotes=tvs)
        JudicialCandidate.objects.filter(id=instance.id).update(poss_error=poss_error)
post_save.connect(judicial_post_save, JudicialCandidate, weak=False, dispatch_uid="judicial_post_save")
