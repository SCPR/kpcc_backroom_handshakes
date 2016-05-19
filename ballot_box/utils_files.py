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
import sys

logger = logging.getLogger("kpcc_backroom_handshakes")


class Retriever(object):
    """
    a series of reusable methods we'll need for downloading and moving files

    if you change something in here you're gonna want to change something in the test_utils_files script as well

    """

    date_object = datetime.datetime.now()

    date_string = date_object.strftime("%Y_%m_%d_%H_%M_%S")

    def _request_results_and_save(self, src, data_directory):
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
            src.source_url,
            headers=settings.REQUEST_HEADERS,
            timeout=10,
            allow_redirects=False
        )
        try:
            response.raise_for_status()
            logger.info("Success! %s responded with a file" % (src.source_url))
        except requests.exceptions.ConnectionError as exception:
            # incorrect domain
            logger.error("%s: %s" % (exception, src.source_url))
            raise
        except requests.exceptions.Timeout as exception:
            # maybe set up for a retry, or continue in a retry loop
            logger.error("%s: %s" % (exception, src.source_url))
            raise
        except requests.exceptions.TooManyRedirects as exception:
            # tell the user their url was bad and try a different one
            logger.error("%s: %s" % (exception, src.source_url))
            raise
        except requests.exceptions.RequestException as exception:
            # catastrophic error and bail
            logger.error("%s: %s" % (exception, src.source_url))
            sys.exit(1)
        this_file = os.path.basename(src.source_url)
        this_file = "_%s_%s_%s" % (
            self.date_string, src.source_short, this_file)
        self.file_name = os.path.join(data_directory, this_file)
        with open(self.file_name, "wb") as output:
            output.write(response.content)
        file_exists = os.path.isfile(self.file_name)
        file_has_size = os.path.getsize(self.file_name)
        if file_exists == True:
            logger.info("Success! %s downloaded" % (this_file))
            if file_has_size > 0:
                logger.info("Success! %s is a valid file" % (this_file))
            else:
                logger.error("Failure! %s isn't valid" % (self.file_name))
                raise Exception
        else:
            logger.error("Failure! %s doesn't exist" % (self.file_name))
            raise Exception

    def _create_directory_for_latest_file(self, src, data_directory):
        """
        move latest files to a working directory
        """
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        dir_exists = os.path.isdir(latest_directory)
        if dir_exists == True:
            logger.info("Skipping because %s already exists" %
                        (latest_directory))
        else:
            try:
                os.makedirs(latest_directory)
                logger.info("Success! We created %s" % (latest_directory))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def _copy_timestamped_file_to_latest(self, src, data_directory):
        """
        create timestamped version of a file deemed latest
        """
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        this_file = "%s%s" % (src.source_slug, src.source_type)
        latest_path = os.path.join(latest_directory, this_file)
        try:
            shutil.copyfile(self.file_name, latest_path)
            file_exists = os.path.isfile(latest_path)
            if file_exists == True:
                logger.info("Success! %s is ready to parse" % (this_file))
        except Exception, exception:
            logger.error(exception)
            raise

    def _archive_downloaded_file(self, src, data_directory):
        """
        move timestamped zipfile to archives
        """
        archives = "%s_archived_files" % (data_directory)
        this_file = os.path.basename(self.file_name)
        try:
            os.makedirs(archives)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        shutil.move(self.file_name, archives)
        file_exists = os.path.isfile(self.file_name)
        if file_exists == False:
            logger.info("Success! %s is archived" % (this_file))

    def _found_required_files(self, src, data_directory):
        """
        compare files in a zipfile with a list of expected files
        """
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        this_file = "%s%s" % (src.source_slug, src.source_type)
        latest_path = os.path.join(latest_directory, this_file)
        if src.source_type == ".zip":
            try:
                with zipfile.ZipFile(latest_path) as zip:
                    files = zipfile.ZipFile.namelist(zip)
                    for file in src.source_files.split(", "):
                        if file in set(files):
                            logger.info("Success: %s exists in the zipfile" % (file))
                        else:
                            logger.error("Failure: %s does not exist in the zipfile" % (file))
            except Exception, exception:
                logger.error(exception)
        else:
            try:
                for file in src.source_files.split(", "):
                    if file == os.path.basename(latest_path):
                        logger.info("Success: %s exists" % (file))
                    else:
                        logger.error("Failure: %s does not exist" % (file))
            except Exception, exception:
                logger.error(exception)
                raise

    def _unzip_latest_file(self, src, data_directory):
        """
        if the src is a zipfile can I extract the files?
        """
        if src.source_type == ".zip":
            latest_directory = "%s%s_latest" % (
                data_directory, src.source_short)
            this_file = "%s%s" % (src.source_slug, src.source_type)
            latest_path = os.path.join(latest_directory, this_file)
            with zipfile.ZipFile(latest_path) as zip:
                if zipfile.ZipFile.testzip(zip) == None:
                    for file in src.source_files.split(", "):
                        zip.extract(file, latest_directory)
                        file_exists = os.path.isfile(
                            os.path.join(latest_directory, file))
                        if file_exists == True:
                            logger.info("Success: %s has been extracted from the zipfile" % (file))
                        else:
                            logger.error("Failure: %s has not been extracted from the zipfile" % (file))
                os.remove(latest_path)
                file_exists = os.path.isfile(latest_path)
                if file_exists == False:
                    logger.info("%s successfully processed" %
                                 (os.path.basename(latest_path)))
        else:
            pass
