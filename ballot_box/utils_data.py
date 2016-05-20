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

    def _slug(self, value):
        """
        creates an unicode slug from a value
        """
        if isinstance(value, basestring):
            try:
                converted = value
            except Exception, exception:
                logger.error(exception)
                raise
        elif isinstance(value, str):
            try:
                converted = unicode(value, "utf-8")
            except Exception, exception:
                logger.error(exception)
                raise
        elif isinstance(value, (int, long, float)):
            self.assertNotIsInstance(value, basestring)
            try:
                converted = str(value)
                converted = unicode(converted)
            except Exception, exception:
                logger.error(exception)
                raise
        else:
            self.assertNotIsInstance(value, basestring)
            try:
                converted = unicode(value)
            except Exception, exception:
                logger.error(exception)
                raise
        output = converted.lower().strip().replace(" ", "-")
        output = re.sub(r"[^\w-]", "", output)

        if isinstance(output, basestring):
            number_of_spaces = output.count(" ")
            if number_of_spaces == 0:
                return output
            else:
                return False

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
        dividend = self._to_num(dividend)
        divisor = self._to_num(divisor)
        if dividend["convert"] == True and divisor["convert"] == True:
            output = float(dividend["value"] / divisor["value"])
        else:
            output = None
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
