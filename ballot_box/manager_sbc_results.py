# -*- coding: utf-8 -*-
from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime
from ballot_box.utils_files import Retriever
from ballot_box.utils_data import Framer, Namefixer
from ballot_box.utils_import import Saver
from ballot_box.tabparser import *
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


class BuildSbcResults(object):
    """
    scaffolding to ingest la county registrar election results
    """

    retrieve = Retriever()

    data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    sources = ResultSource.objects.filter(source_short="sbc", source_active=True)

    elections = Election.objects.all().order_by("-election_date")

    testing = elections[0].test_results

    def _init(self, *args, **kwargs):
        """
        """
        for src in self.sources:
            self.get_results_file(src, self.data_directory)
            self.parse_results_file(src, self.data_directory)
        # self.retrieve._build_and_move_results()

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
        process = SbcProcessMethods()
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        election = Election.objects.filter(electionid=src.election.electionid).first()

        for file in src.source_files.split(", "):
            latest_path = os.path.join(latest_directory, file)
            file_exists = os.path.isfile(latest_path)
            file_has_size = os.path.getsize(latest_path)
            if file_exists == True and file_has_size > 0:
                rows = ParseTabDelimited(latest_path).dictionaries
                race_ids = process.get_race_ids_from(rows)
                election_package = process.collate_and_fetch_records_for_race(race_ids, rows)
                races = election_package[0]
                election_stats = election_package[1]["stats"]
                file_timestring = None
                file_timestamp = None
                logger.info("\n*****\nUpdating...\n*****")
                saver._update_result_timestamps(src, datetime.datetime.now())
                election_info = process.compile_election_stats(election_stats)
                # print election_info
                for r in races:
                    contest_package = process.compile_contest_results(races[r])
                    # print contest_package
                    process.update_database(contest_package, election, src)
                os.remove(latest_path)
                logger.info("we've finished processing sbc results")


