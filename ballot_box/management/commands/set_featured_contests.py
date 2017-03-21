from django.conf import settings
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from ballot_box.models import Contest

logger = logging.getLogger("kpcc_backroom_handshakes")

class Command(BaseCommand):
    help = ""

    interested = [
        u'sos-statewide-president',
        u'sos-statewide-us-senate',
    ]

    featured = [
        u'sos-statewide-president',
        u'sos-statewide-us-senate',
        u'lac-county-los-angeles-county-supervisor-district-4',
        u'lac-county-los-angeles-county-supervisor-district-5',
    ]


    # def generate_lists():
    #     interested = []
    #     featured = []
    #     contests = Contest.objects.all()
    #     for obj in contests:
    #         if obj.is_display_priority == True and obj.is_homepage_priority == True:
    #             interested.append(obj.contestid)
    #             featured.append(obj.contestid)
    #         elif obj.is_display_priority == True:
    #             interested.append(obj.contestid)
    #         elif obj.is_homepage_priority == True:
    #             featured.append(obj.contestid)
    #         else:
    #             pass
    #     print interested
    #     print featured


    def handle(self, *args, **options):
        for id in self.interested:
            try:
                obj = Contest.objects.get(contestid=id)
                obj.is_display_priority = True
                obj.save()
                logger.debug("%s is ready for election night" % (obj.contestname))
            except:
                logger.debug("%s doesn't exist in the database" % (obj.contestname))
        for id in self.featured:
            try:
                obj = Contest.objects.get(contestid=id)
                obj.is_homepage_priority = True
                obj.save()
                logger.debug("%s is ready for election night" % (obj.contestname))
            except:
                logger.debug("%s doesn't exist in the database" % (obj.contestname))
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
