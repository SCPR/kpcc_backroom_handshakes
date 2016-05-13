#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings
import os.path
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
            logger.debug("%s: success" % (item.source_url))
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
        if file_exists == True:
            if file_has_size > 0:
                logger.debug("Success!")
            else:
                logger.error("Your file has zero data")
                raise Exception
        else:
            logger.error("Your file doesn't exist")
            raise Exception


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


    def _found_required_files(self, item, data_directory):
        """
        compare files in a zipfile with a list of expected files
        """
        working = "%s%s_latest" % (data_directory, item.source_short)
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


    def _unzip_latest_file(self, item, data_directory):
        """
        if the item is a zipfile can I extract the files?
        """
        if item.source_type == ".zip":
            working = "%s%s_latest" % (data_directory, item.source_short)
            file_latest = os.path.join(working, os.path.basename(item.file_latest))
            with zipfile.ZipFile(file_latest) as zip:
                if zipfile.ZipFile.testzip(zip) == None:
                    for file in self.list_of_expected_files:
                        file = file.strip()
                        zip.extract(file, working)
                        file_exists = os.path.isfile(os.path.join(working, file))
                        if file_exists == True:
                            logger.debug("Success!")
                os.remove(file_latest)
                file_exists = os.path.isfile(file_latest)
                if file_exists == False:
                    logger.debug("Success!")
