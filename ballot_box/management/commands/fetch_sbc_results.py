from django.conf import settings
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from ballot_box.manager_sbc_results import BuildSbcResults

logger = logging.getLogger("kpcc_backroom_handshakes")

class Command(BaseCommand):
    help = "Begin request to San Bernardino County registrar of voters for latest election results"
    def handle(self, *args, **options):
        task_run = BuildSbcResults()
        task_run._init()
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))