class SbcProcessMethods(object):
    """
    """

    def get_race_ids_from(self, rows):
        """
        returns index of races using CONTEST_ID.
        """
        list_of_race_ids = []
        for result in rows:
            race_id = result["CONTEST_ID"]
            record_type = result["CONTEST_TYPE"]
            if "-" in record_type:
                pass
            else:
                list_of_race_ids.append(race_id)
        set_of_race_ids = set(list_of_race_ids)
        race_ids = list(set_of_race_ids)
        return race_ids

    def collate_and_fetch_records_for_race(self, race_ids, rows):
        races = {}
        election_info = {"title": ["San Bernardino County Election"], "stats": []}
        title_rid = None
        stats_rid = None
        for row in rows:
            if row["CONTEST_ID"] == "0":
                election_info["stats"].append(row)
                if stats_rid == None:
                    stats_rid = row["CONTEST_ID"]
            else:
                pass

        for rid in race_ids:
            if "-" in rid or rid == "0":
                pass
            else:
                race_rows = []
                for row in rows:
                    if row["CONTEST_ID"] == rid:
                        race_rows.append(row)
                    else:
                        pass
                races[rid] = race_rows
        return [races, election_info]

    def compile_election_stats(self, stats):
        """Fetches records that contain overall election title and stats."""
        election_info = {}
        election_info['registration'] = None
        election_info['precinct_ballots_cast'] = None
        election_info['vote_by_mail_ballots_cast'] = None

        for record in stats:
            if not election_info['registration']:
                election_info['registration'] = record['CONTEST_TOTAL']

            if record['CANDIDATE_FULL_NAME'] == 'Precinct Turnout':
                election_info['precinct_ballots_cast'] = record['TOTAL']
                if election_info['registration'] and election_info['registration'] != "0":
                    raw_percent = 100*(float(record['TOTAL'])/float(election_info['registration']))
                    rounded_percent = "%.2f" % raw_percent
                    election_info['precinct_turnout'] = rounded_percent
                else:
                    election_info['precinct_turnout'] = 0.00

            elif record['CANDIDATE_FULL_NAME'] == 'Vote by Mail Turnout':
                election_info['vote_by_mail_ballots_cast'] = record['TOTAL']
                if election_info['registration'] and election_info['registration'] != "0":
                    raw_percent = 100*(float(record['TOTAL'])/float(election_info['registration']))
                    rounded_percent = "%.2f" % raw_percent
                    election_info['votebymail_turnout'] = rounded_percent
                else:
                    election_info['votebymail_turnout'] = 0.00

            # Calculate overall turnout
            if election_info['precinct_ballots_cast'] and election_info['vote_by_mail_ballots_cast']:
                election_info['total_turnout'] = float(election_info['precinct_ballots_cast']) + float(election_info['vote_by_mail_ballots_cast'])
                if election_info['registration'] and election_info['registration'] != "0":
                    raw_percent = 100*(float(election_info['total_turnout'])/float(election_info['registration']))
                    rounded_percent = "%.2f" % raw_percent
                    election_info['overall_percent_turnout'] = rounded_percent
                else:
                    election_info['overall_percent_turnout'] = 0.00

                """ INFO WE'VE GOTTEN FROM OTHER ELECTION OFFICIALS
                    BUT SO FAR NOT SAN BERNARDINO """
                # election_info['absentee_total'] = record['absentee_total'].replace(',', '')
                # election_info['registration'] = record['registration']
                # election_info['election_id']
                # election_info['time']
                # election_info['date']

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
            if record['CONTEST_TOTAL'] == "0":
                rounded_percent = 0.00
            else:
                raw_percent = 100*(float(record['TOTAL'])/float(record['CONTEST_TOTAL']))
                rounded_percent = "%.2f" % raw_percent

            try:
                contest['CONTEST_FULL_NAME']
            except:
                contest['CONTEST_FULL_NAME'] = record['CONTEST_FULL_NAME']
            try:
                contest['VOTE_FOR']
            except:
                contest['VOTE_FOR'] = record['VOTE_FOR']
            try:
                contest['overvote']
            except:
                contest['overvote'] = record['overvote']
            # try:
                # contest['is_visible']
            # except:
                # contest['is_visible'] = record['is_visible']
            try:
                contest['CONTEST_TYPE']
            except:
                contest['CONTEST_TYPE'] = record['CONTEST_TYPE']
            try:
                contest['PROCESSED_STARTED']
            except:
                contest['PROCESSED_STARTED'] = record['PROCESSED_STARTED']
            try:
                contest['PRECINCT_NAME']
            except:
                contest['PRECINCT_NAME'] = record['PRECINCT_NAME']
            try:
                contest['IS_PRECINCT_LEVEL']
            except:
                contest['IS_PRECINCT_LEVEL'] = record['IS_PRECINCT_LEVEL']
            try:
                contest['CONTEST_ID']
            except:
                contest['CONTEST_ID'] = record['CONTEST_ID']
            try:
                contest['undervote']
            except:
                contest['undervote'] = record['undervote']
            try:
                contest['CONTEST_ORDER']
            except:
                contest['CONTEST_ORDER'] = record['CONTEST_ORDER']
            try:
                contest['TOTAL_PRECINCTS']
            except:
                contest['TOTAL_PRECINCTS'] = record['TOTAL_PRECINCTS']
            try:
                contest['CONTEST_TOTAL']
            except:
                contest['CONTEST_TOTAL'] = record['CONTEST_TOTAL']
            try:
                contest['PROCESSED_DONE']
            except:
                contest['PROCESSED_DONE'] = record['PROCESSED_DONE']

            if record['CONTEST_TYPE'] == '0':
                # This is a candidate
                candidate = {}
                try:
                    contest['is_ballot_measure']
                except:
                    contest['is_ballot_measure'] = False
                try:
                    contest['is_judicial_contest']
                except:
                    contest['is_judicial_contest'] = False

                candidate['IS_WINNER'] = record['IS_WINNER']
                candidate['CANDIDATE_ID'] = record['CANDIDATE_ID']
                candidate['TOTAL'] = record['TOTAL']
                candidate['CANDIDATE_FULL_NAME'] = record['CANDIDATE_FULL_NAME']
                candidate['IS_WRITEIN_CANDIDATE'] = record['IS_WRITEIN_CANDIDATE']
                candidate['CANDIDATE_ORDER'] = record['CANDIDATE_ORDER']
                candidate['CANDIDATE_TYPE'] = record['CANDIDATE_TYPE']
                candidate['cf_cand_class'] = record['cf_cand_class']
                candidate['CANDIDATE_PARTY_ID'] = record['CANDIDATE_PARTY_ID']
                candidate['percent_of_vote'] = rounded_percent
                candidates.append(candidate)


            elif record['CONTEST_TYPE'] == '4':
                # This is a ballot measure
                measure = {}
                already_exists = False

                try:
                    contest['is_ballot_measure']
                except:
                    contest['is_ballot_measure'] = True
                try:
                    contest['is_judicial_contest']
                except:
                    contest['is_judicial_contest'] = False

                measure['measure_id'] = record['CONTEST_ID']
                if measures:
                    # Check to see if we've already captured the first of the two measure records
                    for m in measures:
                        if m['measure_id'] == measure['measure_id']:
                            already_exists = True
                            if "YES" in record['CANDIDATE_FULL_NAME']:
                                m['yes_votes'] = record['TOTAL']
                                m['yes_percent'] = rounded_percent
                            elif "NO" in record['CANDIDATE_FULL_NAME']:
                                m['no_votes'] = record['TOTAL']
                                m['no_percent'] = rounded_percent

                if already_exists:
                    pass
                else:
                    # Prep new measure
                    measure['measure_name'] = record['CONTEST_FULL_NAME']
                    measure['measure_order'] = record['CANDIDATE_ORDER']
                    measure['measure_type'] = record['CANDIDATE_TYPE']
                    measure['cf_cand_class'] = record['cf_cand_class']
                    if "YES" in record['CANDIDATE_FULL_NAME']:
                        measure['yes_votes'] = record['TOTAL']
                        measure['yes_percent'] = rounded_percent
                    elif "NO" in record['CANDIDATE_FULL_NAME']:
                        measure['no_votes'] = record['TOTAL']
                        measure['no_percent'] = rounded_percent
                    measures.append(measure)

            """ NEED TO GET EXAMPLE OF JUDICIAL CONFIRMATION CANDIDATES
            elif record['CONTEST_TYPE'] == 'XX':
                try:
                    contest['is_ballot_measure']
                except:
                    contest['is_ballot_measure'] = False
                try:
                    contest['is_judicial_contest']
                except:
                    contest['is_judicial_contest'] = True
            """

        contest_package = {
            'contest_details': contest,
            'candidates': candidates,
            'measures': measures,
            'judges': judge_candidates,
        }
        return contest_package

    def update_database(self, contest_package, election, src):
        """ import candidates, measures, office and contest info from compiled data """
        saver = Saver()
        framer = Framer()
        fixer = Namefixer()
        county_name = "San Bernardino County"
        contest = contest_package['contest_details']
        candidates = contest_package['candidates']
        measures = contest_package['measures']
        judges = contest_package['judges']
        race_log = "\n"

        # Check level of contest (i.e. local, statewide)
        if "United States" in contest['CONTEST_FULL_NAME'] or "STATE" in contest['CONTEST_FULL_NAME']:
            level = "california"
            framer.contest["is_statewide"] = True
        else:
            level = "county"
            framer.contest["is_statewide"] = False
        framer.contest["level"] = level

        """ Need to deal with judicial contests in future elections.. None in 2016 general
        if contest['is_judicial_contest']:
            # This is a judicial appointee
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
            framer.contest["level"] = "california"
            # need to determine appropriate level
            framer.contest["is_ballot_measure"] = False
            framer.contest["is_judicial"] = True
            framer.contest["is_runoff"] = False
            framer.contest["reporttype"] = None
            framer.contest["poss_error"] = False
            if framer._to_num(contest['total_precincts'])["convert"] == True:
                pt = framer._to_num(contest['total_precincts'])["value"]
                framer.contest["precinctstotal"] = pt
            else:
                framer.contest["precinctstotal"] = None
                raise Exception("precinctstotal is not a number")
            if framer._to_num(contest['precincts_reporting'])["convert"] == True:
                pr = framer._to_num(contest['precincts_reporting'])["value"]
                framer.contest["precinctsreporting"] = pr
            else:
                framer.contest["precinctsreporting"] = None
                raise Exception("precinctsreporting is not a number")
            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                framer.contest["precinctsreporting"],
                framer.contest["precinctstotal"]
            )
            if framer._to_num(contest['registration'])["convert"] == True:
                framer.contest["votersregistered"] = framer._to_num(
                    contest['registration'])["value"]
            else:
                framer.contest["votersregistered"] = None
                raise Exception("votersregistered is not a number")
            framer.contest["votersturnout"] = None
            framer.contest["contestname"] = fixer._fix(contestname) # framer.office["officename"]
            framer.contest["contestdescription"] = None
            framer.contest["contestid"] = saver._make_contest_id(
                # election.electionid,
                src.source_short,
                framer.contest["level"],
                framer.office["officeslug"],
            )
            race_log += saver.make_office(framer.office)
            race_log += saver.make_contest(framer.office, framer.contest)

            for judge in judges:
                fullname = judge["judicial_name"].title()
                framer.judicial["firstname"] = None
                framer.judicial["lastname"] = None
                framer.judicial["ballotorder"] = None
                framer.judicial["fullname"] = fullname
                framer.judicial["judicialslug"] = slugify(fullname)
                framer.judicial["description"] = judge['judicial_text'].title()
                framer.judicial["poss_error"] = False
                if framer._to_num(judge['yes_votes'])["convert"] == True:
                    yescount = framer._to_num(judge['yes_votes'])["value"]
                    framer.judicial["yescount"] = yescount
                else:
                    framer.judicial["yescount"] = None
                    raise Exception("yescount is not a number")
                if framer._to_num(judge['yes_percent'])["convert"] == True:
                    yespct = framer._to_num(judge['yes_percent'])["value"]
                    framer.judicial["yespct"] = yespct
                else:
                    framer.judicial["yespct"] = None
                    raise Exception("yespct is not a number")
                if framer._to_num(judge['no_votes'])["convert"] == True:
                    nocount = framer._to_num(judge['no_votes'])["value"]
                    framer.judicial["nocount"] = nocount
                else:
                    framer.judicial["nocount"] = None
                    raise Exception("nocount is not a number")
                if framer._to_num(judge['no_percent'])["convert"] == True:
                    nopct = framer._to_num(judge['no_percent'])["value"]
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
        """
        if contest['is_ballot_measure']:
            """ this is a ballot measure """
            framer.contest["level"] = "county"
            framer.contest["is_statewide"] = False
            contestname = contest['CONTEST_FULL_NAME']
            if "Proposition" in contestname:
                this_type = "Proposition"
                contestname = contestname.replace("STATE ", "")
            else:
                this_type = "Measure"
                contestname = fixer._fix(contestname)
            description = ""
            officename = framer._concat(
                # this_type,
                contestname,
                delimiter="-",
            )
            fullname = contestname
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
            if framer._to_num(contest['TOTAL_PRECINCTS'])["convert"] == True:
                pt = framer._to_num(contest['TOTAL_PRECINCTS'])["value"]
                framer.contest["precinctstotal"] = pt
            else:
                framer.contest["precinctstotal"] = None
                raise Exception("precinctstotal is not a number")
            if framer._to_num(contest['PROCESSED_DONE'])["convert"] == True:
                pr = framer._to_num(contest['PROCESSED_DONE'])["value"]
                framer.contest["precinctsreporting"] = pr
            else:
                framer.contest["precinctsreporting"] = None
                raise Exception("precinctsreporting is not a number")
            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                framer.contest["precinctsreporting"],
                framer.contest["precinctstotal"]
            )
            # if framer._to_num(contest['registration'])["convert"] == True:
            #     framer.contest["votersregistered"] = framer._to_num(
            #         contest['registration'])["value"]
            # else:
            #     framer.contest["votersregistered"] = None
            #     raise Exception(
            #         "votersregistered is not a number")
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
                framer.measure["ballotorder"] = measure["measure_order"]
                framer.measure["fullname"] = fullname
                framer.measure["measureslug"] = slugify(fullname)
                framer.measure["description"] = ""
                framer.measure["poss_error"] = False
                if framer._to_num(measure['yes_votes'])["convert"] == True:
                    yescount = framer._to_num(measure['yes_votes'])["value"]
                    framer.measure["yescount"] = yescount
                else:
                    framer.measure["yescount"] = None
                    raise Exception("yescount is not a number")
                if framer._to_num(measure['yes_percent'])["convert"] == True:
                    yespct = framer._to_num(measure['yes_percent'])["value"]
                    framer.measure["yespct"] = yespct
                else:
                    framer.measure["yespct"] = None
                    raise Exception("yespct is not a number")
                if framer._to_num(measure['no_votes'])["convert"] == True:
                    nocount = framer._to_num(measure['no_votes'])["value"]
                    framer.measure["nocount"] = nocount
                else:
                    framer.measure["nocount"] = None
                    raise Exception("nocount is not a number")
                if framer._to_num(measure['no_percent'])["convert"] == True:
                    nopct = framer._to_num(measure['no_percent'])["value"]
                    framer.measure["nopct"] = nopct
                else:
                    framer.measure["nopct"] = None
                    raise Exception("nopct is not a number")
                framer.measure["measureid"] = saver._make_this_id(
                    "measure",
                    framer.contest["contestid"],
                    measure['measure_id'].lower(),
                )
                race_log += saver.make_measure(framer.contest, framer.measure)
        else:
            """ this is a candidate for elected office """
            # strip_district = contest['district'].lstrip("0")
            framer.contest["seatnum"] = "1010101"
            contestname = contest['CONTEST_FULL_NAME']
            if "Member of the State Assembly" in contestname:
                contestname = "SAN BERNARDINO %s" % (contestname)
            elif "Supervisor" in contestname:
                contestname = county_name + " " + contestname
            elif "United States Representative" in contestname:
                contestname = "SAN BERNARDINO %s" % (
                    contestname)
            elif "State Senator" in contestname:
                contestname = "SAN BERNARDINO %s" % (contestname)
            elif "United States Senator" in contestname:
                contestname = "SAN BERNARDINO %s" % (contestname)
            elif "Judge of the Superior Court" in contestname:
                contestname = county_name + " " + contestname

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
            if framer._to_num(contest['TOTAL_PRECINCTS'])["convert"] == True:
                pt = framer._to_num(contest['TOTAL_PRECINCTS'])["value"]
                framer.contest["precinctstotal"] = pt
            else:
                framer.contest["precinctstotal"] = None
                raise Exception("precinctstotal is not a number")
            if framer._to_num(contest['PROCESSED_DONE'])["convert"] == True:
                pr = framer._to_num(contest['PROCESSED_DONE'])["value"]
                framer.contest["precinctsreporting"] = pr
            else:
                framer.contest["precinctsreporting"] = None
                raise Exception("precinctsreporting is not a number")
            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                framer.contest["precinctsreporting"],
                framer.contest["precinctstotal"]
            )
            # if framer._to_num(contest['registration'])["convert"] == True:
            #     framer.contest["votersregistered"] = framer._to_num(
            #         contest['registration'])["value"]
            # else:
            #     framer.contest["votersregistered"] = None
            #     raise Exception("votersregistered is not a number")
            framer.contest["votersturnout"] = None
            framer.contest["contestname"] = fixer._fix(contestname) # framer.office["officename"]
            if int(contest["VOTE_FOR"]) > 1:
                framer.contest["contestdescription"] = "Vote for " + contest["VOTE_FOR"]
            else:
                framer.contest["contestdescription"] = None
            framer.contest["contestid"] = saver._make_contest_id(
                # election.electionid,
                src.source_short,
                framer.contest["level"],
                framer.office["officeslug"],
            )
            race_log += saver.make_office(framer.office)
            race_log += saver.make_contest(framer.office, framer.contest)
            for candidate in candidates:
                recoded_name = candidate['CANDIDATE_FULL_NAME'].decode('iso-8859-1').encode('utf8')
                recoded_name = lower_case_accents(recoded_name)
                if " - " in recoded_name:
                    fullname = recoded_name.split(" - ")[1].title()
                else:
                    fullname = recoded_name.title()

                party_id = candidate['CANDIDATE_PARTY_ID']
                if party_id == "2":
                    party = "Democratic"
                elif party_id == "3":
                    party = "Green"
                elif party_id == "4":
                    party = "Libertarian"
                elif party_id == "5":
                    party = "Peace and Freedom"
                elif party_id == "6":
                    party = "Republican"
                elif party_id == "8":
                    party = "Republican"
                else:
                    party = ""
                framer.candidate["ballotorder"] = candidate["CANDIDATE_ORDER"]
                framer.candidate["firstname"] = None
                framer.candidate["lastname"] = None
                framer.candidate["fullname"] = fullname
                framer.candidate["candidateslug"] = slugify(fullname)
                framer.candidate["party"] = party
                framer.candidate["incumbent"] = False
                framer.candidate["poss_error"] = False
                if framer._to_num(candidate['TOTAL'])["convert"] == True:
                    framer.candidate["votecount"] = framer._to_num(candidate['TOTAL'])[
                        "value"]
                else:
                    framer.candidate["votecount"] = None
                    raise Exception("votecount is not a number")
                if contest["CONTEST_TOTAL"] != "0":
                    if framer._to_num(contest['CONTEST_TOTAL'])["convert"] == True:
                        vote_total = framer._to_num(contest['CONTEST_TOTAL'])["value"]
                        framer.candidate["votepct"] = framer._calc_pct(
                            framer.candidate["votecount"],
                            vote_total
                        )
                else:
                    framer.candidate["votepct"] = None
                    logger.debug("No votes have been cast in " + contestname + " or votepct is not a number")
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
            if r['record_type'] == "MT" and "RECALL" in r['measure_text']:
                recall = True
            if r['record_type'] == "CC" and "NONPARTISAN" in r['contest_title']:
                nonpartisan = True
        if recall or nonpartisan:
            return True
        else:
            return False

    def printreport(self, election_info, contest_list, measure_list, candidate_list, judicial_list):
        """Prints human readable report of all candidates, contests, measures, and some
        basic election stats. Activate by un-commenting call in evaluate_and_process_races().
        """
        with open("%s/ballot_box/data_dump/lac_latest/lac_latest_report.md" % (settings.BASE_DIR), "w+") as f:
            election_desc = election_info['description'].split(' | ')
            for d in election_desc:
                f.write(d + '\n')
            f.write('\n\n')

            f.write('## BY THE NUMBERS\n\n')
            f.write('__No. of contests:__ ' + str(len(contest_list)) + '\n\n')
            f.write('__No. of measures:__ ' + str(len(measure_list)) + '\n\n')
            f.write('__No. of candidates:__ ' +
                    str(len(candidate_list)) + '\n\n')
            f.write('__No. of judicial appointees:__ ' +
                    str(len(judicial_list)) + '\n')
            f.write('\n\n\n\n')

            f.write('## CONTESTS\n\n')
            for contest in (sorted(contest_list, key=operator.itemgetter('page_sequence'))):
                f.write('* ' + contest['contest_title'] +
                        ' ' + contest['contest_title_cont'] + '\n')
            f.write('\n\n')

            f.write('## MEASURES\n\n')
            if len(measure_list) > 0:
                for measure in (sorted(measure_list, key=operator.itemgetter('measure_id'))):
                    contest = ''
                    for c in contest_list:
                        if c['page_sequence'] == measure['page_sequence'] and c['contest_id'] == measure['contest_id'] and c['district'] == measure['district']:
                            contest = c['contest_title']
                    f.write('* ' + measure['measure_id'] + ' - ' +
                            measure['measure_text'] + ' (' + contest + ')\n')
            else:
                f.write('N/A\n')
            f.write('\n\n')

            f.write('## CANDIDATES\n\n')
            if len(candidate_list) > 0:
                for candidate in (sorted(candidate_list, key=operator.itemgetter('candidate_name'))):
                    contest = ''
                    for c in contest_list:
                        if c['page_sequence'] == candidate['page_sequence'] and c['contest_id'] == candidate['contest_id'] and c['district'] == candidate['district']:
                            contest = c['contest_title'] + \
                                ' ' + c['contest_title_cont']
                    f.write(
                        '* ' + candidate['candidate_name'] + ' - ' + contest + '\n')
            else:
                f.write('N/A\n')
            f.write('\n\n')

            f.write('## JUDICIAL APPOINTEES\n\n')
            if len(judicial_list) > 0:
                for judge in (sorted(judicial_list, key=operator.itemgetter('judicial_name'))):
                    f.write('* ' + judge['judicial_name'] +
                            ' - ' + judge['judicial_text'] + '\n')
            else:
                f.write('N/A\n')

    def prettyprint(self, election_info, contest_list, measure_list, candidate_list, judicial_list):
        """Prints human readable, detailed layout of all candidates, contests, measures, and
        election stats. Activate by un-commenting call in evaluate_and_process_races().
        """
        report = ''
        report += '## election_info\n\n'
        for i in election_info:
            report += i + ': ' + election_info[i] + '\n'
        report += '\n\n\n\n'

        report += '## contest_list\n\n'
        for contest in (sorted(contest_list, key=operator.itemgetter('page_sequence'))):
            for c in contest:
                report += c + ': ' + str(contest[c]) + '\n'
            report += '\n\n'
        report += '\n\n\n\n'

        report += '## measure_list\n\n'
        for measure in (sorted(measure_list, key=operator.itemgetter('measure_id'))):
            for m in measure:
                report += m + ': ' + str(measure[m]) + '\n'
            report += '\n\n'
        report += '\n\n\n\n'

        report += '## candidate_list\n\n'
        for candidate in (sorted(candidate_list, key=operator.itemgetter('candidate_name'))):
            for c in candidate:
                report += c + ': ' + str(candidate[c]) + '\n'
            report += '\n\n'
        report += '\n\n\n\n'

        # report += '## JUDICIAL APPOINTEES\n\n'
        # if len(judicial_list) > 0:
        #     for judge in (sorted(judicial_list, key=operator.itemgetter('judicial_name'))):
        #         report = report + '* ' + judge['judicial_name'] + ' - ' + judge['judicial_text'] + '\n'
        # else:
        #     report += 'N/A\n'
        print report

def lower_case_accents(string):
    subs = ('ÂÁÀÄÊÉÈËÏÍÎÖÓÔÖÚÙÛÑÇ', 'âáàäêéèëïíîöóôöúùûñç')
    newstring = string
    for s in range(len(subs[0])):
        newstring = re.sub(subs[0][s], subs[1][s], newstring)
    return newstring

if __name__ == '__main__':
    task_run = BuildSbcResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
