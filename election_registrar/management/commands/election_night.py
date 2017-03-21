from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand
import time
import datetime
import logging
from election_registrar.models import ResultSource, Election
from ballot_box.manager_sos_results import BuildSosResults
from ballot_box.manager_lac_results import BuildLacResults
from ballot_box.manager_oc_results import BuildOcResults
from ballot_box.manager_sbc_results import BuildSbcResults
from ballot_box.utils_files import Retriever

logger = logging.getLogger("kpcc_backroom_handshakes")

class Command(BaseCommand):
    help = "Begin request to secretary of state for latest election results"
    def handle(self, *args, **options):

        lac = BuildLacResults()
        lac._init()

        # sos = BuildSosResults()
        # sos._init()

        # oc = BuildOcResults()
        # oc._init()

        # sbc = BuildSbcResults()
        # sbc._init()

        sources = ResultSource.objects.filter(ready_to_build=True)
        if sources:
            # retrieve = Retriever()
            # retrieve._build_and_move_results()

            logger.debug("Building views")
            management.call_command("build", keep_build_dir=True, skip_static=True)
            logger.debug("publishing views")
            management.call_command("publish")
            logger.debug("Finished - Hurrah!!")

            for src in sources:
                logger.info("Resetting %s to False in advance of next build" % (src.source_name))
                src.ready_to_build = False
                src.save(update_fields=["ready_to_build"])
        else:
            logger.info("None of the results sources are ready to build just yet")
        self.stdout.write("\nTask finished at %s\n" % str(datetime.datetime.now()))
