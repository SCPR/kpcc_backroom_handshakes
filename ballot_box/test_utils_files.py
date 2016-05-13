from django.test import TestCase
from django.conf import settings
from ballot_box.models import ResultSource
import os.path
import sys
import errno
import logging
import time
import datetime
import shutil
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import zipfile

logger = logging.getLogger("kpcc_backroom_handshakes")

# create your tests here
class TestFileRetrival(TestCase):
    """
    a series of reusable methods we'll need for downloading and moving files
    """

    fixtures = ['ballot_box/fixtures/data.json']

    def setUp(self):
        """
        setup some variables for our tests
        """
        self.data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

        self.list_of_expected_files = []

        self.date_object = datetime.datetime.now()

        self.date_string = self.date_object.strftime("%Y_%m_%d_%H_%M_%S")

        self.sources = ResultSource.objects.all()


    def test_a_download_chain(self):
        """
        initiate a series of functions based on a list of data sources that will eventually be defined in the database
        """
        logger.debug("running file download tests")
        for item in self.sources:
            self.list_of_expected_files = item.source_files.split(",")
            if item.source_active == True:

                item.file_name = "%s_%s_%s_results%s" % (self.data_directory, self.date_string, item.source_short, item.source_type)

                # item.file_name = "%s_%s_%s" % (self.data_directory, item.source_short, os.path.basename(item.source_url))

                self.Test_successful_save_results(item)
                self.Test_copy_timestamped_file_as_latest(item)
                self.Test_create_directory_for_latest_file(item)
                self.Test_move_latest_files_to_latest_directory(item)
                self.Test_archive_downloaded_file(item)
                self.Test_found_required_files(item)
                self.Test_unzip_latest_file(item)


    def Test_successful_save_results(self, item):
        """
        can i take the response from url can and write it to a timestamped version of the a file that should work no matter the file. it's  based on the file_ext specified in a config dict
        """

        # test_urls = [
        #     "https://httpbin.org/status/200",
        #     "https://httpbin.org/gzip",
        #     "https://httpbin.org/status/404",
        #     "https://httpbin.org/status/500",
        #     "https://httpbin.org/status/502",
        #     "https://httpbin.org/status/503",
        #     "https://httpbin.org/status/504",
        #     "https://httpbin.org/redirect/10",
        #     "https://httpbin.org/delay/9",
        #     "https://httpbin.org/delay/11",
        # ]

        session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount("http://", HTTPAdapter(max_retries=retries))
        response = session.get(
            item.source_url,
            headers=settings.REQUEST_HEADERS,
            timeout=10,
            allow_redirects=False
        )
        try:
            response.raise_for_status()
            self.assertEquals(response.status_code, 200)
            self.assertIsNotNone(response.content)
        except requests.exceptions.ConnectionError as exception:
            # incorrect domain
            logger.error("%s: %s" % (exception, item.source_url))
            raise
        except requests.exceptions.Timeout as exception:
            # maybe set up for a retry, or continue in a retry loop
            logger.error("%s: %s" % (exception, item.source_url))
            raise
        except requests.exceptions.TooManyRedirects as exception:
            # tell the user their url was bad and try a different one
            logger.error("%s: %s" % (exception, item.source_url))
            raise
        except requests.exceptions.RequestException as exception:
            # catastrophic error and bail
            logger.error("%s: %s" % (exception, item.source_url))
            sys.exit(1)
        with open(item.file_name, "wb") as output:
            output.write(response.content)
        file_exists = os.path.isfile(item.file_name)
        file_has_size = os.path.getsize(item.file_name)
        self.assertEquals(file_exists, True)
        if file_exists == True:
            self.assertTrue(file_has_size > 0)
            if file_has_size > 0:
                logger.debug("Success!")
            else:
                logger.error("Your file has zero data")
                raise Exception
        else:
            logger.error("Your file doesn't exist")
            raise Exception


    def Test_copy_timestamped_file_as_latest(self, item):
        """
        create timestamped version of a file deemed latest
        """
        item.file_latest = "%s%s_latest%s" % (self.data_directory, item.source_short, item.source_type)
        shutil.copyfile(item.file_name, item.file_latest)
        file_exists = os.path.isfile(item.file_latest)
        self.assertEquals(file_exists, True)
        logger.debug("Success!")


    def Test_create_directory_for_latest_file(self, item):
        """
        move latest files to a working directory
        """
        working = "%s%s_latest" % (self.data_directory, item.source_short)
        try:
            os.makedirs(working)
            logger.debug("Success!")
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


    def Test_move_latest_files_to_latest_directory(self, item):
        """
        move timestamped file to working directory as latest
        """
        working = "%s%s_latest" % (self.data_directory, item.source_short)
        latest = os.path.join(working, os.path.basename(item.file_latest))
        shutil.copy(item.file_latest, working)
        os.remove(item.file_latest)
        file_exists = os.path.isfile(latest)
        self.assertEquals(file_exists, True)
        file_exists = os.path.isfile(working)
        self.assertEquals(file_exists, False)
        logger.debug("Success!")


    def Test_archive_downloaded_file(self, item):
        """
        move timestamped zipfile to archives
        """
        archives = "%s_archived_files" % (self.data_directory)
        try:
            os.makedirs(archives)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        shutil.move(item.file_name, archives)
        file_exists = os.path.isfile(item.file_name)
        self.assertEquals(file_exists, False)
        logger.debug("Success!")


    def Test_found_required_files(self, item):
        """
        compare files in a zipfile with a list of expected files
        """
        working = "%s%s_latest" % (self.data_directory, item.source_short)
        latest = os.path.join(working, os.path.basename(item.file_latest))
        if item.source_type == ".zip":
            try:
                with zipfile.ZipFile(latest) as zip:
                    files = zipfile.ZipFile.namelist(zip)
                    for file in self.list_of_expected_files:
                        self.assertEquals(file.strip() in set(files), True)
                        logger.debug("Success: %s exists" % (file.strip()))
            except Exception, exception:
                logger.error(exception)
        else:
            try:
                for file in self.list_of_expected_files:
                    self.assertEquals(file.strip(), os.path.basename(item.file_latest))
                    logger.debug("Success: %s exists" % (file.strip()))
            except Exception, exception:
                logger.error(exception)
                raise


    def Test_unzip_latest_file(self, item):
        """
        if the item is a zipfile can I extract the files?
        """
        if item.source_type == ".zip":
            working = "%s%s_latest" % (self.data_directory, item.source_short)
            file_latest = os.path.join(working, os.path.basename(item.file_latest))
            with zipfile.ZipFile(file_latest) as zip:
                self.assertIsNone(zipfile.ZipFile.testzip(zip))
                for file in self.list_of_expected_files:
                    file = file.strip()
                    zip.extract(file, working)
                    file_exists = os.path.isfile(os.path.join(working, file))
                    self.assertEquals(file_exists, True)
            os.remove(file_latest)
            file_exists = os.path.isfile(file_latest)
            self.assertEquals(file_exists, False)
            logger.debug("Success!")
