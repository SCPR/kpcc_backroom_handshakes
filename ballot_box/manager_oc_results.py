from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime
from ballot_box.utils_files import Retriever
from ballot_box.utils_data import Framer
from ballot_box.utils_import import Saver
from election_registrar.models import ResultSource, Election
import logging
import time
import datetime
import os.path
import shutil
from bs4 import BeautifulSoup
from delorean import parse
from slugify import slugify

logger = logging.getLogger("kpcc_backroom_handshakes")


class BuildOcResults(object):
    """
    scaffolding to ingest secretary of state election results
    """

    retrieve = Retriever()

    data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    sources = ResultSource.objects.filter(source_short="oc", source_active=True)

    elections = Election.objects.all().order_by("-election_date")

    testing = elections[0].test_results

    race_ids = [
        "742",
        "743",
        "745",
        "746",
        "747",
        "748",
        "749",
        "750",
    ]

    def _init(self, *args, **kwargs):
        """
        """
        for src in self.sources:
            self.get_results_file(src, self.data_directory)
            self.parse_results_file(src, self.data_directory)
        self.retrieve._build_and_move_results()

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

    def parse_results_file(self, src, data_directory):
        """
        """
        saver = Saver()
        compiler = BuildResults()
        latest_directory = "%s%s_latest" % (data_directory, src.source_short)
        election = Election.objects.filter(
            test_results=True, electionid=src.election.electionid).first()
        for file in src.source_files.split(", "):
            latest_path = os.path.join(latest_directory, file)
            file_exists = os.path.isfile(latest_path)
            file_has_size = os.path.getsize(latest_path)
            if file_exists == True and file_has_size > 0:
                soup = BeautifulSoup(open(latest_path), "xml")
                file_timestring = unicode(soup.CumulativeRptHeader.ReportHeader.attrs["run_date"])
                file_timestamp = parse(file_timestring, dayfirst=False).datetime
                update_this = saver._eval_timestamps(file_timestamp, src.source_latest)
                update_this = election.test_results
                if update_this == False:
                    logger.info("\n*****\nwe have newer data in the database so let's delete these files\n*****")
                    os.remove(latest_path)
                else:
                    logger.info("\n*****\nwe have new data to save and we'll update timestamps in the database\n*****")
                    saver._update_result_timestamps(src, file_timestamp)
                    races = soup.find_all("ContestTotal")
                    race_log = "\n"
                    for race in races:
                        if race.attrs["race_id"] in self.race_ids:
                            if race.attrs["contest_type"] == "MS":
                                """
                                this is a proposition
                                """
                                result = compiler._compile_measure(race, election, src)
                                race_log += saver.make_office(result.office)
                                race_log += saver.make_contest(result.office, result.contest)
                                race_log += saver.make_measure(result.contest, result.measure)
                            else:
                                """
                                this is a non-judicial candidate
                                """
                                result = compiler._compile_candidate(race, election, src)
                                race_log += saver.make_office(result.office)
                                race_log += saver.make_contest(result.office, result.contest)
                                for candidate in result.candidates:
                                    race_log += saver.make_candidate(result.contest, candidate)
                    logger.info(race_log)
                    os.remove(latest_path)
                    logger.info("\n*****\nwe've finished processing orange county results\n*****")
            else:
                logger.error("XML file to parse is not at expected location")


