# -*- coding: utf-8 -*-

from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime
from ballot_box.utils_files import Retriever
from ballot_box.utils_data import Framer, Namefixer
from ballot_box.utils_import import Saver
from ballot_box.lac_schemas import *
from election_registrar.models import ResultSource, Election
import logging
import time
import datetime
import os.path
import shutil
import operator
import re
from bs4 import BeautifulSoup
from delorean import parse
from slugify import slugify

logger = logging.getLogger("kpcc_backroom_handshakes")


class BuildLacResults(object):
    """
    scaffolding to ingest la county registrar election results
    """

    retrieve = Retriever()

    data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    sources = ResultSource.objects.filter(source_short="lac", source_active=True)

    elections = Election.objects.all().order_by("-election_date")

    testing = elections[0].test_results

    def _init(self, *args, **kwargs):
        """
        """
        for src in self.sources:
            self.get_results_file(src, self.data_directory)
            self.parse_results_file(src, self.data_directory)
            src.ready_to_build = True
            src.save(update_fields=["ready_to_build"])

    def get_results_file(self, src, data_directory):
        """
        """
        self.retrieve._request_results_and_save(src, data_directory)
        self.retrieve._create_directory_for_latest_file(src, data_directory)
        self.retrieve._copy_timestamped_file_to_latest(src, data_directory)
        self.retrieve._archive_downloaded_file(src, data_directory)
        self.retrieve._found_required_files(src, data_directory)
        self.retrieve._unzip_latest_file(src, data_directory)
        self.retrieve.log_message += "*** Ending Request ***\n"
        logger.info(self.retrieve.log_message)

    def parse_results_file(self, src, data_directory):
        """
        """
        saver = Saver()
        process = LacProcessMethods()
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        election = Election.objects.filter(electionid=src.election.electionid).first()
        for file in src.source_files.split(", "):
            latest_path = os.path.join(latest_directory, file)
            file_exists = os.path.isfile(latest_path)
            file_has_size = os.path.getsize(latest_path)
            if file_exists == True and file_has_size > 0:
                rows = process.open_results_file(latest_path)


                race_ids = process.get_race_ids_from(rows)
                election_package = process.collate_and_fetch_records_for_race(race_ids, rows)
                races = election_package[0]
                election_title = election_package[1]["title"]
                election_stats = election_package[1]["stats"]
                file_timestring = None
                file_timestamp = None
                for t in election_title:
                    if t[3:5] == "TD":
                        parser = TD_parser()
                        parsed = parser.parse_line(t)
                        timestring = parsed["date"] + " " + parsed["time"]
                        file_timestring = timestring
                if file_timestring:
                    file_timestamp = parse(file_timestring, dayfirst=False).datetime
                    file_timestamp = localtime(file_timestamp)
                    if self.testing == True:
                        update_this = self.testing
                    else:
                        # update_this = saver._eval_timestamps(file_timestamp, src.source_latest)
                        update_this = True
                    if update_this == False:
                        logger.info("\n*****\nwe have newer data in the database so let's delete these files\n*****")
                        os.remove(latest_path)
                    else:
                        logger.info("\n*****\nwe have new data to save and we'll update timestamps in the database\n*****")
                        saver._update_result_timestamps(src, file_timestamp)
                        title = process.dictify_records_and_return(election_title)
                        stats = process.dictify_records_and_return(election_stats)
                        election_info = process.compile_election_stats(title, stats)
                        for r in races:
                            records = process.dictify_records_and_return(races[r])
                            """
                            checks to see if this is a recall contest or a nonpartisan contest
                            for now, it's unclear how to store or display these contests
                            in future, however, we may want to parse and return their results
                            """
                            skip = process.check_if_recall_or_nonpartisan(records)
                            if skip:
                                pass
                            else:
                                contest_package = process.compile_contest_results(records)
                                process.update_database(contest_package, election, src)
                #         os.remove(latest_path)
                #         logger.info("we've finished processing lac results")
                # else:
                #     logger.error("unable to determine whether this data is newer than what we already have.")


