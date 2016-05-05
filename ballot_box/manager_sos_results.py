from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from ballot_box.utils_files import Retriever
from ballot_box.models import ResultSource
import logging
import time
import datetime
import os.path
import shutil

logger = logging.getLogger("kpcc_backroom_handshakes")

class BuildSosResults(object):
    """
    scaffolding to ingest secretary of state election results
    """

    retrieve = Retriever()

    data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    date_object = datetime.datetime.now()

    date_string = date_object.strftime("%Y_%m_%d_%H_%M_%S")

    src = ResultSource.objects.filter(source_short="sos", source_active=True)

    def _init(self, *args, **kwargs):
        """
        """
        item = self.src[0]
        item.file_name = "%s_%s_%s_results%s" % (self.data_directory, self.date_string, item.source_short, item.source_type)
        self.get_results(item, self.data_directory)


    def get_get_results(self, item, data_directory):
        """
        """

        # download the latest results file
        self.retrieve._successful_save_results(item)

        # compare files in a zipfile with a list of expected files
        self.retrieve._found_files_in_zipfile(item)

        # create timestamped version of a file deemed latest
        self.retrieve._copy_timestamped_file_as_latest(item, self.data_directory)

        # save path to timestamped version of a filein the db
        """
        """

        # move latest files to a working directory
        self.retrieve._create_directory_for_latest_file(item, self.data_directory)

        # move timestamped file to working directory as latest
        self.retrieve._move_latest_files_to_latest_directory(item, self.data_directory)

        # move timestamped zipfile to archives
        self.retrieve._archive_downloaded_file(item, self.data_directory)

        # if the item is a zipfile extract the files
        self.retrieve._unzip_latest_file(item, self.data_directory)











if __name__ == '__main__':
    task_run = BuildSosResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
