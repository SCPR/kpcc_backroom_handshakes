#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime
from ballot_box.models import *
from ballot_box.utils_data import Framer
import logging
import time
import datetime
import os.path
import shutil
import pytz

logger = logging.getLogger("kpcc_backroom_handshakes")


class Saver(object):
    """
    """

    def make_office(self, office):
        """
        """
        obj, created = Office.objects.update_or_create(
            slug=office["officeslug"],
            defaults={
                "name": office["officename"],
                "active": office["active"]
            }
        )
        if created:
            logger.debug("%s created" % (office["officeslug"]))
        else:
            logger.debug("%s exists" % (office["officeslug"]))

    def make_contest(self, office, contest):
        """
        """
        this_office = Office.objects.get(name=office["officename"])
        obj, created = this_office.contest_set.update_or_create(
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
                "reporttype": contest["reporttype"],
                "precinctstotal": contest["precinctstotal"],
                "precinctsreporting": contest["precinctsreporting"],
                "precinctsreportingpct": contest["precinctsreportingpct"],
                "votersregistered": contest["votersregistered"],
                "votersturnout": contest["votersturnout"],
            }
        )
        if created:
            logger.debug("%s created" % (contest["contestid"]))
        else:
            logger.debug("%s exists but we updated figures" %
                         (contest["contestid"]))

    def make_judicial(self, contest, judicial):
        """
        """
        this_contest = Contest.objects.get(contestid=contest["contestid"])
        obj, created = this_contest.judicialcandidate_set.update_or_create(
            judgeid=judicial["judgeid"],
            defaults={
                "ballotorder": judicial["ballotorder"],
                "firstname": judicial["firstname"],
                "lastname": judicial["lastname"],
                "fullname": judicial["fullname"],
                "yescount": judicial["yescount"],
                "yespct": judicial["yespct"] / 100,
                "nocount": judicial["nocount"],
                "nopct": judicial["nopct"] / 100,
            }
        )
        if created:
            logger.debug("%s created" % (judicial["judgeid"]))
        else:
            logger.debug("%s exists but we updated figures" %
                         (judicial["judgeid"]))

    def make_measure(self, contest, measure):
        """
        """
        this_contest = Contest.objects.get(contestid=contest["contestid"])
        obj, created = this_contest.ballotmeasure_set.update_or_create(
            measureid=measure["measureid"],
            defaults={
                "ballotorder": measure["ballotorder"],
                "fullname": measure["fullname"],
                "description": measure["description"],
                "yescount": measure["yescount"],
                "yespct": measure["yespct"] / 100,
                "nocount": measure["nocount"],
                "nopct": measure["nopct"] / 100,
            }
        )
        if created:
            logger.debug("%s created" % (measure["measureid"]))
        else:
            logger.debug("%s exists but we updated figures" %
                         (measure["measureid"]))

    def make_candidate(self, contest, candidate):
        """
        """
        this_contest = Contest.objects.get(contestid=contest["contestid"])
        obj, created = this_contest.candidate_set.update_or_create(
            candidateid=candidate["candidateid"],
            defaults={
                "ballotorder": candidate["ballotorder"],
                "firstname": candidate["firstname"],
                "lastname": candidate["lastname"],
                "fullname": candidate["fullname"],
                "party": candidate["party"],
                "incumbent": candidate["incumbent"],
                "votecount": candidate["votecount"],
                "votepct": candidate["votepct"] / 100,
            }
        )
        if created:
            logger.debug("%s created" % (candidate["candidateid"]))
        else:
            logger.debug("%s exists but we updated figures" %
                         (candidate["candidateid"]))

    def _eval_timestamps(self, file_time, database_time):
        """
        """
        fttz = localtime(file_time).tzinfo
        dbtz = localtime(database_time).tzinfo
        if fttz == None and dbtz == None:
            raise Exception
        elif fttz == None:
            raise Exception
        elif dbtz == None:
            raise Exception
        else:
            if fttz._tzname == "PDT" or fttz._tzname == "PST":
                if file_time > database_time:
                    return True
                else:
                    return False
            else:
                raise Exception

    def _update_result_timestamps(self, src, file_timestamp):
        """
        """
        obj = ResultSource.objects.get(source_slug=src.source_slug)
        obj.source_latest = file_timestamp
        obj.save(update_fields=["source_latest"])

    def _make_contest_id(self, *args, **kwargs):
        """
        """
        framer = Framer()
        required_keys = [
            "electionid",
            "source_short",
            "level",
            "officeslug",
        ]
        if len(args) != len(required_keys):
            raise Exception
        else:
            pass
        if kwargs:
            args = list(args)
            # this needs work but it's a start
            args.append(kwargs.values()[0].lower())
            output = framer._concat(*args, delimiter="-")
        else:
            output = framer._concat(*args, delimiter="-")
        return output

    def _make_this_id(self, contest_type, *args, **kwargs):
        """
        """
        framer = Framer()
        if contest_type == "measure":
            required_keys = [
                "contestid",
                "measure_id",
            ]
        elif contest_type == "judicial":
            required_keys = [
                "contestid",
                "judicialslug",
            ]
        elif contest_type == "candidate":
            required_keys = [
                "contestid",
                "candidateslug",
            ]
        if len(args) != len(required_keys):
            raise Exception
        else:
            pass
        if kwargs:
            args = list(args)
            # this needs work but it's a start
            args.append(kwargs.values()[0].lower())
            output = framer._concat(*args, delimiter="-")
        else:
            output = framer._concat(*args, delimiter="-")
        return output
