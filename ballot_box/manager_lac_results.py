from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from ballot_box.utils_files import Retriever
from ballot_box.models import ResultSource
from ballot_box.lac_schemas import *
import logging
import time
import datetime
import os.path
import shutil
from bs4 import BeautifulSoup


logger = logging.getLogger("kpcc_backroom_handshakes")


class BuildLacResults(object):
    """
    scaffolding to ingest secretary of state election results
    """

    retrieve = Retriever()

    data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    contest_file = "internet.dat"

    date_object = datetime.datetime.now()

    date_string = date_object.strftime("%Y_%m_%d_%H_%M_%S")

    src = ResultSource.objects.filter(source_short="lac", source_active=True)

    def _init(self, *args, **kwargs):
        """
        """
        item = self.src[0]
        item.file_name = "%s_%s_%s_results%s" % (self.data_directory, self.date_string, item.source_short, item.source_type)
        # self.get_results_file(item, self.data_directory)
        self.parse_results_file(item, self.data_directory)


    def get_results_file(self, item, data_directory):
        """
        """

        # download the latest results file
        self.retrieve._successful_save_results(item)

        # compare files in a zipfile with a list of expected files
        # self.retrieve._found_files_in_zipfile(item)

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
        # self.retrieve._unzip_latest_file(item, self.data_directory)

    def parse_results_file(self, item, data_directory):
        """
        """
        latest = "%s_latest" % (item.source_short)

        latest_path = os.path.join(data_directory, latest)

        contest_path = os.path.join(latest_path, item.source_files)

        def get_race_ids_from(rows):
            """ loop through file and try to parse out race ids """
            list_of_race_ids = []
            for result in rows:
                race_id = result[:3]
                record_type = result[3:5]
                if race_id == "000" or record_type == "EF":
                    pass
                else:
                    list_of_race_ids.append(race_id)
            set_of_race_ids = set(list_of_race_ids)
            race_ids = list(set_of_race_ids)
            print "\t* Race ids compiled"
            return race_ids

        rows = []

        # Get data from file
        with open(contest_path, "r") as f:    
            for line in f:
                record_type = line[3:5]
                if record_type == "EF":
                    break
                rows.append(line)

        race_ids = get_race_ids_from(rows)
        print race_ids
        for line in rows:
            record_type = line[3:5]
            #if record_type = 
            #parsed = self._result_parser.parse_line(line)
        # print f


    #     def get_race_ids_from(file):
    #     def get_data_for_a_race(race_ids, file):
    #     def evaluate_result_types(id, file, race_data_list):
    #     def evaluate_supreme_court_races(file, id):
    #     def evaluate_ballot_measures(file, id):


if __name__ == '__main__':
    task_run = BuildLacResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
