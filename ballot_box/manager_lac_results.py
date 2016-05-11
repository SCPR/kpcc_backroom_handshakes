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
import operator
from bs4 import BeautifulSoup


logger = logging.getLogger("kpcc_backroom_handshakes")


class BuildLacResults(object):
    """Scaffolding to ingest LA County registrar election results."""

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

        # Create list to store raw data
        rows = []

        def retrieve_data():
            """Fetches data rows from file and stores in a list."""
            with open(contest_path, "r") as f:    
                for line in f:
                    record_type = line[3:5]
                    if record_type == "EF":
                        break
                    rows.append(line)

        def get_race_ids_from(rows):
            """Returns index of races using page sequence (one contest or statistical set
            per page).
            """
            list_of_race_ids = []
            for result in rows:
                race_id = result[:3]
                record_type = result[3:5]
                if record_type == "EF":
                    pass
                else:
                    list_of_race_ids.append(race_id)
            set_of_race_ids = set(list_of_race_ids)
            race_ids = list(set_of_race_ids)
            print "\t* Race ids compiled"
            return race_ids

        def collate_races():
            """Groups all records into a dictionary indexed by race_id."""
            race_ids = get_race_ids_from(rows)
            races = {}
            for rid in race_ids:
                race = fetch_records_for_race(rid)
                races[rid] = race
            return races

        def fetch_records_for_race(rid):
            """Pulls all records for a specific contest or stats set."""
            race_rows = []
            for row in rows:
                if row[:3] == rid:
                    race_rows.append(row)
                else:
                    pass
            return race_rows

        def evaluate_and_process_races():
            """This is the primary function handling the parsing."""
            races = collate_races()
            contest_list = []
            candidate_list = []
            measure_list = []
            judicial_list = []
            election_info = {}

            for r in races:
                records = objectify_records(races[r])

                # Identify and process overall election stats
                if r == '000':
                    stats = objectify_records(races['145'])
                    election_info = compile_election_stats(records,stats)

                elif r == '145':
                    pass

                # Process individual contest and candidate info
                else:
                    skip = check_if_recall_or_nonpartisan(records)
                    """Checks to see if this is a recall contest or a nonpartisan contest. For now,
                    it's unclear how to store or display these contests. In future, however, we may
                    want to parse and return their results.
                    """
                    if skip:
                        pass
                    else:
                        contest = compile_contest_results(records)
                        contest_list.append(contest['contest_details'])
                        for measure in contest['measures']:
                            measure_list.append(measure)
                        for candidate in contest['candidates']:
                            candidate_list.append(candidate)
                        for judge in contest['judges']:
                            judicial_list.append(judge)

            #printreport(election_info,contest_list,measure_list,candidate_list,judicial_list)

        # Parse records and return as set of objects
        def objectify_records(race):
            """Parses each record and returns everything as a list of dictionaries. 
            NOTE: Party Statistics (PS) records are not yet represented in our models 
            and are not being parsed. Also, Party Stats in 2016 appear to have been 
            recoded (PC).
            """
            race_package = []
            for r in range(0,len(race)):
                record_type = race[r][3:5]
                if record_type == 'ET':
                    parser = ET_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'TD':
                    parser = TD_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'ST':
                    parser = ST_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'PT':
                    parser = PT_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'CC':
                    parser = CC_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'MC':
                    parser = MC_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'JC':
                    parser = JC_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)
                
                elif record_type == 'CN':
                    parser = CN_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'MT':
                    parser = MT_parser()
                    record = parser.parse_line(race[r])
                    combined_record = {}
                    if 'YES' in record['measure_text']:
                        record2 = parser.parse_line(race[r+1])
                        combined_record['page_sequence'] = record['page_sequence']
                        combined_record['record_type'] = record['record_type']
                        combined_record['contest_id'] = record['contest_id']
                        combined_record['district'] = record['district']
                        combined_record['division'] = record['division']
                        combined_record['measure_id'] = record['measure_id']
                        combined_record['measure_text'] = record['measure_text']
                        combined_record['yes_votes'] = record['votes']
                        combined_record['yes_percent'] = record['percent_of_vote']
                        combined_record['no_votes'] = record2['votes']
                        combined_record['no_percent'] = record2['percent_of_vote']
                        race_package.append(combined_record)
                    else:
                        pass

                elif record_type == 'JN':
                    parser = JN_parser()
                    record = parser.parse_line(race[r])
                    combined_record = {}
                    if 'YES' in record['voting_rule']:
                        record2 = parser.parse_line(race[r+1])
                        combined_record['record_type'] = record['record_type']
                        combined_record['contest_id'] = record['contest_id']
                        combined_record['district'] = record['district']
                        combined_record['division'] = record['division']
                        combined_record['judicial_text'] = record['judicial_text']
                        combined_record['judicial_name'] = record['judicial_name']
                        combined_record['voting_rule'] = record['voting_rule']
                        combined_record['yes_votes'] = record['votes']
                        combined_record['yes_percent'] = record['percent_of_vote']
                        combined_record['no_votes'] = record2['votes']
                        combined_record['no_percent'] = record2['percent_of_vote']
                        race_package.append(combined_record)
                    else:
                        pass

                elif record_type == 'PR':
                    parser = PR_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'DR':
                    parser = DR_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'AB':
                    parser = AB_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

                elif record_type == 'BC':
                    parser = BC_parser()
                    record = parser.parse_line(race[r])
                    combined_record = {}
                    if 'MAIL' in record['ballots_cast_text']:
                        record2 = parser.parse_line(race[r+1])
                        combined_record['record_type'] = record['record_type']
                        combined_record['contest_id'] = record['contest_id']
                        combined_record['district'] = record['district']
                        combined_record['division'] = record['division']
                        combined_record['vote_by_mail_ballots'] = record['ballots_cast']
                        combined_record['ballots_cast'] = record2['ballots_cast']
                        combined_record['percent_turnout'] = record2['percent_turnout']
                        race_package.append(combined_record)
                    else:
                        pass

                elif record_type == 'VF':
                    parser = VF_parser()
                    record = parser.parse_line(race[r])
                    race_package.append(record)

            return race_package

        def check_if_recall_or_nonpartisan(records):
            """ Check to see if this is a recall contest or a nonpartisan contest. For now,
            it's unclear how to store or display these contests. In future, however, we may
            want to parse and return their results.
            """
            recall = False
            nonpartisan = False
            for r in records:
                if r['record_type'] == "MT" and "RECALL" in r['measure_text']:
                    recall = True
                if r['record_type'] == "CC" and "NONPARTISAN" in r['contest_title']:
                    nonpartisan = True
            if recall or nonpartisan:
                return True
            else:
                return False

        def compile_election_stats(title,stats):
            """Fetches records that contain overall election title and stats."""
            election_info = {'description': ''}
            for record in title:
                if record['record_type'] == 'ET':
                    if election_info['description'] == '':
                        election_info['description'] = record['election_text']
                    else:
                        election_info['description'] = election_info['description'] + ' | ' + record['election_text']
                elif record['record_type'] == 'TD':
                    election_info['election_id'] = record['election_id']
                    election_info['time'] = record['time']
                    election_info['date'] = record['date']
            for record in stats:
                if record['record_type'] == 'ST':
                    election_info['statistical_text'] = record['statistical_text']
                    election_info['statistical_text_cont'] = record['statistical_text_cont']

                elif record['record_type'] == 'AB':
                    election_info['absentee_total_text'] = record['absentee_total_text']
                    election_info['absentee_total'] = record['absentee_total']

                elif record['record_type'] == 'BC':
                    election_info['vote_by_mail_ballots'] = record['vote_by_mail_ballots']
                    election_info['ballots_cast'] = record['ballots_cast']
                    election_info['percent_turnout'] = record['percent_turnout']

                elif record['record_type'] == 'PR':
                    if 'ELECTION STATISTICS' in record['record_type']:
                        pass
                    else:
                        election_info['total_precinct_text'] = record['total_precinct_text']
                        election_info['total_precincts'] = record['total_precincts']
                        election_info['precincts_reporting_text'] = record['precincts_reporting_text']
                        election_info['precincts_reporting'] = record['precincts_reporting']
                        election_info['percent_precincts_reporting'] = record['percent_precincts_reporting']

                elif record['record_type'] == 'DR':
                    election_info['registration'] = record['registration']
            return election_info

        def compile_contest_results(records):
            """Fetches records for each contest and returns overall contest info, candidates, 
            measures, etc.
            """
            contest_dictionary = {}
            measure_list = []
            candidate_list = []
            judicial_list = []
            for record in records:
                if record['record_type'] == 'CC':
                    contest_dictionary['page_sequence'] = record['page_sequence']
                    contest_dictionary['contest_id'] = record['contest_id']
                    contest_dictionary['district'] = record['district']
                    contest_dictionary['division'] = record['division']
                    contest_dictionary['party_code'] = record['party_code']
                    contest_dictionary['contest_title'] = record['contest_title']
                    contest_dictionary['contest_title_cont'] = record['contest_title_cont']
                    contest_dictionary['is_ballot_measure'] = False
                    contest_dictionary['is_judicial_contest'] = False

                elif record['record_type'] == 'MC':
                    contest_dictionary['page_sequence'] = record['page_sequence']
                    contest_dictionary['contest_id'] = record['contest_id']
                    contest_dictionary['district'] = record['district']
                    contest_dictionary['division'] = record['division']
                    contest_dictionary['contest_title'] = record['contest_title']
                    contest_dictionary['contest_title_cont'] = record['contest_title_cont']
                    contest_dictionary['is_ballot_measure'] = True
                    contest_dictionary['is_judicial_contest'] = False

                elif record['record_type'] == 'JC':
                    contest_dictionary['page_sequence'] = record['page_sequence']
                    contest_dictionary['contest_id'] = record['contest_id']
                    contest_dictionary['district'] = record['district']
                    contest_dictionary['division'] = record['division']
                    contest_dictionary['contest_title'] = record['contest_title']
                    contest_dictionary['contest_title_cont'] = record['contest_title_cont']
                    contest_dictionary['is_ballot_measure'] = False
                    contest_dictionary['is_judicial_contest'] = True

                elif record['record_type'] == 'PT':
                    contest_dictionary['party_code'] = record['party_code']
                    contest_dictionary['party_name'] = record['party_name']
                
                elif record['record_type'] == 'CN':
                    candidate_dictionary = {}
                    candidate_dictionary['page_sequence'] = record['page_sequence']
                    candidate_dictionary['contest_id'] = record['contest_id']
                    candidate_dictionary['district'] = record['district']
                    candidate_dictionary['division'] = record['division']
                    candidate_dictionary['party_code'] = record['party_code']
                    candidate_dictionary['candidate_name'] = record['candidate_name']
                    candidate_dictionary['party_short'] = record['party_short']
                    candidate_dictionary['votes'] = record['votes']
                    candidate_dictionary['percent_of_vote'] = record['percent_of_vote']
                    candidate_list.append(candidate_dictionary)

                elif record['record_type'] == 'MT':
                    measure_dictionary = {}
                    measure_dictionary['page_sequence'] = record['page_sequence']
                    measure_dictionary['contest_id'] = record['contest_id']
                    measure_dictionary['district'] = record['district']
                    measure_dictionary['division'] = record['division']
                    measure_dictionary['measure_id'] = record['measure_id']
                    measure_dictionary['measure_text'] = record['measure_text'].replace('- YES','').strip()
                    measure_dictionary['yes_votes'] = record['yes_votes']
                    measure_dictionary['yes_percent'] = record['yes_percent']
                    measure_dictionary['no_votes'] = record['no_votes']
                    measure_dictionary['no_percent'] = record['no_percent']
                    measure_list.append(measure_dictionary)

                elif record['record_type'] == 'JN':
                    judge_dictionary = {}
                    judge_dictionary['record_type'] = record['record_type']
                    judge_dictionary['contest_id'] = record['contest_id']
                    judge_dictionary['district'] = record['district']
                    judge_dictionary['division'] = record['division']
                    judge_dictionary['judicial_text'] = record['judicial_text']
                    judge_dictionary['judicial_name'] = record['judicial_name']
                    judge_dictionary['voting_rule'] = record['voting_rule']
                    judge_dictionary['yes_votes'] = record['yes_votes']
                    judge_dictionary['yes_percent'] = record['no_percent']
                    judge_dictionary['no_votes'] = record['no_votes']
                    judge_dictionary['no_percent'] = record['no_percent']
                    judicial_list.append(judge_dictionary)

                elif record['record_type'] == 'PR':
                    contest_dictionary['total_precinct_text'] = record['total_precinct_text']
                    contest_dictionary['total_precincts'] = record['total_precincts']
                    contest_dictionary['precincts_reporting_text'] = record['precincts_reporting_text']
                    contest_dictionary['precincts_reporting'] = record['precincts_reporting']
                    contest_dictionary['percent_precincts_reporting'] = record['percent_precincts_reporting']

                elif record['record_type'] == 'DR':
                    contest_dictionary['registration'] = record['registration']

                elif record['record_type'] == 'VF':
                    contest_dictionary['vote_for_text'] = record['vote_for_text']
                    contest_dictionary['vote_for_number'] = record['vote_for_number']

            contest_package = {'contest_details':contest_dictionary,'candidates':candidate_list,'measures':measure_list,'judges':judicial_list}
            return contest_package
        
        def printreport(election_info,contest_list,measure_list,candidate_list,judicial_list):
            """Prints human readable report of all candidates, contests, measures, and some 
            basic election stats. Activate by un-commenting call in evaluate_and_process_races().
            """
            with open ("%s/ballot_box/data_dump/lac_latest/lac_latest_report.md" % (settings.BASE_DIR), "w+") as f:
                election_desc = election_info['description'].split(' | ')
                for d in election_desc:
                    f.write(d + '\n')
                f.write('\n\n')

                f.write('## BY THE NUMBERS\n\n')
                f.write('__No. of contests:__ ' + str(len(contest_list)) + '\n\n')
                f.write('__No. of measures:__ ' + str(len(measure_list)) + '\n\n')
                f.write('__No. of candidates:__ ' + str(len(candidate_list)) + '\n\n')
                f.write('__No. of judicial appointees:__ ' + str(len(judicial_list)) + '\n')
                f.write('\n\n\n\n')

                f.write('## CONTESTS\n\n')
                for contest in (sorted(contest_list, key=operator.itemgetter('page_sequence'))):
                    f.write('* ' + contest['contest_title'] + ' ' + contest['contest_title_cont'] + '\n')
                f.write('\n\n')

                f.write('## MEASURES\n\n')
                if len(measure_list) > 0:
                    for measure in (sorted(measure_list, key=operator.itemgetter('measure_id'))):
                        contest = ''
                        for c in contest_list:
                            if c['page_sequence'] == measure['page_sequence'] and c['contest_id'] == measure['contest_id'] and c['district'] == measure['district']:
                                contest = c['contest_title']
                        f.write('* ' + measure['measure_id'] + ' - ' + measure['measure_text'] + ' (' + contest + ')\n')
                else:
                    f.write('N/A\n')
                f.write('\n\n')

                f.write('## CANDIDATES\n\n')
                if len(candidate_list) > 0:
                    for candidate in (sorted(candidate_list, key=operator.itemgetter('candidate_name'))):
                        contest = ''
                        for c in contest_list:
                            if c['page_sequence'] == candidate['page_sequence'] and c['contest_id'] == candidate['contest_id'] and c['district'] == candidate['district']:
                                contest = c['contest_title'] + ' ' + c['contest_title_cont']
                        f.write('* ' + candidate['candidate_name'] + ' - ' + contest + '\n')
                else:
                    f.write('N/A\n')
                f.write('\n\n')

                f.write('## JUDICIAL APPOINTEES\n\n')
                if len(judicial_list) > 0:
                    for judge in (sorted(judicial_list, key=operator.itemgetter('judicial_name'))):
                        f.write('* ' + judge['judicial_name'] + ' - ' + judge['judicial_text'] + '\n')
                else:
                    f.write('N/A\n')

        def return_structured_data():
            """Triggers data retrieval and parsing."""
            retrieve_data()
            evaluate_and_process_races()

        return_structured_data()

if __name__ == '__main__':
    task_run = BuildLacResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
