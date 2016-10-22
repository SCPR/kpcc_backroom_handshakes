#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.encoding import smart_str, smart_unicode
from measure_finance.models import Measure, MeasureContributor, MeasureTotal
from election_registrar.models import ResultSource, Election
from delorean import parse
import pytz
from pytz import timezone
from nameparser import HumanName
import requests
import logging
import types
import re
from datetime import tzinfo, date

logger = logging.getLogger("kpcc_backroom_handshakes")


class BuildDonationCharts(object):
    """
    scaffolding to make an api request to MapLight and return ballot initiative contributions
    """

    this_election = "general-2016-11-08"

    list_of_measures = [
        2014,
        2015,
        2016,
        2017,
        2018,
        2019,
        2020,
        2021,
        2022,
        2023,
        2024,
        2025,
        2026,
        2027,
        2028,
        2029,
        2030,
    ]

    request_headers = settings.REQUEST_HEADERS

    request_headers["x-api-key"] = settings.MAP_LIGHT_API_KEY

    api_url = "https://8d984hb45b.execute-api.us-west-2.amazonaws.com/prod/measures?language=en&id="

    def _init(self, *args, **kwargs):
        """
        run the functions needed to get contributors
        """
        f = Framer()
        election = Election.objects.filter(electionid=self.this_election).first()
        for measure in self.list_of_measures:
            requested_url = "%s%s" % (self.api_url, measure)
            response = requests.get(requested_url, headers=self.request_headers)
            measure_data = response.json()["measure"]
            identifying_information = measure_data["official_identifier"].split(" ")
            measure_data["official_identifier"] = "Proposition %s" % (identifying_information[1])
            measure_data["official_identifier_slug"] = f._slug(measure_data["official_identifier"])
            measure_data["election_id"] = election.id
            measure_data = f._massage_measure_title(measure_data)
            saver = Saver()
            saver.make_measure(measure_data)
            saver.make_measure_contributor(measure_data)
            saver.make_measure_total(measure_data)


