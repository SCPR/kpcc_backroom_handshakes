#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
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

# create your tests here


class TestFramer(TestCase):
    """
    a series of reusable methods we'll need for manipulating election results
    """

    def setUp(self):
        self.list_of_data_to_transform = [
            u" 2,354",
            " 2,354",
            u"3,354 ",
            "3,354 ",
            u" 4,354 ",
            " 4,354 ",
            u"2,354",
            "2,354",
            2354,
            u"235,409",
            "235,409",
            235409,
            u"3.1415",
            "3.1415",
            3.1415,
            u"-1",
            "-1",
            -1,
            u"42262",
            "42262",
            42262,
            u"5060.727",
            "5060.727",
            5060.727,
            u"6528.4",
            "6528.4",
            6528.4,
            u"I Was Walking Down The Stree One Day",
            "I Was Walking Down The Stree One Day",
            u"I WAS WALKING DOWN THE STREE ONE DAY",
            "I WAS WALKING DOWN THE STREE ONE DAY",
            u"Kathryn Mickle Werdegar",
            "Kathryn Mickle Werdegar",
            u"Goodwin Liu",
            "Goodwin Liu",
            u"Mariano-Florentino Cuéllar",
            "Mariano-Florentino Cuéllar",
            u"Christopher-Richard-Smith",
            "Christopher-Richard-Smith",
            None,
            True,
            False,
            [1, 2, 3, 4, 5, 6, 7],
            ["one", "two", "three", "four", "five", "six", "seven"],
            u"51924361L",
            "51924361L",
            51924361L,
            u"9.322e-36j",
            "9.322e-36j",
            9.322e-36j,
            u"0.0343",
            "0.0343",
            0.0343,
            {"nonstring": "none"},
        ]

        self.list_of_contest_ids = [
            190000000050,
            190000000150,
            190000001150,
            "190000000050",
            "190000000150",
            "190000001150",
            u"190000000050",
            u"190000000150",
            u"190000001150",
        ]

    def test_a_download_chain(self):
        """
        initiate a series of functions based on a list of data sources that will eventually be defined in the database
        """
        logger.debug("running data framing tests")
        for value in self.list_of_data_to_transform:
            self.Test_slug(value)
            self.Test_to_num(value)
            self.Test_calc_pct(value, 100)

        for value in self.list_of_contest_ids:
            self.Test_get_prop_number(value, "190")

        self.Test_find_nth(
            "Mariano-Florentino-Ricardo",
            " - ",
            0
        )

        self.Test_concat(
            1,
            "Mariano-Florentino Cuéllar",
            0.0343,
            " three ",
            delimiter="|"
        )

    def Test_slug(self, value):
        """
        creates an unicode slug from a value
        """
        if isinstance(value, basestring):
            self.assertIsInstance(value, basestring)
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
        self.assertIsInstance(output, basestring)
        number_of_spaces = output.count(" ")
        self.assertEquals(number_of_spaces, 0)
        logger.debug("given %s i can slug it" % (value))
        return output

    def Test_to_num(self, value):
        """
        given a value can it be converted to an int
        http://stackoverflow.com/a/16464365
        """
        status = {}
        # actually integer values
        if isinstance(value, (int, long)):
            status["convert"] = True
            status["value"] = value
            status["type"] = type(value)
            self.assertIsInstance(value, (int, long))
            self.assertEqual(status["convert"], True)
        # some floats can be converted without loss
        elif isinstance(value, float):
            status["convert"] = (int(value) == float(value))
            status["value"] = value
            status["type"] = type(value)
            self.assertIsInstance(value, (int, float))
            self.assertEqual(status["convert"], False)
        # we can't convert nonetypes
        elif isinstance(value, types.NoneType):
            status["convert"] = False
            status["value"] = None
            status["type"] = type(value)
            self.assertIsInstance(value, types.NoneType)
            self.assertEqual(status["convert"], False)
        # we can't convert non-string
        elif not isinstance(value, basestring):
            status["convert"] = False
            status["value"] = "Nonstring"
            status["type"] = type(value)
            self.assertNotIsInstance(value, basestring)
            self.assertEqual(status["convert"], False)
        else:
            value = value.strip()
            try:
                # try to convert value to float
                float_value = float(value)
                status["convert"] = True
                status["value"] = float_value
                status["type"] = type(float_value)
                self.assertIsInstance(float_value, float)
                self.assertEqual(status["convert"], True)
            except ValueError:
                # if fails try to convert value to int
                try:
                    int_value = int(value)
                    status["convert"] = True
                    status["value"] = int_value
                    status["type"] = type(int_value)
                    self.assertIsInstance(int_value, int)
                    self.assertEqual(status["convert"], True)
                # if fails it's a string
                except ValueError:
                    status["convert"] = False
                    status["value"] = None
                    status["type"] = type(value)
                    self.assertIsInstance(value, (str, basestring))
                    self.assertEqual(status["convert"], False)
        self.assertIsNotNone(status)
        self.assertIs(type(status), dict)
        self.assertEqual(status.has_key("convert"), True)
        self.assertEqual(status.has_key("value"), True)
        self.assertEqual(status.has_key("type"), True)
        logger.debug("%s - given %s i made it %s" %
                     (status["convert"], value, status["value"]))
        return status

    def Test_calc_pct(self, dividend, divisor):
        """
        calculate a percent or return false
        """
        dividend = self.Test_to_num(dividend)
        divisor = self.Test_to_num(divisor)
        if dividend["convert"] == True and divisor["convert"] == True:
            output = float(dividend["value"] / divisor["value"])
            self.assertIsInstance(output, float)
        else:
            output = None
            self.assertEquals(output, None)

    def Test_get_prop_number(self, value, substring):
        value = str(value)
        self.assertIsInstance(value, (str))
        self.assertEquals(len(value), 12)
        format_value = value.replace(substring, "")
        self.assertEquals(len(format_value), 9)
        output = int(format_value)

    def Test_find_nth(self, haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + 1)
            n -= 1
        self.assertIsInstance(start, (int, float))
        return start

    def Test_concat(self, *args, **kwargs):
        """
        create a slug-like string given values and a delimiter
        """
        values = list(args)
        self.assertIsInstance(values, list)
        output = []
        for value in values:
            if not isinstance(value, (str, basestring)):
                value = unicode(value)
            else:
                value = unicode(value, "utf-8")
            value = value.strip()
            output.append(value)
        logger.debug(output)
        self.assertIsInstance(output, list)
        output = kwargs["delimiter"].join(output)
        output = unicode(output)
        self.assertIsInstance(output, basestring)
        return output
