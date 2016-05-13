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

    def set_id_field(self):
        """
        """
        self.id = self.unique_id

    def _slug(self, unicode_string):
        """
        creates a slug from a unicode string
        """
        if isinstance(unicode_string, unicode):
            output = unicode_string.lower().strip().replace(" ", "-")
        else:
            output = unicode(unicode_string)
            output = output.lower().strip().replace(" ", "-")
        number_of_spaces = output.count(" ")
        if number_of_spaces == 0:
            return output
        else:
            return False

    def _concat(self, *args, **kwargs):
        """
        """
        values = list(args)
        output = kwargs["delimiter"].join(values)
        return output

    def _to_num(self, value):
        """
        can this value be converted to an int
        """
        output = {}
        # actually integer values
        if isinstance(value, (int, long)):
            output["change"] = True
            output["value"] = value
        # some floats can be converted without loss
        elif isinstance(value, float):
            output["change"] = (int(value) == float(value))
            output["value"] = value
        # we can't convert non-string
        elif not isinstance(value, basestring):
            output["change"] = False
            output["value"] = None
        else:
            value = value.strip()
            try:
                # try to convert value to float
                float_value = float(value)
                output["change"] = True
                output["value"] = float_value
            except ValueError:
                # if fails try to convert value to int
                try:
                    int_value = int(value)
                    output["change"] = True
                    output["value"] = int_value
                # if fails it's a string
                except ValueError:
                    output["change"] = False
                    output["value"] = None
        return output

    def _calc_pct(self, dividend, divisor):
        """
        """
        if dividend is not None and divisor is not None:
            output = dividend / divisor
        else:
            output = False
        return output

    def _find_nth(self, haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start+1)
            n -= 1
        return start