class Saver(object):
    """
    """

    log_message = "\n*** My Import Messages ***\n"

    def make_measure(self, measure):
        """
        """
        log_message = ""
        f = Framer()
        try:
            obj, created = Measure.objects.update_or_create(
                measure_id=measure["measure_id"],
                election_id=measure["election_id"],
                defaults={
                    "official_identifier": measure["official_identifier"],
                    "official_identifier_slug": measure["official_identifier_slug"],
                    "topic": measure["topic"],
                    "official_title": measure["official_title"],
                    "official_short_summary": measure["official_short_summary"],
                    "official_summary": measure["official_summary"],
                    "official_summary_author": measure["official_summary_author"],
                    "official_yes_vote_means": measure["official_yes_vote_means"],
                    "official_no_vote_means": measure["official_no_vote_means"],
                    "official_vote_means_source": measure["official_vote_means_source"],
                    "official_financial_effect": measure["official_financial_effect"],
                    "official_financial_effect_author": measure["official_financial_effect_author"],
                    "official_impartial_analysis": measure["official_impartial_analysis"],
                    "official_impartial_analysis_author": measure["official_impartial_analysis_author"],
                    "official_tax_rate": measure["official_tax_rate"],
                    "official_tax_rate_author": measure["official_tax_rate_author"],
                    "official_short_arguments_yes": measure["official_short_arguments_yes"],
                    "official_short_arguments_no": measure["official_short_arguments_no"],
                    "official_short_arguments_source": measure["official_short_arguments_source"],
                    "official_rebuttal_yes": measure["official_rebuttal_yes"],
                    "official_rebuttal_no": measure["official_rebuttal_no"],
                    "measure_type": measure["measure_type"],
                    "passage_requirements": measure["passage_requirements"],
                    "fulltext_link": measure["fulltext_link"],
                    "published": measure["published"],
                    "disable_finance_data": measure["disable_finance_data"],
                    "deleted": measure["deleted"],
                    "entity_type": measure["entity_type"],
                    "measure_timestamp": f._save_proper_timezone(measure["measure_timestamp"]),
                }
            )
            if created:
                log_message += "* %s created\n" % (measure["official_title"])
            else:
                log_message += "* %s exists\n" % (measure["official_title"])
        except Exception, exception:
            error_output = "%s %s" % (exception, measure["official_title"])
            logger.error(error_output)
            raise
        logger.info(log_message)
        return log_message

    def make_measure_contributor(self, measure):
        """
        """
        log_message = "\n"
        f = Framer()
        this_measure = Measure.objects.get(measure_id=measure["measure_id"])
        try:
            this_measure = Measure.objects.get(measure_id=measure["measure_id"])
        except Exception, exception:
            error_output = "%s %s" % (exception, measure["measure_id"])
            logger.error(error_output)
            raise
        try:
            contrib = MeasureContributor.objects.filter(measure_id=this_measure.id)
            if contrib:
                contrib.delete()
                log_message += "\t* Resetting contributors\n"
        except:
            pass
        try:
            for contrib in measure["measure_finance_top"]:
                if contrib["percentage_individual"] == "100.00" and contrib["top_type"] == "D":
                    contrib["name"] = f._massage_measure_donor_name(contrib["name"])
                is_llc = contrib["name"].find("LLC")
                if is_llc > 0:
                    donor_name = contrib["name"].split("LLC")
                    contrib["name"] = "%s LLC" % (donor_name[0].strip().title())
                obj, created = this_measure.measurecontributor_set.update_or_create(
                    measure=this_measure.id,
                    finance_top_id=f._to_num(contrib["finance_top_id"])["value"],
                    defaults={
                        "top_type": contrib["top_type"],
                        "support": contrib["support"],
                        "name": contrib["name"],
                        "total_amount": f._to_num(contrib["total_amount"])["value"],
                        "total_individual": f._to_num(contrib["total_individual"])["value"],
                        "total_organization": f._to_num(contrib["total_organization"])["value"],
                        "percentage_total": f._convert_to_pct(contrib["percentage_total"])["output_decimal"],
                        "percentage_individual": f._convert_to_pct(contrib["percentage_individual"])["output_decimal"],
                        "percentage_organization": f._convert_to_pct(contrib["percentage_organization"])["output_decimal"],
                        "updated_date": contrib["updated_date"],
                        "entity_type": contrib["entity_type"],
                        "finance_top_timestamp": f._save_proper_timezone(contrib["finance_top_timestamp"])
                    }
                )
                if created:
                    log_message += "\t* %s created\n" % (smart_unicode(contrib["name"]))
                else:
                    log_message += "\t* %s updated\n" % (smart_unicode(contrib["name"]))
        except Exception, exception:
            error_output = "%s %s" % (exception, contrib["finance_top_id"])
            logger.error(error_output)
            raise
        logger.info(log_message)
        return log_message

    def make_measure_total(self, measure):
        """
        """
        log_message = "\n"
        f = Framer()
        try:
            this_measure = Measure.objects.get(measure_id=measure["measure_id"])
        except Exception, exception:
            error_output = "%s %s" % (exception, measure["measure_id"])
            logger.error(error_output)
            raise
        try:
            for position in measure["measure_finance"]:
                uniq_key = "%s_%s" % (position["support"].lower(), this_measure.measure_id)
                obj, created = this_measure.measuretotal_set.update_or_create(
                    measure=this_measure.id,
                    finance_id=uniq_key,
                    defaults={
                        "support": position["support"],
                        "total_amount": f._to_num(position["total_amount"])["value"],
                        "total_individual": f._to_num(position["total_individual"])["value"],
                        "total_unitemized": f._to_num(position["total_unitemized"])["value"],
                        "total_itemized": f._to_num(position["total_itemized"])["value"],
                        "total_organization": f._to_num(position["total_organization"])["value"],
                        "pct_individual": f._convert_to_pct(position["percentage_individual"])["output_decimal"],
                        "pct_organization": f._convert_to_pct(position["percentage_organization"])["output_decimal"],
                        "pct_unitemized": f._convert_to_pct(position["percentage_unitemized"])["output_decimal"],
                        "pct_itemized": f._convert_to_pct(position["percentage_itemized"])["output_decimal"],
                        "updated_date": position["updated_date"],
                        "entity_type": position["entity_type"],
                        "finance_timestamp": f._save_proper_timezone(position["finance_timestamp"])
                    }
                )
                if created:
                    log_message += "\t* %s created\n" % (smart_unicode(position["support"]))
                else:
                    log_message += "\t* %s updated\n" % (smart_unicode(position["support"]))
        except Exception, exception:
            error_output = "%s %s" % (exception, position["finance_id"])
            logger.error(error_output)
            raise
        logger.info(log_message)
        return log_message


