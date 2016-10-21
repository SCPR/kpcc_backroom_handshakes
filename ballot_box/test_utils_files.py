from django.test import TestCase
from django.conf import settings
from election_registrar.models import ResultSource
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
import glob

logger = logging.getLogger("kpcc_backroom_handshakes")

# create your tests here


class TestFileRetrival(TestCase):
    """
    a series of reusable methods we'll need for downloading and moving files
    """

    fixtures = ['election_registrar/fixtures/election_registrar.json']

    def setUp(self):
        """
        setup some variables for our tests
        """
        self.date_object = datetime.datetime.now()
        self.date_string = self.date_object.strftime("%Y_%m_%d_%H_%M_%S")
        self.sources = ResultSource.objects.all()

    def test_a_download_chain(self):
        """
        initiate a series of functions based on a list of data sources that will eventually be defined in the database
        """
        logger.debug("running file download tests")
        data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)
        for src in self.sources:
            if src.source_active == True:
                self.Test_request_results_and_save(src, data_directory)
                self.Test_create_directory_for_latest_file(src, data_directory)
                self.Test_copy_timestamped_file_to_latest(src, data_directory)
                self.Test_archive_downloaded_file(src, data_directory)
                self.Test_found_required_files(src, data_directory)
                self.Test_unzip_latest_file(src, data_directory)
            else:
                pass

    def Test_request_results_and_save(self, src, data_directory):
        """
        can i take the response from url can and write it to a timestamped version of the a file that should work no matter the file. it's  based on the file_ext specified in a config dict
        """

        # test_urls = [
            # "https://httpbin.org/status/200",
            # "https://httpbin.org/gzip",
            # "https://httpbin.org/status/404",
            # "https://httpbin.org/status/500",
            # "https://httpbin.org/status/502",
            # "https://httpbin.org/status/503",
            # "https://httpbin.org/status/504",
            # "https://httpbin.org/redirect/10",
            # "https://httpbin.org/delay/9",
            # "https://httpbin.org/delay/11",
        # ]
        # src.source_url = test_urls[0]
        # this_file = os.path.basename("X16DPv7.zip")

        this_file = os.path.basename(src.source_url)

        this_file = "_%s_%s_%s" % (self.date_string, src.source_short, this_file)

        self.file_name = os.path.join(data_directory, this_file)

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
            self.assertEquals(response.status_code, 200)
            self.assertIsNotNone(response.content)
            with open(self.file_name, "wb") as output:
                output.write(response.content)

        except requests.exceptions.ReadTimeout as exception:
            # maybe set up for a retry, or continue in a retry loop
            logger.error("%s: %s" % (exception, src.source_url))
            logger.error("will need to setup retry and then access archived file")
            failsafe = self.Test_return_archived_file(src, data_directory)
            if failsafe:
                logger.info("failsafe successful")
                shutil.copyfile(failsafe, self.file_name)
            else:
                raise

        except requests.exceptions.ConnectionError as exception:
            # incorrect domain
            logger.error("will need to raise message that we can't connect")
            logger.error("%s: %s" % (exception, src.source_url))
            raise

        except requests.exceptions.HTTPError as exception:
            # http error occurred
            logger.error("%s: %s" % (exception, src.source_url))
            logger.error("trying to access archived file via failsafe")
            failsafe = self.Test_return_archived_file(src, data_directory)
            if failsafe:
                logger.info("failsafe successful")
                shutil.copyfile(failsafe, self.file_name)
            else:
                raise

        except requests.exceptions.URLRequired as exception:
            # valid URL is required to make a request
            logger.error("%s: %s" % (exception, src.source_url))
            logger.error("will need to raise message that URL is broken")
            failsafe = self.Test_return_archived_file(src, data_directory)
            if failsafe:
                logger.info("failsafe successful")
                shutil.copyfile(failsafe, self.file_name)
            else:
                raise

        except requests.exceptions.TooManyRedirects as exception:
            # tell the user their url was bad and try a different one
            logger.error("%s: %s" % (exception, src.source_url))
            logger.error("will need to raise message that URL is broken")
            failsafe = self.Test_return_archived_file(src, data_directory)
            if failsafe:
                logger.info("failsafe successful")
                shutil.copyfile(failsafe, self.file_name)
            else:
                raise

        except requests.exceptions.RequestException as exception:
            # ambiguous exception
            logger.error("%s: %s" % (exception, src.source_url))
            logger.error("trying to access archived file via failsafe")
            failsafe = self.Test_return_archived_file(src, data_directory)
            if failsafe:
                logger.info("failsafe successful")
                shutil.copyfile(failsafe, self.file_name)
            else:
                raise

        file_exists = os.path.isfile(self.file_name)
        file_has_size = os.path.getsize(self.file_name)
        self.assertEquals(file_exists, True)
        if file_exists == True:
            logger.debug("Success! %s exists" % (self.file_name))
            self.assertTrue(file_has_size > 0)
            if file_has_size > 0:
                logger.debug("Success! %s is valid" % (self.file_name))
            else:
                logger.debug("Failure! %s isn't valid" % (self.file_name))
                raise Exception
        else:
            logger.debug("Failure! %s doesn't exist" % (self.file_name))
            raise Exception

    def Test_create_directory_for_latest_file(self, src, data_directory):
        """
        move latest files to a working directory
        """
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        dir_exists = os.path.isdir(latest_directory)
        if dir_exists == True:
            logger.debug("Skipping because %s already exists" % (latest_directory))
        else:
            try:
                os.makedirs(latest_directory)
                logger.debug("Success! We created %s" % (latest_directory))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def Test_copy_timestamped_file_to_latest(self, src, data_directory):
        """
        create timestamped version of a file deemed latest
        """
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        this_file = "%s%s" % (src.source_slug, src.source_type)
        latest_path = os.path.join(latest_directory, this_file)
        try:
            shutil.copyfile(self.file_name, latest_path)
            file_exists = os.path.isfile(latest_path)
            self.assertEquals(file_exists, True)
            logger.debug("Success! %s exists" % (self.file_name))
        except Exception, exception:
            logger.error(exception)
            raise

    def Test_archive_downloaded_file(self, src, data_directory):
        """
        move timestamped zipfile to archives
        """
        archives = "%s_archived_files" % (data_directory)
        try:
            os.makedirs(archives)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        shutil.move(self.file_name, archives)
        file_exists = os.path.isfile(self.file_name)
        self.assertEquals(file_exists, False)
        logger.debug("Success! %s exists" % (self.file_name))

    def Test_found_required_files(self, src, data_directory):
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
                        self.assertEquals(file in set(files), True)
                        logger.debug("Success: %s exists" % (file))
            except Exception, exception:
                logger.error(exception)
        else:
            try:
                for file in src.source_files.split(", "):
                    self.assertEquals(file, os.path.basename(latest_path))
                    logger.debug("Success: %s exists" % (file))
            except Exception, exception:
                logger.error(exception)
                raise

    def Test_unzip_latest_file(self, src, data_directory):
        """
        if the src is a zipfile can I extract the files?
        """
        if src.source_type == ".zip":
            latest_directory = "%s%s_latest" % (
                data_directory, src.source_short)
            this_file = "%s%s" % (src.source_slug, src.source_type)
            latest_path = os.path.join(latest_directory, this_file)
            with zipfile.ZipFile(latest_path) as zip:
                self.assertIsNone(zipfile.ZipFile.testzip(zip))
                for file in src.source_files.split(", "):
                    zip.extract(file, latest_directory)
                    file_exists = os.path.isfile(
                        os.path.join(latest_directory, file))
                    self.assertEquals(file_exists, True)
                    logger.debug("Success: %s exists" % (file))
            os.remove(latest_path)
            file_exists = os.path.isfile(latest_path)
            self.assertEquals(file_exists, False)
            logger.debug("%s successfully removed" % (os.path.basename(latest_path)))
        else:
            pass

    def Test_return_archived_file(self, src, data_directory):
        this_file = os.path.basename(src.source_url)
        this_file = "X16DPv7.zip"
        archives = "%s_archived_files" % (data_directory)
        dir_exists = os.path.isdir(archives)
        self.assertEquals(dir_exists, True)
        glob_path = "%s/*%s" % (archives, src.source_type)
        archived_files = sorted(glob.glob(glob_path), key=os.path.getmtime, reverse=True)
        done = False
        for file in archived_files:
            file_base = os.path.basename(file).split("_%s_" % (src.source_short))
            while not done:
                if str(file_base[1]) == this_file:
                    done = True
                    return file
                else:
                    done = False
                    return False
