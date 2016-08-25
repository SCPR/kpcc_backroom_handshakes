from django.conf import settings
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from maplight_finance.manager_fetch_cash_money import BuildDonationCharts

logger = logging.getLogger("kpcc_backroom_handshakes")

class Command(BaseCommand):
    help = "Begin request to maplight for latest ballot measure donations"
    def handle(self, *args, **options):
        task_run = BuildDonationCharts()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