class Framer(object):
    """
    """

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
        output = re.sub(r'[^a-z0-9]+', '-', output).strip('-')
        output = re.sub(r'[-]+', '-', output)
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

    def _convert_to_pct(self, value):
        """
        convert whole percent to decimal
        """
        output = self._to_num(value)
        if output["convert"] == True:
            output["output_decimal"] = float(output["value"] / 100)
        else:
            output["output_decimal"] = None
        return output

    def _save_proper_timezone(self, eval_this_time):
        """
        """
        file_timestamp = parse(eval_this_time, timezone="US/Pacific")
        output = file_timestamp.datetime.astimezone(pytz.UTC)
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


    def _massage_measure_donor_name(self, name_string):
        """
        """
        name = HumanName(name_string)
        name.first = name.first.title()
        name.last = name.last.title()
        if name.middle:
            name.middle = name.middle.replace(".", "")
            name.middle = "%s." % (name.middle.title())
        if name == "JR. Munger CHARLES T.":
            name.first = "Charles"
            name.middle = "T."
            name.last = "Munger"
            name.suffix = "Jr."
        if name == "M. Quinn. Delaney":
            name.first = "M."
            name.middle = "Quinn"
            name.last = "Delaney"
            name.suffix = None
        if name == "Robert Alan. Eustace":
            name.first = "Robert"
            name.middle = "Alan"
            name.last = "Eustace"
            name.suffix = None
        if name == "Susie Tompkins. Buell":
            name.first = "Susie"
            name.middle = "Tompkins"
            name.last = "Buell"
            name.suffix = None
        if name.middle and name.suffix:
            output = "%s %s %s %s" % (name.first, name.middle, name.last, name.suffix)
        if name.middle:
            output = "%s %s %s" % (name.first, name.middle, name.last)
        elif name.suffix:
            output = "%s %s %s" % (name.first, name.last, name.suffix)
        else:
            output = "%s %s" % (name.first, name.last)
        return output


    def _massage_measure_title(self, measure):
        """
        """
        string = measure["official_title"]
        number_of_periods = [i for i, letter in enumerate(string) if letter == "."]
        if len(number_of_periods) > 1:
            count = len(number_of_periods) - 1
            output = string.replace(". ", ", ", count)
            output = output.replace(".", "")
        else:
            output = string.replace(".", "")
        measure["official_title"] = output
        if measure["official_identifier_slug"] == "proposition-54":
            measure["official_title"] = "public display of legislative bills, initiative and statute"
        elif measure["official_identifier_slug"] == "proposition-63":
            measure["official_title"] = "ammunition sales background checks, large-capacity magazine ban"
        elif measure["official_identifier_slug"] == "proposition-64":
            measure["official_title"] = "recreational marijuana legalization"
        elif measure["official_identifier_slug"] == "proposition-65":
            measure["official_title"] = "disposable bag sales for wildlife conservation"
        return measure

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
            sane_data.append(self._eval_part_of_whole(obj.votecount, kwargs["totalvotes"]))
        if hasattr(obj, "precinctsreporting") and hasattr(obj, "precinctstotal"):
            sane_data.append(self._eval_part_of_whole(obj.precinctsreporting, obj.precinctstotal))
            if obj.precinctsreporting == obj.precinctstotal and obj.precinctsreportingpct != 1.0:
                sane_data.append(False)
            sane_data.append(self._eval_part_of_whole(obj.precinctsreportingpct, 1.0))
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
