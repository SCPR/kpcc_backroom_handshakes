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

class Retriever(object):
    """
    a series of reusable methods we'll need for downloading and moving files

    if you change something in here you're gonna want to change something in the test_utils_files script as well

    """

    list_of_expected_sos_files = [
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

    # def setUp(self):
    #     """
    #     setup some variables for our tests
    #     """

    #     self.data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    #     self.date_object = datetime.datetime.now()

    #     self.date_string = self.date_object.strftime("%Y_%m_%d_%H_%M_%S")

    #     self.sources =ResultSource.objects.all()


    # def test_a_download_chain(self):
    #     """
    #     initiate a series of functions based on a list of data sources that will eventually be defined in the database
    #     """
    #     logger.debug("running file download tests")
    #     for item in self.sources:
    #         if item.source_active == True:
    #             item.file_name = "%s_%s_%s_results%s" % (self.data_directory, self.date_string, item.source_short, item.source_type)
    #             self.Test_successful_response_from_url(item)
    #             self.Test_successful_save_results(item)
    #             if item.source_type == ".zip":
    #                 self.Test_found_files_in_zipfile(item)
    #             self.Test_copy_timestamped_file_as_latest(item)
    #             self.Test_create_directory_for_latest_file(item)
    #             self.Test_move_latest_files_to_latest_directory(item)
    #             self.Test_archive_downloaded_file(item)
    #             self.Test_unzip_latest_file(item)


    def _successful_save_results(self, item):
        """
        can i take the response from url can and write it to a timestamped version of the a file that should work no matter the file. it's  based on the file_ext specified in a config dict
        """
        try:
            response = requests.get(item.source_url, headers=settings.REQUEST_HEADERS, stream=True)
            with open(item.file_name, "wb") as output:
                output.write(response.content)
            file_exists = os.path.isfile(item.file_name)
            file_has_size = os.path.getsize(item.file_name)
            if file_exists == True and file_has_size > 0:
                logger.debug("Success!")
        except Exception, exception:
            logger.error(exception)
            raise


    def _found_files_in_zipfile(self, item):
        """
        compare files in a zipfile with a list of expected files
        """
        try:
            with zipfile.ZipFile(item.file_name) as zip:
                files = zipfile.ZipFile.namelist(zip)
                if set(files) == set(self.list_of_expected_sos_files):
                    logger.debug("File names match")
                if len(files) == len(self.list_of_expected_sos_files):
                    logger.debug("File quantities match")
            logger.debug("Success!")
        except Exception, exception:
            logger.error(exception)
            raise


    def _copy_timestamped_file_as_latest(self, item, data_directory):
        """
        create timestamped version of a file deemed latest
        """
        try:
            item.file_latest = "%s%s_latest%s" % (data_directory, item.source_short, item.source_type)
            shutil.copyfile(item.file_name, item.file_latest)
            file_exists = os.path.isfile(item.file_latest)
            if file_exists == True:
                logger.debug("Success!")
        except Exception, exception:
            logger.error(exception)
            raise


    def _create_directory_for_latest_file(self, item, data_directory):
        """
        move latest files to a working directory
        """
        working = "%s%s_latest" % (data_directory, item.source_short)
        try:
            os.makedirs(working)
            logger.debug("Success!")
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise


    def _move_latest_files_to_latest_directory(self, item, data_directory):
        """
        move timestamped file to working directory as latest
        """
        working = "%s%s_latest" % (data_directory, item.source_short)
        latest = os.path.join(working, os.path.basename(item.file_latest))
        shutil.copy(item.file_latest, working)
        os.remove(item.file_latest)
        latest_exists = os.path.isfile(latest)
        working_exists = os.path.isfile(working)
        if latest_exists == True and working_exists == False:
            logger.debug("Success!")


    def _archive_downloaded_file(self, item, data_directory):
        """
        move timestamped zipfile to archives
        """
        archives = "%s_archived_files" % (data_directory)
        try:
            os.makedirs(archives)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        shutil.move(item.file_name, archives)
        file_exists = os.path.isfile(item.file_name)
        if file_exists == False:
            logger.debug("Success!")


    def _unzip_latest_file(self, item, data_directory):
        """
        if the item is a zipfile can I extract the files?
        """
        if item.source_type == ".zip":
            working = "%s%s_latest" % (data_directory, item.source_short)
            file_latest = os.path.join(working, os.path.basename(item.file_latest))
            with zipfile.ZipFile(file_latest) as zip:
                if zipfile.ZipFile.testzip(zip) == None:
                    zip.extractall(working)
                os.remove(file_latest)
                file_exists = os.path.isfile(file_latest)
                if file_exists == False:
                    logger.debug("Success!")
