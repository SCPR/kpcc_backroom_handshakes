from django.conf import settings
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from ballot_box.models import Contest, BallotMeasure, Candidate

logger = logging.getLogger("kpcc_backroom_handshakes")

class Command(BaseCommand):
    help = ""
    def handle(self, *args, **options):
        contests = Contest.objects.all()
        for obj in contests:
            obj.precinctsreporting = 0
            obj.precinctsreportingpct = 0
            obj.save(update_fields=["precinctsreporting", "precinctsreportingpct"])
        candidates = Candidate.objects.all()
        for obj in candidates:
            obj.votecount = 0
            obj.votepct = 0
            obj.save(update_fields=["votecount", "votepct"])
        measures = BallotMeasure.objects.all()
        for obj in measures:
            obj.yescount = 0
            obj.yespct = 0.0
            obj.nocount = 0
            obj.nopct = 0.0
            obj.save(update_fields=["yescount", "yespct", "nocount", "nopct"])
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
