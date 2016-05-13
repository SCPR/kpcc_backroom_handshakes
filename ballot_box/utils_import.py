#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from ballot_box.models import *
import logging
import time
import datetime
import os.path
import shutil

logger = logging.getLogger("kpcc_backroom_handshakes")


class Saver(object):
    """
    """

    def make_office(self, office):
        """
        """
        obj, created = Office.objects.get_or_create(
            slug=office["officeslug"],
            defaults={
                "name": office["officename"],
                "active": office["active"]
            }
        )
        if not created:
            logger.debug("%s exists" % (office["officeslug"]))
        else:
            logger.debug("%s created" % (office["officeslug"]))

    def make_contest(self, office, contest):
        """
        """
        this_office = Office.objects.get(name=office["officename"])
        obj, created = this_office.contest_set.get_or_create(
            election_id=contest["election_id"],
            resultsource_id=contest["resultsource_id"],
            contestid=contest["contestid"],
            defaults={
                "contestname": contest["contestname"],
                "seatnum": contest["seatnum"],
                "contestdescription": contest["contestdescription"],
                "is_uncontested": contest["is_uncontested"],
                "is_national": contest["is_national"],
                "is_statewide": contest["is_statewide"],
                "is_ballot_measure": contest["is_ballot_measure"],
                "is_judicial": contest["is_judicial"],
                "precinctstotal": contest["precinctstotal"],
                "precinctsreporting": contest["precinctsreporting"],
                "precinctsreportingpct": contest["precinctsreportingpct"],
                "votersregistered": contest["votersregistered"],
                "votersturnout": contest["votersturnout"],
            }
        )
        if not created:
            logger.debug("%s exists" % (contest["contestid"]))
        else:
            logger.debug("%s created" % (contest["contestid"]))

    def make_judicial(self, contest, judicial):
        """
        """
        this_contest = Contest.objects.get(contestid=contest["contestid"])
        obj, created = this_contest.judicialcandidate_set.get_or_create(
            judgeid=judicial["judgeid"],
            defaults={
                "ballotorder": judicial["ballotorder"],
                "firstname": judicial["firstname"],
                "lastname": judicial["lastname"],
                "fullname": judicial["fullname"],
                "yescount": judicial["yescount"],
                "yespct": judicial["yespct"],
                "nocount": judicial["nocount"],
                "nopct": judicial["nopct"],
            }
        )
        if not created:
            logger.debug("%s exists" % (judicial["judgeid"]))
        else:
            logger.debug("%s created" % (judicial["judgeid"]))

    def make_measure(self, contest, measure):
        """
        """
        this_contest = Contest.objects.get(contestid=contest["contestid"])
        obj, created = this_contest.ballotmeasure_set.get_or_create(
            measureid=measure["measureid"],
            defaults={
                "ballotorder": measure["ballotorder"],
                "fullname": measure["fullname"],
                "description": measure["description"],
                "yescount": measure["yescount"],
                "yespct": measure["yespct"],
                "nocount": measure["nocount"],
                "nopct": measure["nopct"],
            }
        )
        if not created:
            logger.debug("%s exists" % (measure["measureid"]))
        else:
            logger.debug("%s created" % (measure["measureid"]))

    def make_candidate(self, contest, candidate):
        """
        """
        this_contest = Contest.objects.get(contestid=contest["contestid"])
        obj, created = this_contest.candidate_set.get_or_create(
            candidateid=candidate["candidateid"],
            defaults={
                "ballotorder": candidate["ballotorder"],
                "firstname": candidate["firstname"],
                "lastname": candidate["lastname"],
                "fullname": candidate["fullname"],
                "party": candidate["party"],
                "incumbent": candidate["incumbent"],
                "votecount": candidate["votecount"],
                "votepct": candidate["votepct"],
            }
        )
        if not created:
            logger.debug("%s exists" % (candidate["candidateid"]))
        else:
            logger.debug("%s created" % (candidate["candidateid"]))
