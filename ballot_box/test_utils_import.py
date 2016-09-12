from django.test import TestCase
from django.conf import settings
from ballot_box.models import *
from election_registrar.models import *
import logging

logger = logging.getLogger("kpcc_backroom_handshakes")

class ContestTestCase(TestCase):
    """
    a series of reusable methods we'll need for downloading and moving files
    """


    def setUp(self):

        Office.objects.create(
            slug="my-test-office",
            name = "My Test Office",
            active = True,
        )

        # Contest.objects.create(
        #     election_id="",
        #     resultsource_id="",
        #     contestid=1,
        #     contestname="test",
        #     seatnum="test",
        #     contestdescription="test",
        #     is_uncontested=False,
        #     is_national=False,
        #     is_statewide=True,
        #     is_ballot_measure=False,
        #     is_judicial=False,
        #     precinctstotal=60,
        #     precinctsreporting=30,
        #     precinctsreportingpct=0.500,
        #     votersregistered=100,
        #     votersturnout=0.125,
        # )

    def test_make_contest(self):
        """
        """

        test = Office.objects.all().first()
        logger.debug(test)

        # contest = Contest.objects.get(contestid="test")

        # logger.debug(contest)






        # this_office = Office.objects.get(name=office["officename"])
        # obj, created = this_office.contest_set.update_or_create(
        #     election_id=contest["election_id"],
        #     resultsource_id=contest["resultsource_id"],
        #     contestid=contest["contestid"],
        #     defaults={



