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

logger = logging.getLogger("kpcc_backroom_handshakes")

# create your tests here


class TestDataManipulation(TestCase):
    """
    a series of reusable methods we'll need for manipulating election results
    """

    def setUp(self):
        self.list_of_potential_ints = [
            "This Could",
            " This Could ",
            "2,354",
            " 2,354 ",
            2354,
            "235,409",
            " 235,409 ",
            235409,
            3.1415,
            " 3.1415 ",
            -1,
            "42262",
            42262,
            "5060.7",
            5060.7,
            "6528.4",
            6528.4,
            "1001.5",
            1001.5,
            "221.27",
            221.27,
            "472853",
            472853,
            "237081000",
            237081000,
            "237,081,000",
            "61",
            "65.65",
            "75.27",
            "0.0343",
            0.0343,
            {"nonstring": "none"}
        ]

        self.list_of_unicode_strings = [
            u"Kathryn Mickle Werdegar",
            u"Goodwin Liu",
            u"Mariano-Florentino Cuéllar",
            u"Christopher Lawrence Keller",
        ]

    def test_can_str_to_num(self):
        """
        given a value can it be converted to an int
        http://stackoverflow.com/a/16464365
        """
        logger.debug("given a value can it be converted to an int")
        for value in self.list_of_potential_ints:
            status = {}
            # actually integer values
            if isinstance(value, (int, long)):
                status["convert"] = True
                status["value"] = value
                self.assertIs(type(value), int)
                self.assertEqual(status["convert"], True)
            # some floats can be converted without loss
            elif isinstance(value, float):
                status["convert"] = (int(value) == float(value))
                status["value"] = value
                self.assertEqual(status["convert"], False)
            # we can't convert non-string
            elif not isinstance(value, basestring):
                status["convert"] = False
                status["value"] = "Nonstring"
                self.assertEqual(status["convert"], False)
            else:
                value = value.strip()
                try:
                    # try to convert value to float
                    float_value = float(value)
                    status["convert"] = True
                    status["value"] = float_value
                    self.assertIs(type(float_value), float)
                    self.assertEqual(status["convert"], True)
                except ValueError:
                    # if fails try to convert value to int
                    try:
                        int_value = int(value)
                        status["convert"] = True
                        status["value"] = int_value
                        self.assertIs(type(int_value), int)
                        self.assertEqual(status["convert"], True)
                    # if fails it's a string
                    except ValueError:
                        status["convert"] = False
                        status["value"] = "String"
                        self.assertIs(type(value), str)
                        self.assertEqual(status["convert"], False)
            self.assertIsNotNone(status)
            self.assertIs(type(status), dict)
            self.assertEqual(status.has_key("convert"), True)
            self.assertEqual(status.has_key("value"), True)
        logger.debug("Success!")

    def test_can_create_slug(self):
        logger.debug("given an unicode string it can be slugged")
        for uni in self.list_of_unicode_strings:
            self.assertIsInstance(uni, unicode)
            value = uni.lower().strip().replace(" ", "-")
            number_of_spaces = value.count(" ")
            self.assertEqual(number_of_spaces, 0)
