from django.test import TestCase
from django.conf import settings
import os.path
import errno
import logging
import time
import datetime
import shutil
import requests
import zipfile

logger = logging.getLogger("kpcc_backroom_handshakes")

# create your tests here
class TestFileRetrival(TestCase):
    """
    a series of reusable methods we'll need for downloading and moving files
    """
    def setUp(self):
        self.data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)
        self.file_urls = [
            {"source": "secretary of state", "file_url": "http://cms.cdn.sos.ca.gov/media/14GG/X14GGv7.zip", "file_slug": "sos", "file_ext": ".zip"},
            {"source": "la county", "file_url": "http://rrcc.co.la.ca.us/results/0014nov14.ets", "file_slug": "lac", "file_ext": ".txt"},
        ]
        self.list_of_expected_sos_files = [
            'X14GG530v7.xml',
            'X14GG510v7.xml',
            'X14GG510_0200v7.xml',
            'X14GG510_0300v7.xml',
            'X14GG510_0400v7.xml',
            'X14GG510_0500v7.xml',
            'X14GG510_0600v7.xml',
            'X14GG510_0700v7.xml',
            'X14GG510_0800v7.xml',
            'X14GG510_0900v7.xml',
            'X14GG510_1100v7.xml',
            'X14GG510_1200v7.xml',
            'X14GG510_1300v7.xml',
            'X14GG510_1400v7.xml',
            'X14GG510_1500v7.xml',
            'X14GG510_1600v7.xml',
            'X14GG510_1900v7.xml'
        ]


    def test_a_download_chain(self):
        """
        initiate a series of functions based on a list of data sources that will eventually be defined in the database
        """
        logger.debug("running file download tests")
        for item in self.file_urls:
            date_object = datetime.datetime.now()
            date_string = date_object.strftime("%Y_%m_%d_%H_%M_%S")
            item["file_name"] = "%s_%s_%s_results%s" % (self.data_directory, date_string, item["file_slug"], item["file_ext"])

            self.Test_successful_response_from_url(item)
            self.Test_successful_save_results(item)
            if item["file_ext"] == ".zip":
                self.Test_found_files_in_zipfile(item)
            self.Test_copy_timestamped_file_as_latest(item)
            self.Test_create_directory_for_latest_file(item)
            self.Test_move_latest_files_to_latest_directory(item)
            self.Test_archive_downloaded_file(item)
            self.Test_unzip_latest_file(item)

    def Test_successful_response_from_url(self, item):
        """
        make a request to a url for data or a file and evaluate the response
        """
        logger.debug("make a request to a url for data or a file and evaluate the response")
        response = requests.get(item["file_url"], headers=settings.REQUEST_HEADERS, stream=True)
        self.assertEquals(response.status_code, 200)
        self.assertIsNotNone(response.content)
        logger.debug("Success!")


    def Test_successful_save_results(self, item):
        """
        can i take the response from url can and write it to a timestamped version of the a file that should work no matter the file. it's  based on the file_ext specified in a config dict
        """
        logger.debug("can i take the response from url can and write it to a timestamped version of the a file")
        response = requests.get(item["file_url"], headers=settings.REQUEST_HEADERS, stream=True)
        output = open(item["file_name"], "wb")
        output.write(response.content)
        output.close()
        file_exists = os.path.isfile(item["file_name"])
        file_has_size = os.path.getsize(item["file_name"])
        self.assertEquals(file_exists, True)
        self.assertTrue(file_has_size > 0)
        logger.debug("Success!")


    def Test_found_files_in_zipfile(self, item):
        """
        compare files in a zipfile with a list of expected files
        """
        logger.debug("compare files in a zipfile with a list of expected files")
        with zipfile.ZipFile(item["file_name"]) as zip:
            files = zipfile.ZipFile.namelist(zip)
            self.assertEquals(set(files), set(self.list_of_expected_sos_files))
            self.assertEquals(len(files), len(self.list_of_expected_sos_files))
            logger.debug("Success!")

    def Test_copy_timestamped_file_as_latest(self, item):
        """
        create timestamped version of zipfile deemed latest
        """
        logger.debug("create timestamped version of zipfile deemed latest")
        item["file_latest"] = "%s%s_latest%s" % (self.data_directory, item["file_slug"], item["file_ext"])
        shutil.copyfile(item["file_name"], item["file_latest"])
        file_exists = os.path.isfile(item["file_latest"])
        self.assertEquals(file_exists, True)
        logger.debug("Success!")

    def Test_create_directory_for_latest_file(self, item):
        """
        move latest files to a working directory
        """
        logger.debug("move latest files to a working directory")
        working = "%s%s_latest" % (self.data_directory, item["file_slug"])
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
        logger.debug("move timestamped file to working directory as latest")
        working = "%s%s_latest" % (self.data_directory, item["file_slug"])
        latest = os.path.join(working, os.path.basename(item["file_latest"]))
        shutil.copy(item["file_latest"], working)
        os.remove(item["file_latest"])
        file_exists = os.path.isfile(latest)
        self.assertEquals(file_exists, True)
        file_exists = os.path.isfile(working)
        self.assertEquals(file_exists, False)
        logger.debug("Success!")


    def Test_archive_downloaded_file(self, item):
        """
        move timestamped zipfile to archives
        """
        logger.debug("move timestamped zipfile to archives")
        archives = "%s_archived_files" % (self.data_directory)
        try:
            os.makedirs(archives)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        shutil.move(item["file_name"], archives)
        file_exists = os.path.isfile(item["file_name"])
        self.assertEquals(file_exists, False)
        logger.debug("Success!")


    def Test_unzip_latest_file(self, item):
        """
        if the item is a zipfile can I extract the files?
        """
        logger.debug("if the item is a zipfile can I extract the files?")
        if item["file_ext"] == ".zip":
            working = "%s%s_latest" % (self.data_directory, item["file_slug"])
            file_latest = os.path.join(working, os.path.basename(item["file_latest"]))
            with zipfile.ZipFile(file_latest) as zip:
                self.assertIsNone(zipfile.ZipFile.testzip(zip))
                zip.extractall(working)
            os.remove(file_latest)
            file_exists = os.path.isfile(file_latest)
            self.assertEquals(file_exists, False)
            logger.debug("Success!")
