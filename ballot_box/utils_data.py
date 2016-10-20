#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from django.conf import settings
import os.path
import errno
import logging
import time
import datetime
import shutil
import re
import types

logger = logging.getLogger("kpcc_backroom_handshakes")


class Framer(object):
    """
    """

    def __init__(self, **kwargs):
        """
        """
        self.office = {}
        self.office["officename"] = None
        self.office["officeslug"] = None
        self.office["active"] = None
        self.contest = {}
        self.contest["election_id"] = None
        self.contest["resultsource_id"] = None
        self.contest["contestid"] = None
        self.contest["contestname"] = None
        self.contest["seatnum"] = None
        self.contest["contestdescription"] = None
        self.contest["is_uncontested"] = None
        self.contest["is_national"] = None
        self.contest["is_statewide"] = None
        self.contest["is_ballot_measure"] = None
        self.contest["is_judicial"] = None
        self.contest["is_runoff"] = None
        self.contest["reporttype"] = None
        self.contest["precinctstotal"] = None
        self.contest["precinctsreporting"] = None
        self.contest["precinctsreportingpct"] = None
        self.contest["votersregistered"] = None
        self.contest["votersturnout"] = None
        self.candidate = {}
        self.candidate["candidateid"] = None
        self.candidate["ballotorder"] = None
        self.candidate["firstname"] = None
        self.candidate["lastname"] = None
        self.candidate["fullname"] = None
        self.candidate["party"] = None
        self.candidate["incumbent"] = None
        self.candidate["votecount"] = None
        self.candidate["votepct"] = None
        self.measure = {}
        self.measure["measureid"] = None
        self.measure["ballotorder"] = None
        self.measure["name"] = None
        self.measure["description"] = None
        self.measure["yescount"] = None
        self.measure["yespct"] = None
        self.measure["nocount"] = None
        self.measure["nopct"] = None
        self.judicial = {}
        self.judicial["judgeid"] = None
        self.judicial["judicialslug"] = None
        self.judicial["ballotorder"] = None
        self.judicial["fullname"] = None
        self.judicial["yescount"] = None
        self.judicial["yespct"] = None
        self.judicial["nocount"] = None
        self.judicial["nopct"] = None

    # def set_id_field(self):
    #     """
    #     """
    #     self.id = self.unique_id


    def _to_num(self, value):
        """
        given a value can it be converted to an int
        http://stackoverflow.com/a/16464365
        """
        output = {}
        # actually integer values
        if isinstance(value, (int, long)):
            output["convert"] = True
            output["value"] = value
            output["type"] = type(value)
        # some floats can be converted without loss
        elif isinstance(value, float):
            output["convert"] = (int(value) == float(value))
            output["value"] = value
            output["type"] = type(value)
        # we can't convert nonetypes
        elif isinstance(value, types.NoneType):
            output["convert"] = False
            output["value"] = None
            output["type"] = type(value)
        # we can't convert non-string
        elif not isinstance(value, basestring):
            output["convert"] = False
            output["value"] = "Nonstring"
            output["type"] = type(value)
        else:
            value = value.strip()
            try:
                # try to convert value to float
                float_value = float(value)
                output["convert"] = True
                output["value"] = float_value
                output["type"] = type(float_value)
            except ValueError:
                # if fails try to convert value to int
                try:
                    int_value = int(value)
                    output["convert"] = True
                    output["value"] = int_value
                    output["type"] = type(int_value)
                # if fails it's a string
                except ValueError:
                    output["convert"] = False
                    output["value"] = None
                    output["type"] = type(value)
        return output

    def _calc_pct(self, dividend, divisor):
        """
        calculate a percent or return false
        """
        logger.debug(dividend)
        logger.debug(divisor)

        dividend = self._to_num(dividend)
        divisor = self._to_num(divisor)
        if dividend["convert"] == True and divisor["convert"] == True:
            if divisor["value"] == 0:
                output = 0
            else:
                output = float(dividend["value"] / divisor["value"])
        else:
            output = None
        return output

    def _get_prop_number(self, value, substring):
        value = str(value)
        format_value = value.replace(substring, "")
        output = int(format_value)
        return output

    def _find_nth(self, haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + 1)
            n -= 1
        if isinstance(start, (int, float)):
            return start
        else:
            return False

    def _concat(self, *args, **kwargs):
        """
        create a slug-like string given values and a delimiter
        """
        values = list(args)
        output = []
        for value in values:
            if not isinstance(value, (str, basestring)):
                value = unicode(value)
            else:
                value = unicode(value)
            value = value.strip()
            output.append(value)
        output = kwargs["delimiter"].join(output)
        output = unicode(output)
        return output


class Checker(object):
    """
    """

    def _return_sanity_checks(self, obj, **kwargs):
        sane_data = []
        if hasattr(obj, "votepct"):
            sane_data.append(self._eval_part_of_whole(obj.votepct, 100))
        if hasattr(obj, "votecount"):
            sane_data.append(self._eval_part_of_whole(
                obj.votecount, kwargs["totalvotes"]))
        if hasattr(obj, "precinctsreporting") and hasattr(obj, "precinctstotal"):
            sane_data.append(self._eval_part_of_whole(
                obj.precinctsreporting, obj.precinctstotal))
            if obj.precinctsreporting == obj.precinctstotal and obj.precinctsreportingpct != 1.0:
                sane_data.append(False)
            sane_data.append(self._eval_part_of_whole(
                obj.precinctsreportingpct, 1.0))
        if hasattr(obj, "votersturnout"):
            sane_data.append(self._eval_part_of_whole(obj.votersturnout, 1.0))
        if hasattr(obj, "yescount") and hasattr(obj, "nocount"):
            total = (obj.yescount + obj.nocount)
            sane_data.append(self._eval_part_of_whole(obj.yescount, total))
            sane_data.append(self._eval_part_of_whole(obj.nocount, total))
        if hasattr(obj, "yespct") and hasattr(obj, "nopct"):
            sane_data.append(self._eval_part_of_whole(obj.yespct, 100))
            sane_data.append(self._eval_part_of_whole(obj.nopct, 100))
        if False in sane_data:
            return True
        else:
            return False

    def _eval_part_of_whole(self, part, whole):
        if part <= whole:
            return True
        else:
            return False