class LacProcessMethods(object):
    """
    """

    def open_results_file(self, file):
        """
        """
        rows = []
        with open(file, "r") as f:
            for line in f:
                record_type = line[3:5]
                if record_type == "EF":
                    break
                else:
                    rows.append(line)
        return rows

    def get_race_ids_from(self, rows):
        """
        returns index of races using page sequence (one contest or statistical set per page).
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
        return race_ids

    def collate_and_fetch_records_for_race(self, race_ids, rows):
        races = {}
        election_info = {"title": [], "stats": []}
        title_rid = None
        stats_rid = None
        for row in rows:
            if row[3:5] == "ET" or row[3:5] == "TD":
                election_info["title"].append(row)
                if title_rid == None:
                    title_rid = row[:3]
            elif row[5:9] == "STAT":
                election_info["stats"].append(row)
                if stats_rid == None:
                    stats_rid = row[:3]
            else:
                pass

        for rid in race_ids:
            if rid == title_rid or rid == stats_rid:
                pass
            else:
                race_rows = []
                for row in rows:
                    if row[:3] == rid:
                        race_rows.append(row)
                    else:
                        pass
                races[rid] = race_rows
        return [races, election_info]

    def dictify_records_and_return(self, race):
        """Parses each record and returns everything as a list of dictionaries.
        NOTE: Party Statistics (PS) records are not yet represented in our models
        and are not being parsed. Also, Party Stats in 2016 appear to have been
        recoded (PC).
        """
        race_package = []
        for r in range(0, len(race)):
            record_type = race[r][3:5]

            # https://stackoverflow.com/questions/3951840/python-how-to-invoke-an-function-on-an-object-dynamically-by-name
            if record_type == "ET":
                parser = ET_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "TD":
                parser = TD_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "ST":
                parser = ST_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "PT":
                parser = PT_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "CC":
                parser = CC_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "MC":
                parser = MC_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "JC":
                parser = JC_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "CN":
                parser = CN_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "MT":
                parser = MT_parser()
                record = parser.parse_line(race[r])
                combined_record = {}
                if "YES" in record["measure_text"]:
                    record2 = parser.parse_line(race[r + 1])
                    combined_record["page_sequence"] = record["page_sequence"]
                    combined_record["record_type"] = record["record_type"]
                    combined_record["contest_id"] = record["contest_id"]
                    combined_record["district"] = record["district"]
                    combined_record["division"] = record["division"]
                    combined_record["measure_id"] = record["measure_id"]
                    combined_record["measure_text"] = record["measure_text"]
                    combined_record["yes_votes"] = record["votes"]
                    combined_record["yes_percent"] = record["percent_of_vote"]
                    combined_record["no_votes"] = record2["votes"]
                    combined_record["no_percent"] = record2["percent_of_vote"]
                    race_package.append(combined_record)
                else:
                    pass

            elif record_type == "JN":
                parser = JN_parser()
                record = parser.parse_line(race[r])
                combined_record = {}
                if "YES" in record["voting_rule"]:
                    record2 = parser.parse_line(race[r + 1])
                    combined_record["record_type"] = record["record_type"]
                    combined_record["contest_id"] = record["contest_id"]
                    combined_record["district"] = record["district"]
                    combined_record["division"] = record["division"]
                    combined_record["judicial_text"] = record["judicial_text"]
                    combined_record["judicial_name"] = record["judicial_name"]
                    combined_record["voting_rule"] = record["voting_rule"]
                    combined_record["yes_votes"] = record["votes"]
                    combined_record["yes_percent"] = record["percent_of_vote"]
                    combined_record["no_votes"] = record2["votes"]
                    combined_record["no_percent"] = record2["percent_of_vote"]
                    race_package.append(combined_record)
                else:
                    pass

            elif record_type == "PR":
                parser = PR_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "DR":
                parser = DR_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "AB":
                parser = AB_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

            elif record_type == "BC":
                parser = BC_parser()
                record = parser.parse_line(race[r])
                combined_record = {}
                if "MAIL" in record["ballots_cast_text"]:
                    record2 = parser.parse_line(race[r + 1])
                    combined_record["record_type"] = record["record_type"]
                    combined_record["contest_id"] = record["contest_id"]
                    combined_record["district"] = record["district"]
                    combined_record["division"] = record["division"]
                    combined_record["vote_by_mail_ballots"] = record[
                        "ballots_cast"]
                    combined_record["ballots_cast"] = record2["ballots_cast"]
                    combined_record["percent_turnout"] = record2[
                        "percent_turnout"]
                    race_package.append(combined_record)
                else:
                    pass

            elif record_type == "VF":
                parser = VF_parser()
                record = parser.parse_line(race[r])
                race_package.append(record)

        return race_package

    def compile_election_stats(self, title, stats):
        """Fetches records that contain overall election title and stats."""
        election_info = {"description": ""}
        for record in title:
            if record["record_type"] == "ET":
                if election_info["description"] == "":
                    election_info["description"] = record["election_text"]
                else:
                    election_info["description"] = election_info[
                        "description"] + " | " + record["election_text"]
            elif record["record_type"] == "TD":
                election_info["election_id"] = record["election_id"]
                election_info["time"] = record["time"]
                election_info["date"] = record["date"]
        for record in stats:
            if record["record_type"] == "ST":
                election_info["statistical_text"] = record["statistical_text"]
                election_info["statistical_text_cont"] = record["statistical_text_cont"]

            elif record["record_type"] == "AB":
                election_info["absentee_total_text"] = record["absentee_total_text"]
                election_info["absentee_total"] = record["absentee_total"].replace(",", "")

            elif record["record_type"] == "BC":
                election_info["vote_by_mail_ballots"] = record["vote_by_mail_ballots"].replace(",", "")
                election_info["ballots_cast"] = record["ballots_cast"].replace(",", "")
                election_info["percent_turnout"] = record["percent_turnout"]

            elif record["record_type"] == "PR":
                if "ELECTION STATISTICS" in record["record_type"]:
                    pass
                else:
                    election_info["total_precinct_text"] = record["total_precinct_text"]
                    election_info["total_precincts"] = record["total_precincts"].replace(",", "")
                    election_info["precincts_reporting_text"] = record["precincts_reporting_text"]
                    election_info["precincts_reporting"] = record["precincts_reporting"].replace(",", "")
                    election_info["percent_precincts_reporting"] = record["percent_precincts_reporting"]

            elif record["record_type"] == "DR":
                election_info["registration"] = record["registration"]
        return election_info

    def compile_contest_results(self, records):
        """
        fetches records for each contest and returns overall contest info,candidates, measures, etc.
        """
        contest = {}
        measures = []
        candidates = []
        judge_candidates = []
        for record in records:
            if record["record_type"] == "CC":
                contest["page_sequence"] = record["page_sequence"]
                contest["contest_id"] = record["contest_id"]
                contest["district"] = record["district"]
                contest["division"] = record["division"]
                contest["party_code"] = record["party_code"]
                contest["contest_title"] = record["contest_title"]
                contest["contest_title_cont"] = record["contest_title_cont"]
                contest["is_ballot_measure"] = False
                contest["is_judicial_contest"] = False
            elif record["record_type"] == "MC":
                contest["page_sequence"] = record["page_sequence"]
                contest["contest_id"] = record["contest_id"]
                contest["district"] = record["district"]
                contest["division"] = record["division"]
                contest["contest_title"] = record["contest_title"]
                contest["contest_title_cont"] = record["contest_title_cont"]
                contest["is_ballot_measure"] = True
                contest["is_judicial_contest"] = False
            elif record["record_type"] == "JC":
                contest["page_sequence"] = record["page_sequence"]
                contest["contest_id"] = record["contest_id"]
                contest["district"] = record["district"]
                contest["division"] = record["division"]
                contest["contest_title"] = record["contest_title"]
                contest["contest_title_cont"] = record["contest_title_cont"]
                contest["is_ballot_measure"] = False
                contest["is_judicial_contest"] = True
            elif record["record_type"] == "PT":
                contest["party_code"] = record["party_code"]
                contest["party_name"] = record["party_name"]
            elif record["record_type"] == "CN":
                candidate = {}
                candidate["page_sequence"] = record["page_sequence"]
                candidate["contest_id"] = record["contest_id"]
                candidate["district"] = record["district"]
                candidate["division"] = record["division"]
                candidate["party_code"] = record["party_code"]
                candidate["candidate_name"] = record["candidate_name"]
                candidate["party_short"] = record["party_short"]
                candidate["votes"] = record["votes"].replace(",", "")
                candidate["percent_of_vote"] = record["percent_of_vote"]
                candidates.append(candidate)
            elif record["record_type"] == "MT":
                measure = {}
                measure["page_sequence"] = record["page_sequence"]
                measure["contest_id"] = record["contest_id"]
                measure["district"] = record["district"]
                measure["division"] = record["division"]
                measure["measure_id"] = record["measure_id"]
                measure["measure_text"] = record["measure_text"].replace("- YES", "").strip()
                measure["yes_votes"] = record["yes_votes"].replace(",", "")
                measure["yes_percent"] = record["yes_percent"]
                measure["no_votes"] = record["no_votes"].replace(",", "")
                measure["no_percent"] = record["no_percent"]
                measures.append(measure)
            elif record["record_type"] == "JN":
                judge_candidate = {}
                judge_candidate["record_type"] = record["record_type"]
                judge_candidate["contest_id"] = record["contest_id"]
                judge_candidate["district"] = record["district"]
                judge_candidate["division"] = record["division"]
                judge_candidate["judicial_text"] = record["judicial_text"]
                judge_candidate["judicial_name"] = record["judicial_name"]
                judge_candidate["voting_rule"] = record["voting_rule"]
                judge_candidate["yes_votes"] = record["yes_votes"].replace(",", "")
                judge_candidate["yes_percent"] = record["yes_percent"]
                judge_candidate["no_votes"] = record["no_votes"].replace(",", "")
                judge_candidate["no_percent"] = record["no_percent"]
                judge_candidates.append(judge_candidate)
            elif record["record_type"] == "PR":
                contest["total_precinct_text"] = record["total_precinct_text"]
                contest["total_precincts"] = record["total_precincts"].replace(",", "")
                contest["precincts_reporting_text"] = record["precincts_reporting_text"]
                contest["precincts_reporting"] = record["precincts_reporting"].replace(",", "")
                contest["percent_precincts_reporting"] = record["percent_precincts_reporting"]
            elif record["record_type"] == "DR":
                contest["registration"] = record["registration"].replace(",", "")
            elif record["record_type"] == "VF":
                contest["vote_for_text"] = record["vote_for_text"]
                contest["vote_for_number"] = record["vote_for_number"]
        contest_package = {
            "contest_details": contest,
            "candidates": candidates,
            "measures": measures,
            "judges": judge_candidates,
        }
        return contest_package

    def update_database(self, contest_package, election, src):
        """ import candidates, measures, office and contest info from compiled data """
        saver = Saver()
        framer = Framer()
        fixer = Namefixer()
        county_name = "Los Angeles County"
        contest = contest_package["contest_details"]
        candidates = contest_package["candidates"]
        measures = contest_package["measures"]
        judges = contest_package["judges"]
        race_log = "\n"
        # """
        # Check level of contest (i.e. local, statewide)
        # """
        if "U.S." in contest["contest_title"] or "STATE" in contest["contest_title"]:
            level = "county"
            framer.contest["is_statewide"] = True
        else:
            level = "county"
            framer.contest["is_statewide"] = False
        framer.contest["level"] = level
        if contest["is_judicial_contest"]:
            """
            This is a judicial appointee
            """
            if "SUPREME COURT" in contest["contest_title"]:
                contestname = "Supreme Court"
            elif "APPELLATE COURT" in contest["contest_title"]:
                contestname = "Courts of Appeal District 02"
            else:
                contestname = contest["contest_title"]
            officename = contestname
            framer.office["officename"] = officename
            framer.office["officeslug"] = slugify(officename)
            framer.office["active"] = True
            framer.office["officeid"] = framer.office["officeslug"]
            framer.contest["election_id"] = election.id
            framer.contest["resultsource_id"] = src.id
            framer.contest["seatnum"] = None
            framer.contest["is_uncontested"] = False
            framer.contest["is_national"] = False
            framer.contest["is_statewide"] = True
            framer.contest["level"] = "county"
            framer.contest["is_ballot_measure"] = False
            framer.contest["is_judicial"] = True
            framer.contest["is_runoff"] = False
            framer.contest["reporttype"] = None
            framer.contest["poss_error"] = False
            if framer._to_num(contest["total_precincts"])["convert"] == True:
                pt = framer._to_num(contest["total_precincts"])["value"]
                framer.contest["precinctstotal"] = pt
            else:
                framer.contest["precinctstotal"] = None
                raise Exception("precinctstotal is not a number")
            if framer._to_num(contest["precincts_reporting"])["convert"] == True:
                pr = framer._to_num(contest["precincts_reporting"])["value"]
                framer.contest["precinctsreporting"] = pr
            else:
                framer.contest["precinctsreporting"] = None
                raise Exception("precinctsreporting is not a number")
            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                framer.contest["precinctsreporting"],
                framer.contest["precinctstotal"]
            )
            if framer._to_num(contest["registration"])["convert"] == True:
                framer.contest["votersregistered"] = framer._to_num(
                    contest["registration"])["value"]
            else:
                framer.contest["votersregistered"] = None
                raise Exception("votersregistered is not a number")
            framer.contest["votersturnout"] = None
            framer.contest["contestname"] = fixer._fix(contestname)
            framer.contest["contestdescription"] = None
            framer.contest["contestid"] = saver._make_contest_id(
                src.source_short,
                framer.contest["level"],
                framer.office["officeslug"],
            )
            race_log += saver.make_office(framer.office)
            race_log += saver.make_contest(framer.office, framer.contest)
            for judge in judges:
                fullname = fixer._titlecase_with_accents(judge["judicial_name"].encode('utf8'))
                framer.judicial["firstname"] = None
                framer.judicial["lastname"] = None
                framer.judicial["ballotorder"] = None
                framer.judicial["fullname"] = fullname
                framer.judicial["judicialslug"] = slugify(fullname)
                framer.judicial["description"] = judge["judicial_text"].title()
                framer.judicial["poss_error"] = False
                if framer._to_num(judge["yes_votes"])["convert"] == True:
                    yescount = framer._to_num(judge["yes_votes"])["value"]
                    framer.judicial["yescount"] = yescount
                else:
                    framer.judicial["yescount"] = None
                    raise Exception("yescount is not a number")
                if framer._to_num(judge["yes_percent"])["convert"] == True:
                    yespct = framer._to_num(judge["yes_percent"])["value"]
                    framer.judicial["yespct"] = yespct
                else:
                    framer.judicial["yespct"] = None
                    raise Exception("yespct is not a number")
                if framer._to_num(judge["no_votes"])["convert"] == True:
                    nocount = framer._to_num(judge["no_votes"])["value"]
                    framer.judicial["nocount"] = nocount
                else:
                    framer.judicial["nocount"] = None
                    raise Exception("nocount is not a number")
                if framer._to_num(judge["no_percent"])["convert"] == True:
                    nopct = framer._to_num(judge["no_percent"])["value"]
                    framer.judicial["nopct"] = nopct
                else:
                    framer.judicial["nopct"] = None
                    raise Exception("nopct is not a number")
                framer.judicial["judgeid"] = saver._make_this_id(
                    "judicial",
                    framer.contest["contestid"],
                    framer.judicial["judicialslug"],
                )
                race_log += saver.make_judicial(framer.contest, framer.judicial)
        elif contest["is_ballot_measure"]:
            """
            this is a ballot measure
            """
            framer.contest["level"] = "county"
            framer.contest["is_statewide"] = False
            contestname = contest["contest_title"]
            if contest["contest_id"] == "00":
                if contestname == "COUNTY MEASURE A":
                    this_type = "Measure"
                    contestname = "%swide" % (county_name)
                    contest["contest_title_cont"] = "Measure A"
                else:
                    this_type = "Proposition"
                contestname = contestname.replace("STATE MEASURE", "Proposition")
            else:
                this_type = "Measure"
                contestname = fixer._fix(contestname)
            contestname = contestname.title()
            if contestname == "Metro Transportation Authority":
                contestname = "%swide" % (county_name)
            if contest["contest_title_cont"]:
                fullname = (contest["contest_title_cont"]).replace("MEASURE", "Measure")
            else:
                fullname = contestname
            if contest["contest_id"] == "00":
                description = None
                officename = framer._concat(
                    # this_type,
                    contestname,
                    delimiter="-",
                )
            else:
                description = "%s %s" % (contestname, this_type)
                officename = framer._concat(
                    # this_type,
                    contestname,
                    delimiter="-",
                )
            framer.office["officename"] = officename
            framer.office["officeslug"] = slugify(officename)
            framer.office["active"] = True
            framer.office["officeid"] = framer.office["officeslug"]
            framer.contest["election_id"] = election.id
            framer.contest["resultsource_id"] = src.id
            framer.contest["seatnum"] = None
            framer.contest["is_uncontested"] = False
            framer.contest["is_national"] = False
            framer.contest["is_ballot_measure"] = True
            framer.contest["is_judicial"] = False
            framer.contest["is_runoff"] = False
            framer.contest["reporttype"] = None
            framer.contest["poss_error"] = False
            if framer._to_num(contest["total_precincts"])["convert"] == True:
                pt = framer._to_num(contest["total_precincts"])["value"]
                framer.contest["precinctstotal"] = pt
            else:
                framer.contest["precinctstotal"] = None
                raise Exception("precinctstotal is not a number")
            if framer._to_num(contest["precincts_reporting"])["convert"] == True:
                pr = framer._to_num(contest["precincts_reporting"])["value"]
                framer.contest["precinctsreporting"] = pr
            else:
                framer.contest["precinctsreporting"] = None
                raise Exception("precinctsreporting is not a number")
            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                framer.contest["precinctsreporting"],
                framer.contest["precinctstotal"]
            )
            if framer._to_num(contest["registration"])["convert"] == True:
                framer.contest["votersregistered"] = framer._to_num(
                    contest["registration"])["value"]
            else:
                framer.contest["votersregistered"] = None
                raise Exception(
                    "votersregistered is not a number")
            framer.contest["votersturnout"] = None
            framer.contest["contestname"] = contestname
            framer.contest["contestdescription"] = description
            framer.contest["contestid"] = saver._make_contest_id(
                # election.electionid,
                src.source_short,
                framer.contest["level"],
                framer.office["officeslug"],
            )
            race_log += saver.make_office(framer.office)
            race_log += saver.make_contest(framer.office, framer.contest)
            for measure in measures:
                framer.measure["ballotorder"] = None
                framer.measure["fullname"] = fullname
                framer.measure["measureslug"] = slugify(fullname)
                framer.measure["description"] = measure["measure_text"].title()
                framer.measure["poss_error"] = False
                if framer._to_num(measure["yes_votes"])["convert"] == True:
                    yescount = framer._to_num(measure["yes_votes"])["value"]
                    framer.measure["yescount"] = yescount
                else:
                    framer.measure["yescount"] = None
                    raise Exception("yescount is not a number")
                if framer._to_num(measure["yes_percent"])["convert"] == True:
                    yespct = framer._to_num(measure["yes_percent"])["value"]
                    framer.measure["yespct"] = yespct
                else:
                    framer.measure["yespct"] = None
                    raise Exception("yespct is not a number")
                if framer._to_num(measure["no_votes"])["convert"] == True:
                    nocount = framer._to_num(measure["no_votes"])["value"]
                    framer.measure["nocount"] = nocount
                else:
                    framer.measure["nocount"] = None
                    raise Exception("nocount is not a number")
                if framer._to_num(measure["no_percent"])["convert"] == True:
                    nopct = framer._to_num(measure["no_percent"])["value"]
                    framer.measure["nopct"] = nopct
                else:
                    framer.measure["nopct"] = None
                    raise Exception("nopct is not a number")
                if this_type == "Proposition":
                    framer.measure["measureid"] = saver._make_this_id(
                        "measure",
                        "%s-%s" % (src.source_short, framer.contest["level"]),
                        "%s-%s" % (this_type.lower(), measure["measure_id"].lower())
                    )
                else:
                    framer.measure["measureid"] = saver._make_this_id(
                        "measure",
                        framer.contest["contestid"],
                        "%s-%s" % (measure["measure_id"].lower(), slugify(framer.measure["description"].lower()))
                    )
                race_log += saver.make_measure(framer.contest, framer.measure)
        else:
            """
            this is a candidate for elected office
            """
            strip_district = contest["district"].lstrip("0")
            framer.contest["seatnum"] = "1010101"
            if contest["contest_title"] == "MEMBER OF THE ASSEMBLY":
                contestname = "State Assembly District %s" % (strip_district)
            elif "SUPERVISOR" in contest["contest_title"]:
                contestname = "Supervisor District %s" % (strip_district)
                contestname = fixer._affix_county(county_name,contestname)
            elif "U.S. REPRESENTATIVE" in contest["contest_title"]:
                contestname = "U.S. House of Representatives District %s" % (strip_district)
            elif "DELEGATES" in contest["contest_title"]:
                designation = contest["contest_title_cont"].replace("CONGRESSIONAL DISTRICT-", "")
                if designation == "REP":
                    this_desig = "Republican"
                elif designation == "DEM":
                    this_desig = "Democratic"
                else:
                    this_desig = None
                contestname = "%s Presidential Primary Delegates - CD%s" % (this_desig, strip_district)
            elif "STATE SENATOR" in contest["contest_title"]:
                contestname = "State Senate District %s" % (strip_district)
            elif "UNITED STATES SENATOR" in contest["contest_title"]:
                contestname = "US Senate"
            elif "PRESIDENTIAL PREFERENCE" in contest["contest_title"]:
                designation = contest["contest_title_cont"].upper()
                if designation == "AI":
                    this_desig = "American Independent"
                elif designation == "REP":
                    this_desig = "Republican"
                elif designation == "DEM":
                    this_desig = "Democratic"
                elif designation == "PF":
                    this_desig = "Peace And Freedom"
                elif designation == "LIB":
                    this_desig = "Libertarian"
                elif designation == "GRN":
                    this_desig = "Green"
                else:
                    this_desig = None
                contestname = "%s Presidential Primary" % (this_desig)
            elif "PARTY COUNTY COMMITTEE" in contest["contest_title"]:
                contestname = "%s Party County Committee District %s" % (
                    contest["party_name"].capitalize(), strip_district)
            elif "JUDGE-SUPERIOR COURT" in contest["contest_title"]:
                contestname = "Judge Superior Court %s" % (contest["contest_title_cont"].title())
                contestname = fixer._affix_county(county_name, contestname)
            else:
                contestname = "%s %s" % (contest["contest_title"].title(), contest["contest_title_cont"].title())
            contestname = fixer._fix(contestname)
            contestname = contestname.title()
            contestname = framer._convert_district_number(contestname)
            framer.office["officename"] = contestname.replace(".", "")
            framer.office["officeslug"] = slugify(framer.office["officename"])
            framer.office["active"] = True
            framer.office["officeid"] = framer.office["officeslug"]
            framer.contest["election_id"] = election.id
            framer.contest["resultsource_id"] = src.id
            if len(candidates) < 2:
                framer.contest["is_uncontested"] = True
            else:
                framer.contest["is_uncontested"] = False
            framer.contest["is_national"] = False
            framer.contest["is_ballot_measure"] = False
            framer.contest["is_judicial"] = False
            framer.contest["is_runoff"] = False
            framer.contest["reporttype"] = None
            framer.contest["poss_error"] = False
            if framer._to_num(contest["total_precincts"])["convert"] == True:
                pt = framer._to_num(contest["total_precincts"])["value"]
                framer.contest["precinctstotal"] = pt
            else:
                framer.contest["precinctstotal"] = None
                raise Exception("precinctstotal is not a number")
            if framer._to_num(contest["precincts_reporting"])["convert"] == True:
                pr = framer._to_num(contest["precincts_reporting"])["value"]
                framer.contest["precinctsreporting"] = pr
            else:
                framer.contest["precinctsreporting"] = None
                raise Exception("precinctsreporting is not a number")
            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                framer.contest["precinctsreporting"],
                framer.contest["precinctstotal"]
            )
            if framer._to_num(contest["registration"])["convert"] == True:
                framer.contest["votersregistered"] = framer._to_num(
                    contest["registration"])["value"]
            else:
                framer.contest["votersregistered"] = None
                raise Exception("votersregistered is not a number")
            framer.contest["votersturnout"] = None
            framer.contest["contestname"] = contestname
            try:
                framer.contest["contestdescription"] = contest[
                    "vote_for_text"].capitalize() + " " + contest["vote_for_number"]
            except:
                framer.contest["contestdescription"] = None
            framer.contest["contestid"] = saver._make_contest_id(
                src.source_short,
                framer.contest["level"],
                framer.office["officeslug"],
            )
            race_log += saver.make_office(framer.office)
            race_log += saver.make_contest(framer.office, framer.contest)
            for candidate in candidates:
                fullname = fixer._titlecase_with_accents(candidate["candidate_name"].encode('utf8'))
                party = candidate["party_short"]
                if party == "REP":
                    party = "Republican"
                elif party == "DEM":
                    party = "Democrat"
                elif party == "AI":
                    party = "American Independent"
                elif party == "PF":
                    party = "Peace And Freedom"
                elif party == "LIB":
                    party = "Libertarian"
                elif party == "GRN":
                    party = "Green"
                elif party == "NP":
                    party = "No Party Preference"
                framer.candidate["ballotorder"] = None
                framer.candidate["firstname"] = None
                framer.candidate["lastname"] = None
                framer.candidate["fullname"] = fullname
                framer.candidate["candidateslug"] = slugify(fullname)
                framer.candidate["party"] = party
                framer.candidate["incumbent"] = False
                framer.candidate["poss_error"] = False
                if framer._to_num(candidate["votes"])["convert"] == True:
                    framer.candidate["votecount"] = framer._to_num(candidate["votes"])["value"]
                else:
                    framer.candidate["votecount"] = None
                    raise Exception("votecount is not a number")
                if framer._to_num(candidate["percent_of_vote"])["convert"] == True:
                    framer.candidate["votepct"] = framer._to_num(candidate["percent_of_vote"])["value"]
                else:
                    framer.candidate["votepct"] = None
                    raise Exception("votepct is not a number")
                framer.candidate["candidateid"] = saver._make_this_id(
                    "candidate",
                    framer.contest["contestid"],
                    framer.candidate["candidateslug"],
                )
                race_log += saver.make_candidate(framer.contest, framer.candidate)
        logger.info(race_log)

    def check_if_recall_or_nonpartisan(self, records):
        """
        check to see if this is a recall contest or a nonpartisan contest. for now, it's unclear how to store or display these contests. in future, however, we may want to parse and return their results.
        """
        recall = False
        nonpartisan = False
        for r in records:
            if r["record_type"] == "MT" and "RECALL" in r["measure_text"]:
                recall = True
            if r["record_type"] == "CC" and "NONPARTISAN" in r["contest_title"]:
                nonpartisan = True
        if recall or nonpartisan:
            return True
        else:
            return False

    # def printreport(self, election_info, contest_list, measure_list, candidate_list, judicial_list):
        """Prints human readable report of all candidates, contests, measures, and some
        basic election stats. Activate by un-commenting call in evaluate_and_process_races().
        """
        # with open("%s/ballot_box/data_dump/lac_latest/lac_latest_report.md" % (settings.BASE_DIR), "w+") as f:
        #     election_desc = election_info["description"].split(" | ")
        #     for d in election_desc:
        #         f.write(d + "\n")
        #     f.write("\n\n")

        #     f.write("## BY THE NUMBERS\n\n")
        #     f.write("__No. of contests:__ " + str(len(contest_list)) + "\n\n")
        #     f.write("__No. of measures:__ " + str(len(measure_list)) + "\n\n")
        #     f.write("__No. of candidates:__ " +
        #             str(len(candidate_list)) + "\n\n")
        #     f.write("__No. of judicial appointees:__ " +
        #             str(len(judicial_list)) + "\n")
        #     f.write("\n\n\n\n")

        #     f.write("## CONTESTS\n\n")
        #     for contest in (sorted(contest_list, key=operator.itemgetter("page_sequence"))):
        #         f.write("* " + contest["contest_title"] +
        #                 " " + contest["contest_title_cont"] + "\n")
        #     f.write("\n\n")

        #     f.write("## MEASURES\n\n")
        #     if len(measure_list) > 0:
        #         for measure in (sorted(measure_list, key=operator.itemgetter("measure_id"))):
        #             contest = ""
        #             for c in contest_list:
        #                 if c["page_sequence"] == measure["page_sequence"] and c["contest_id"] == measure["contest_id"] and c["district"] == measure["district"]:
        #                     contest = c["contest_title"]
        #             f.write("* " + measure["measure_id"] + " - " + measure["measure_text"] + " (" + contest + ")\n")
        #     else:
        #         f.write("N/A\n")
        #     f.write("\n\n")

        #     f.write("## CANDIDATES\n\n")
        #     if len(candidate_list) > 0:
        #         for candidate in (sorted(candidate_list, key=operator.itemgetter("candidate_name"))):
        #             contest = ""
        #             for c in contest_list:
        #                 if c["page_sequence"] == candidate["page_sequence"] and c["contest_id"] == candidate["contest_id"] and c["district"] == candidate["district"]:
        #                     contest = c["contest_title"] + " " + c["contest_title_cont"]
        #             f.write("* " + candidate["candidate_name"] + " - " + contest + "\n")
        #     else:
        #         f.write("N/A\n")
        #     f.write("\n\n")

        #     f.write("## JUDICIAL APPOINTEES\n\n")
        #     if len(judicial_list) > 0:
        #         for judge in (sorted(judicial_list, key=operator.itemgetter("judicial_name"))):
        #             f.write("* " + judge["judicial_name"] + " - " + judge["judicial_text"] + "\n")
        #     else:
        #         f.write("N/A\n")

    # def prettyprint(self, election_info, contest_list, measure_list, candidate_list, judicial_list):
        """Prints human readable, detailed layout of all candidates, contests, measures, and
        election stats. Activate by un-commenting call in evaluate_and_process_races().
        """
        # report = ""
        # report += "## election_info\n\n"
        # for i in election_info:
        #     report += i + ": " + election_info[i] + "\n"
        # report += "\n\n\n\n"

        # report += "## contest_list\n\n"
        # for contest in (sorted(contest_list, key=operator.itemgetter("page_sequence"))):
        #     for c in contest:
        #         report += c + ": " + str(contest[c]) + "\n"
        #     report += "\n\n"
        # report += "\n\n\n\n"

        # report += "## measure_list\n\n"
        # for measure in (sorted(measure_list, key=operator.itemgetter("measure_id"))):
        #     for m in measure:
        #         report += m + ": " + str(measure[m]) + "\n"
        #     report += "\n\n"
        # report += "\n\n\n\n"

        # report += "## candidate_list\n\n"
        # for candidate in (sorted(candidate_list, key=operator.itemgetter("candidate_name"))):
        #     for c in candidate:
        #         report += c + ": " + str(candidate[c]) + "\n"
        #     report += "\n\n"
        # report += "\n\n\n\n"

        # report += "## JUDICIAL APPOINTEES\n\n"
        # if len(judicial_list) > 0:
        #     for judge in (sorted(judicial_list, key=operator.itemgetter("judicial_name"))):
        #         report = report + "* " + judge["judicial_name"] + " - " + judge["judicial_text"] + "\n"
        # else:
        #     report += "N/A\n"
        # print report

if __name__ == "__main__":
    task_run = BuildLacResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