class BuildResults(object):
    """
    """
    saver = Saver()
    framer = Framer()

    def _compile_judicial(self, race, race_id, election, src):
        """
        """
        r = race.find("TotalVotes")
        this_type = "judicial"
        contestname = unicode(" ".join(race.ContestName.stripped_strings))
        if race_id == "140":
            officename_idx = self.framer._find_nth(contestname, " - ", 1)
            officename = unicode(contestname[:officename_idx].replace(".", ""))
            officename = unicode(officename.replace(" Justice", ""))
            fullname_idx = self.framer._find_nth(contestname, " - ", 1) + 3
        elif race_id == "150":
            officename_idx = self.framer._find_nth(contestname, " - ", 2)
            officename = unicode(contestname[:officename_idx].replace(" - ", " "))
            fullname_idx = self.framer._find_nth(contestname, " - ", 2) + 3
        fullname = unicode(contestname[fullname_idx:])
        level = "california"
        seatnum = None
        is_statewide = True
        precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
        precinctsreport = r.find(attrs={"Id": "PR"}).contents[0]
        reporttype = r.find(attrs={"Id": "RT"}).contents[0]
        yescount = self.framer._to_num(r.find_all("Selection")[0].ValidVotes.contents[0])["value"]
        yespct = self.framer._to_num(r.find(attrs={"Id": "PYV"}).contents[0])["value"]
        nocount = self.framer._to_num(r.find_all("Selection")[1].ValidVotes.contents[0])["value"]
        nopct = self.framer._to_num(r.find(attrs={"Id": "PNV"}).contents[0])["value"]
        self.framer.office["officename"] = officename
        self.framer.office["officeslug"] = slugify(officename)
        self.framer.office["active"] = True
        self.framer.office["officeid"] = self.framer.office["officeslug"]
        self.framer.contest["election_id"] = election.id
        self.framer.contest["resultsource_id"] = src.id
        self.framer.contest["seatnum"] = seatnum
        self.framer.contest["is_uncontested"] = False
        self.framer.contest["is_national"] = False
        self.framer.contest["is_statewide"] = True
        self.framer.contest["level"] = level
        self.framer.contest["is_ballot_measure"] = False
        self.framer.contest["is_judicial"] = True
        self.framer.contest["is_runoff"] = False
        self.framer.contest["reporttype"] = None
        self.framer.contest["poss_error"] = False
        if self.framer._to_num(precinctstotal)["convert"] == True:
            pt = self.framer._to_num(precinctstotal)["value"]
            self.framer.contest["precinctstotal"] = pt
        else:
            self.framer.contest["precinctstotal"] = None
            raise Exception("precinctstotal is not a number")
        if self.framer._to_num(precinctsreport)["convert"] == True:
            pr = self.framer._to_num(precinctsreport)["value"]
            self.framer.contest["precinctsreporting"] = pr
        else:
            self.framer.contest["precinctsreporting"] = None
            raise Exception("precinctsreporting is not a number")
        self.framer.contest["precinctsreportingpct"] = self.framer._calc_pct(
            self.framer.contest["precinctsreporting"], self.framer.contest["precinctstotal"])
        self.framer.contest["votersregistered"] = self.framer._to_num(None)["value"]
        self.framer.contest["votersturnout"] = self.framer._to_num(None)["value"]
        self.framer.contest["contestname"] = self.framer.office["officename"]
        self.framer.contest["contestdescription"] = None
        if race_id == "140":
            self.framer.contest["contestid"] = self.saver._make_contest_id(
                election.electionid,
                src.source_short,
                self.framer.contest["level"],
                self.framer.office["officeslug"],
            )
            self.framer.judicial["ballotorder"] = None
            self.framer.judicial["firstname"] = None
            self.framer.judicial["lastname"] = None
            self.framer.judicial["fullname"] = fullname
            self.framer.judicial["judicialslug"] = slugify(fullname)
            self.framer.judicial["yescount"] = yescount
            self.framer.judicial["yespct"] = yespct
            self.framer.judicial["nocount"] = nocount
            self.framer.judicial["nopct"] = nopct
            self.framer.judicial["poss_error"] = False
            self.framer.judicial["judgeid"] = self.saver._make_this_id(
                "judicial",
                self.framer.contest["contestid"],
                self.framer.judicial["judicialslug"],
            )
        elif race_id == "150":
            self.framer.contest["contestid"] = self.saver._make_contest_id(
                election.electionid,
                src.source_short,
                self.framer.contest["level"],
                self.framer.office["officeslug"],
            )
            self.framer.judicial["ballotorder"] = None
            self.framer.judicial["firstname"] = None
            self.framer.judicial["lastname"] = None
            self.framer.judicial["fullname"] = fullname
            self.framer.judicial["judicialslug"] = slugify(fullname)
            self.framer.judicial["yescount"] = yescount
            self.framer.judicial["yespct"] = yespct
            self.framer.judicial["nocount"] = nocount
            self.framer.judicial["nopct"] = nopct
            self.framer.judicial["poss_error"] = False
            self.framer.judicial["judgeid"] = self.saver._make_this_id(
                "judicial",
                self.framer.contest["contestid"],
                self.framer.judicial["judicialslug"],
            )
        return self.framer

    def _compile_measure(self, race, election, src):
        """
        """
        this_type = "Proposition"
        fullname = unicode(race.attrs["contest_title"])
        description = unicode(race.attrs["contest_title"])
        prop_num = unicode(race.attrs["race_seq_nbr"])
        officename = self.framer._concat(
            this_type,
            prop_num,
            delimiter=" ",
        )
        level = None
        seatnum = None
        precinctstotal = race.attrs["total_precincts"]
        precinctsreport = race.attrs["counted_precincts"]
        vote_counts = race.find_all("ChoiceTotal")
        yescount = self.framer._to_num(vote_counts[0].attrs["c_total_votes"])["value"]
        nocount = self.framer._to_num(vote_counts[1].attrs["c_total_votes"])["value"]
        total = yescount + nocount
        yespct = self.framer._calc_pct(yescount, total)
        nopct = self.framer._calc_pct(nocount, total)
        poss_error = False
        self.framer.office["officename"] = unicode(officename)
        self.framer.office["officeslug"] = slugify(officename)
        self.framer.office["active"] = True
        self.framer.office["officeid"] = self.framer.office["officeslug"]
        self.framer.contest["election_id"] = election.id
        self.framer.contest["resultsource_id"] = src.id
        self.framer.contest["seatnum"] = seatnum
        self.framer.contest["is_uncontested"] = False
        self.framer.contest["is_national"] = False
        self.framer.contest["is_statewide"] = True
        self.framer.contest["level"] = "california"
        self.framer.contest["is_ballot_measure"] = True
        self.framer.contest["is_judicial"] = False
        self.framer.contest["is_runoff"] = False
        self.framer.contest["reporttype"] = None
        self.framer.contest["poss_error"] = poss_error
        if self.framer._to_num(precinctstotal)["convert"] == True:
            pt = self.framer._to_num(precinctstotal)["value"]
            self.framer.contest["precinctstotal"] = pt
        else:
            self.framer.contest["precinctstotal"] = None
            raise Exception("precinctstotal is not a number")
        if self.framer._to_num(precinctsreport)["convert"] == True:
            pr = self.framer._to_num(precinctsreport)["value"]
            self.framer.contest["precinctsreporting"] = pr
        else:
            self.framer.contest["precinctsreporting"] = None
            raise Exception("precinctsreporting is not a number")
        self.framer.contest["precinctsreportingpct"] = self.framer._calc_pct(
            self.framer.contest["precinctsreporting"],
            self.framer.contest["precinctstotal"]
        )
        self.framer.contest["votersregistered"] = self.framer._to_num(race.attrs["reg_voters"])["value"]
        self.framer.contest["votersturnout"] = self.framer._to_num(None)["value"]
        self.framer.contest["contestname"] = self.framer._concat(
            officename,
            fullname,
            delimiter=" ",
        )
        self.framer.contest["contestdescription"] = description
        self.framer.contest["contestid"] = self.saver._make_contest_id(
            election.electionid,
            src.source_short,
            self.framer.contest["level"],
            self.framer.office["officeslug"],
        )
        self.framer.measure["ballotorder"] = None
        self.framer.measure["fullname"] = officename
        self.framer.measure["measureslug"] = slugify(self.framer.contest["contestname"])
        self.framer.measure["description"] = description
        self.framer.measure["yescount"] = yescount
        self.framer.measure["yespct"] = yespct
        self.framer.measure["nocount"] = nocount
        self.framer.measure["nopct"] = nopct
        self.framer.measure["poss_error"] = poss_error
        self.framer.measure["measureid"] = self.saver._make_this_id(
            "measure",
            self.framer.contest["contestid"],
            slugify(self.framer.measure["description"]),
        )
        return self.framer

    def _compile_candidate(self, race, election, src):
        """
        """
        this_type = "Candidate"
        officename = unicode(race.attrs["contest_title"])
        description = unicode(race.attrs["contest_title"])
        prop_num = unicode(race.attrs["race_seq_nbr"])
        level = "Orange"
        seatnum = None
        precinctstotal = race.attrs["total_precincts"]
        precinctsreport = race.attrs["counted_precincts"]
        reporttype = None
        poss_error = False
        self.framer.office["officename"] = officename
        self.framer.office["officeslug"] = slugify(officename)
        self.framer.office["active"] = True
        self.framer.office["officeid"] = self.framer.office["officeslug"]
        self.framer.contest["election_id"] = election.id
        self.framer.contest["resultsource_id"] = src.id
        self.framer.contest["seatnum"] = seatnum
        self.framer.contest["is_uncontested"] = False
        self.framer.contest["is_national"] = False
        self.framer.contest["is_statewide"] = False
        self.framer.contest["level"] = level
        self.framer.contest["is_ballot_measure"] = False
        self.framer.contest["is_judicial"] = False
        self.framer.contest["is_runoff"] = False
        self.framer.contest["reporttype"] = reporttype
        self.framer.contest["poss_error"] = poss_error
        if self.framer._to_num(precinctstotal)["convert"] == True:
            pt = self.framer._to_num(precinctstotal)["value"]
            self.framer.contest["precinctstotal"] = pt
        else:
            self.framer.contest["precinctstotal"] = None
            raise Exception("precinctstotal is not a number")
        if self.framer._to_num(precinctsreport)["convert"] == True:
            pr = self.framer._to_num(precinctsreport)["value"]
            self.framer.contest["precinctsreporting"] = pr
        else:
            self.framer.contest["precinctsreporting"] = None
            raise Exception("precinctsreporting is not a number")
        self.framer.contest["precinctsreportingpct"] = self.framer._calc_pct(
            self.framer.contest["precinctsreporting"],
            self.framer.contest["precinctstotal"]
        )
        self.framer.contest["votersregistered"] = self.framer._to_num(race.attrs["reg_voters"])["value"]
        self.framer.contest["votersturnout"] = self.framer._to_num(None)["value"]
        self.framer.contest["contestname"] = "%s %s" % (level, self.framer.office["officename"])
        self.framer.contest["contestdescription"] = None
        self.framer.contest["contestid"] = self.saver._make_contest_id(
            election.electionid,
            src.source_short,
            self.framer.contest["level"].lower(),
            self.framer.office["officeslug"],
        )
        self.framer.candidates = []
        for candidate in race.find_all("ChoiceTotal"):
            this_candidate = {}
            fullname = unicode(candidate.attrs["candidate_name"].title())
            party = unicode(candidate.attrs["party"].title())
            if party == "Democratic":
                party = "Democrat"
            votecount = self.framer._to_num(candidate.attrs["c_total_votes"])["value"]
            votepct = 0
            this_candidate["ballotorder"] = candidate.attrs["cand_Seq_nbr"]
            this_candidate["firstname"] = None
            this_candidate["lastname"] = None
            this_candidate["fullname"] = fullname.replace("* ", "")
            this_candidate["candidateslug"] = slugify(fullname)
            this_candidate["party"] = party
            this_candidate["incumbent"] = False
            this_candidate["votecount"] = votecount
            this_candidate["votepct"] = votepct
            this_candidate["poss_error"] = False
            this_candidate["candidateid"] = self.saver._make_this_id(
                "candidate",
                self.framer.contest["contestid"],
                this_candidate["candidateslug"],
            )
            self.framer.candidates.append(this_candidate)
        return self.framer

if __name__ == '__main__':
    task_run = BuildSosResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
