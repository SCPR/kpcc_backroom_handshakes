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


register.filter(currency)
register.filter(neg_to_posi)
register.filter(percentage)
