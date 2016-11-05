from django.contrib.humanize.templatetags.humanize import intcomma
from django.template import Library, Context
from django.conf import settings
from django.utils.timezone import utc
from django.db.models import Q, Avg, Max, Min, Sum, Count
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.template import Library
from dateutil import parser
from datetime import datetime, date, time, timedelta
import json
import logging
import decimal
import calculate
import math

logger = logging.getLogger("kpcc_backroom_handshakes")

register = Library()


@register.filter
def currency(dollars):
    dollars = round(int(dollars), 2)
    return "$%s" % (intcomma(int(dollars)))


@register.filter
def neg_to_posi(value):
    return abs(value)


@register.filter
def percentage(value):
    if value == None or value == 0:
        return "0"
    else:
        return "%s" % (value*100)

@register.filter
def convert_political_party(value):
    if value == "American Independent":
        output = "AI"
    elif value == "Republican":
        output = "R"
    elif value == "Democrat":
        output = "D"
    elif value == "Peace And Freedom":
        output = "PF"
    elif value == "Peace and Freedom":
        output = "PF"
    elif value == "Libertarian":
        output = "L"
    elif value == "Green":
        output = "G"
    elif value == "Republican , American Independent":
        output = "R"
    else:
        output = None
    return output

register.filter(currency)
register.filter(neg_to_posi)
register.filter(percentage)
register.filter(convert_political_party)
