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

    list_of_expected_files = []

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
                for item in self.list_of_expected_files:
                    if item.strip() in set(files) == True:
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
                    zip.extract("X14GG510v7.xml", working)
                    zip.extract("X14GG530v7.xml", working)
                os.remove(file_latest)
                file_exists = os.path.isfile(file_latest)
                if file_exists == False:
                    logger.debug("Success!")