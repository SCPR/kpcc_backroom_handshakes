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
import pdb

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

    def _convert_district_number(self, value):
        if "St District" in value:
            output = value.replace("St District", "st District")
        elif "Nd District" in value:
            output = value.replace("Nd District", "nd District")
        elif "Rd District" in value:
            output = value.replace("Rd District", "rd District")
        elif "Th District" in value:
            output = value.replace("Th District", "th District")
        else:
            output = value
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

class Namefixer(object):
    """
    """

    def __init__(self, **kwargs):
        """
        """
        self.patterns = {
            "muni":"municipal",
            "bd":"board",
            "dist":"district",
            "cr":"center",
            "wtr":"water",
            "div":"division",
            "vly":"valley",
            "gov":"governing",
            "gbm":"governing board member",
            "tr":"trustee",
            "no":["no.","north"],
            "co":"county",
            "gen":"general",
            "mun":"municipal",
            "comm":"community",
            "unif":"unified",
            "replenish":"replenishment district",
            "so":"southern",
            "cal":"california",
            "spc":"special",
            "spec":"special",
            "authy":"authority",
            "mt":"mountains",
            "rec":"recreation",
            "con":"conservation",
            "sch":"school",
            "coll":"college",
            "usd":"unified school district",
            "cty":"city",
            "com":"community",
            "col":"college"
        }

        self.county_exceptions = {
            "judge":"judge",
            "county measure":"measure",
            "supervisor":"supervisor"
        }

        self.statewide_props = {
            "51": "K-12 and Community College Facilities",
            "52": "Medi-Cal Hospital Fee Program",
            "53": "Voter Approval of Revenue Bonds",
            "54": "Legislative Procedure Requirements",
            "55": "Tax Extension for Education and Healthcare",
            "56": "Cigarette Tax",
            "57": "Criminal Sentences & Juvenile Crime Proceedings",
            "58": "English Proficiency Multilingual Education",
            "59": "Corporate Political Spending Advisory Question",
            "60": "Adult Film Condom Requirements",
            "61": "State Prescription Drug Purchase Standards",
            "62": "Repeal of Death Penalty",
            "63": "Firearms and Ammunition Sales",
            "64": "Marijuana Legalization",
            "65": "Carryout Bag Charges",
            "66": "Death Penalty Procedure Time Limits",
            "67": "Ban on Single-use Plastic Bags",
        }

    def _fix(self, string):
        for p, r in self.patterns.iteritems():
            if p == "no":
                number = re.compile(p + r'(\s[0-9])',flags=re.IGNORECASE)
                # north = re.compile(p + r'(\s[a-zA-Z])',flags=re.IGNORECASE)
                north = re.compile(r'(\s)' + p + r'(\s[a-zA-Z])',flags=re.IGNORECASE)
                bernardino = re.compile(r'(?<=bernardi)' + p,flags=re.IGNORECASE)
                if re.search(number,string):
                    string = re.sub(number,r[0]+r'\1',string)
                elif re.search(north,string):
                    string = re.sub(north,r[1]+r'\1',string)
                elif re.search(bernardino,string):
                    pass
            elif p == "cal":
                local = re.compile(r'(?<=lo)' + p,flags=re.IGNORECASE)
                california = re.compile(p + r'(?=\s|$)',flags=re.IGNORECASE)
                if re.search(local,string):
                    pass
                else:
                    string = re.sub(california,r,string)
            elif p == "tr":
                search = re.compile(r'(?<=\s)' + p + r'(?=\s|$)',flags=re.IGNORECASE)
                string = re.sub(search,r,string)
            else:
                search = re.compile(p + r'(?=\s|$)',flags=re.IGNORECASE)
                string = re.sub(search,r,string)
        return string

    def _affix_county(self, county, contest):
        for p, r in self.county_exceptions.iteritems():
            search = re.compile(p, flags=re.IGNORECASE)
            contest = re.sub(search,county + ' ' + r,contest)
        return contest

    def _titlecase_with_accents(self, string):
        subs = ('ABCDEFGHIJKLMNOPQRSTUVWXYZÂÁÀÄÃÊÉÈËÏÍÎÖÓÔÖÚÙÛÑÇ', 'abcdefghijklmnopqrstuvwxyzâáàäãêéèëïíîöóôöúùûñç')
        string = string.split(" ")
        titlecase = []
        for word in string:
            if word:
                if word == "II" or word == "III" or word == "IV":
                    titlecase.append(word)
                else:
                    quoted = False

                    # More individual character exceptions
                    if "¡" in word:
                        word = re.sub("¡", "", word)
                    if "'" in word or "\"" in word:
                        word = re.sub(r'\'|\"',"",word)
                        quoted = True
                    first_letter = word[0]
                    new_word = word
                    for s in range(len(subs[0])):
                        new_word = re.sub(subs[0][s], subs[1][s], new_word)
                    titled_word = first_letter + new_word[1:]
                    if quoted:
                        titled_word = "'" + titled_word + "'"
                    titlecase.append(titled_word)
        newstring = " ".join(titlecase)
        return newstring

    def _fix_oc_props(self, type, string):
        """
        a helper method to deal with how orange county
        is sending along the props and measures
        for the 2016 general election
        """
        output = {}
        string = string.replace("  ", " ")
        if type == "Advisory Vote":
            value = string.replace("Advisory Vote Only. ", "")
            output["type"] = type
            output["prop_num"] = value[0:2]
            output["district"] = "Mesa Water District"
            output["measure_fullname"] = "Advisory Vote TT"
            output["description"] = value[3:].lower()
        elif type == "Proposition":
            output["type"] = type
            output["prop_num"] = string[0:2]
            output["measure_fullname"] = "%s %s" % (output["type"], output["prop_num"])
            # output["description"] = self.statewide_props[output["prop_num"]]
            output["description"] = string[3:len(string)].title()
        elif type == "Recall":
            output["type"] = ""
            output["prop_num"] = ""
            output["district"] = "Senate District 29"
            output["measure_fullname"] = string.lower()
            output["description"] = string.lower()
        elif type == "Measure":
            dash_loco = string.index("-")
            first_comma = string.find(",")
            description_index = first_comma + 2
            output["type"] = type
            output["prop_num"] = string[0:dash_loco]
            output["district"] = string[dash_loco:first_comma].replace("-", "")
            output["measure_fullname"] = "%s %s" % (output["type"], output["prop_num"])
            output["description"] = string[description_index:].lower()
        else:
            output["type"] = type
            output["prop_num"] = ""
            output["district"] = ""
            output["measure_fullname"] = string.lower()
            output["description"]      = string.lower()
        output["type"] = unicode(output["type"])
        output["prop_num"] = unicode(output["prop_num"])
        output["measure_fullname"] = unicode(output["measure_fullname"])
        output["description"] = unicode(output["description"])
        return output
