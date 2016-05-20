from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime
from ballot_box.utils_files import Retriever
from ballot_box.utils_data import Framer
from ballot_box.utils_import import Saver
from ballot_box.models import ResultSource, Election
import logging
import time
import datetime
import os.path
import shutil
from bs4 import BeautifulSoup
from delorean import parse

logger = logging.getLogger("kpcc_backroom_handshakes")


class BuildSosResults(object):
    """
    scaffolding to ingest secretary of state election results
    """

    data_directory = "%s/ballot_box/data_dump/" % (settings.BASE_DIR)

    sources = ResultSource.objects.filter(
        source_short="sos", source_active=True)

    def _init(self, *args, **kwargs):
        """
        """
        for src in self.sources:
            self.get_results_file(src, self.data_directory)
            self.parse_results_file(src, self.data_directory)

    def get_results_file(self, src, data_directory):
        """
        """
        retrieve = Retriever()

        # download the latest results file
        retrieve._request_results_and_save(src, data_directory)

        # move latest files to a working directory
        retrieve._create_directory_for_latest_file(src, data_directory)

        # create timestamped version of a file deemed latest
        retrieve._copy_timestamped_file_to_latest(src, data_directory)

        # move timestamped zipfile to archives
        retrieve._archive_downloaded_file(src, data_directory)

        # compare files in a zipfile with a list of expected files
        retrieve._found_required_files(src, data_directory)

        # if the item is a zipfile extract the files
        retrieve._unzip_latest_file(src, data_directory)

    def parse_results_file(self, src, data_directory):
        """
        """
        saver = Saver()

        latest_directory = "%s%s_latest" % (data_directory, src.source_short)

        election = Election.objects.filter(test_results=True).first()

        for file in src.source_files.split(", "):
            latest_path = os.path.join(latest_directory, file)
            file_exists = os.path.isfile(latest_path)
            file_has_size = os.path.getsize(latest_path)
            if file_exists == True and file_has_size > 0:
                soup = BeautifulSoup(open(latest_path), "xml")
                file_timestring = unicode(soup.find("IssueDate").contents[0])
                file_timestamp = parse(file_timestring, dayfirst=False).datetime
                update_this = saver._eval_timestamps(
                    file_timestamp, src.source_latest)
                if update_this == False:
                    logger.info(
                        "@chrislkeller we have newer data in the database so let's delete these files")
                    os.remove(latest_path)
                else:
                    logger.info("@chrislkeller we have new data to save and we'll update timestamps in the database")
                    saver._update_result_timestamps(src, file_timestamp)
                    races = soup.find_all("Contest")
                    for race in races:
                        framer = Framer()
                        r = race.find("TotalVotes")
                        if race.ContestIdentifier.attrs["IdNumber"][0:3] == "140":
                            """
                            this is a judicial candidate
                            """
                            this_type = "judicial"
                            contestname = unicode(" ".join(race.ContestName.stripped_strings))
                            officename_idx = framer._find_nth(contestname, " - ", 1)
                            officename = unicode(contestname[:officename_idx])
                            fullname_idx = framer._find_nth(
                                contestname, " - ", 1) + 3
                            fullname = unicode(contestname[fullname_idx:])
                            level = None
                            seatnum = None
                            precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                            precinctsreport = r.find(
                                attrs={"Id": "PR"}).contents[0]
                            reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                            yescount = framer._to_num(r.find_all("Selection")[
                                0].ValidVotes.contents[0])["value"]
                            yespct = framer._to_num(r.find(attrs={"Id": "PYV"}).contents[0])["value"]
                            nocount = framer._to_num(r.find_all("Selection")[
                                1].ValidVotes.contents[0])["value"]
                            nopct = framer._to_num(r.find(attrs={"Id": "PNV"}).contents[0])["value"]
                            framer.office["officename"] = officename
                            framer.office["officeslug"] = framer._slug(officename)
                            framer.office["active"] = True
                            framer.contest["election_id"] = election.id
                            framer.contest["resultsource_id"] = src.id
                            framer.contest["seatnum"] = seatnum
                            framer.contest["is_uncontested"] = False
                            framer.contest["is_national"] = False
                            framer.contest["is_statewide"] = True
                            framer.contest["level"] = "california"
                            framer.contest["is_ballot_measure"] = False
                            framer.contest["is_judicial"] = True
                            framer.contest["is_runoff"] = False
                            framer.contest["reporttype"] = None
                            if framer._to_num(precinctstotal)["convert"] == True:
                                pt = framer._to_num(precinctstotal)["value"]
                                framer.contest["precinctstotal"] = pt
                            else:
                                framer.contest["precinctstotal"] = None
                                raise Exception("precinctstotal is not a number")
                            if framer._to_num(precinctsreport)["convert"] == True:
                                pr = framer._to_num(precinctsreport)["value"]
                                framer.contest["precinctsreporting"] = pr
                            else:
                                framer.contest["precinctsreporting"] = None
                                raise Exception(
                                    "precinctsreporting is not a number")
                            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                                framer.contest["precinctsreporting"],
                                framer.contest["precinctstotal"]
                            )
                            framer.contest["votersregistered"] = framer._to_num(None)["value"]
                            framer.contest["votersturnout"] = framer._to_num(None)["value"]
                            framer.contest["contestname"] = framer.office[
                                "officename"]
                            framer.contest["contestdescription"] = None
                            framer.contest["contestid"] = framer._concat(
                                election.electionid,
                                src.source_short,
                                framer.contest["level"],
                                framer.office["officeslug"],
                                framer.contest["seatnum"],
                                delimiter="-"
                            )
                            framer.judicial["ballotorder"] = None
                            framer.judicial["firstname"] = None
                            framer.judicial["lastname"] = None
                            framer.judicial["fullname"] = fullname
                            framer.judicial["judicialslug"] = framer._slug(fullname)
                            framer.judicial["yescount"] = yescount
                            framer.judicial["yespct"] = yespct
                            framer.judicial["nocount"] = nocount
                            framer.judicial["nopct"] = nopct
                            framer.judicial["judgeid"] = framer._concat(
                                framer.judicial["judicialslug"],
                                framer.contest["contestid"],
                                delimiter="-"
                            )
                            saver.make_office(framer.office)
                            saver.make_contest(framer.office, framer.contest)
                            saver.make_judicial(framer.contest, framer.judicial)

                        elif race.ContestIdentifier.attrs["IdNumber"][0:3] == "150":
                            """
                            this is a judicial candidate
                            """
                            this_type = "judicial"
                            contestname = unicode(" ".join(race.ContestName.stripped_strings))
                            officename_idx = framer._find_nth(contestname, " - ", 2)
                            officename = unicode(
                                contestname[:officename_idx].replace(" - ", " "))
                            fullname_idx = framer._find_nth(
                                contestname, " - ", 2) + 3
                            fullname = unicode(contestname[fullname_idx:])
                            level = None
                            seatnum = None
                            precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                            precinctsreport = r.find(
                                attrs={"Id": "PR"}).contents[0]
                            reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                            yescount = framer._to_num(r.find_all("Selection")[
                                0].ValidVotes.contents[0])["value"]
                            yespct = framer._to_num(r.find(attrs={"Id": "PYV"}).contents[0])["value"]
                            nocount = framer._to_num(r.find_all("Selection")[
                                1].ValidVotes.contents[0])["value"]
                            nopct = framer._to_num(r.find(attrs={"Id": "PNV"}).contents[0])["value"]
                            framer.office["officename"] = officename
                            framer.office["officeslug"] = framer._slug(officename)
                            framer.office["active"] = True
                            framer.contest["election_id"] = election.id
                            framer.contest["resultsource_id"] = src.id
                            framer.contest["seatnum"] = seatnum
                            framer.contest["is_uncontested"] = False
                            framer.contest["is_national"] = False
                            framer.contest["is_statewide"] = True
                            framer.contest["level"] = "california"
                            framer.contest["is_ballot_measure"] = False
                            framer.contest["is_judicial"] = True
                            framer.contest["is_runoff"] = False
                            framer.contest["reporttype"] = None
                            if framer._to_num(precinctstotal)["convert"] == True:
                                pt = framer._to_num(precinctstotal)["value"]
                                framer.contest["precinctstotal"] = pt
                            else:
                                framer.contest["precinctstotal"] = None
                                raise Exception("precinctstotal is not a number")
                            if framer._to_num(precinctsreport)["convert"] == True:
                                pr = framer._to_num(precinctsreport)["value"]
                                framer.contest["precinctsreporting"] = pr
                            else:
                                framer.contest["precinctsreporting"] = None
                                raise Exception(
                                    "precinctsreporting is not a number")
                            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                                framer.contest["precinctsreporting"],
                                framer.contest["precinctstotal"]
                            )
                            framer.contest["votersregistered"] = framer._to_num(None)["value"]
                            framer.contest["votersturnout"] = framer._to_num(None)["value"]
                            framer.contest["contestname"] = framer.office[
                                "officename"]
                            framer.contest["contestdescription"] = None
                            framer.contest["contestid"] = framer._concat(
                                election.electionid,
                                src.source_short,
                                framer.contest["level"],
                                framer.office["officeslug"],
                                framer.contest["seatnum"],
                                delimiter="-"
                            )
                            framer.judicial["ballotorder"] = None
                            framer.judicial["firstname"] = None
                            framer.judicial["lastname"] = None
                            framer.judicial["fullname"] = fullname
                            framer.judicial["judicialslug"] = framer._slug(fullname)
                            framer.judicial["yescount"] = yescount
                            framer.judicial["yespct"] = yespct
                            framer.judicial["nocount"] = nocount
                            framer.judicial["nopct"] = nopct
                            framer.judicial["judgeid"] = framer._concat(
                                framer.judicial["judicialslug"],
                                framer.contest["contestid"],
                                delimiter="-"
                            )
                            saver.make_office(framer.office)
                            saver.make_contest(framer.office, framer.contest)
                            saver.make_judicial(framer.contest, framer.judicial)

                        elif race.ContestIdentifier.attrs["IdNumber"][0:3] == "190":
                            """
                            this is a measure
                            """
                            this_type = "measure"
                            contestname = unicode(" ".join(race.ContestName.stripped_strings))
                            officename = framer._concat(
                                "Measure",
                                contestname,
                                delimiter="-",
                            )
                            fullname = unicode(race.ContestName.contents[0])
                            level = None
                            seatnum = None
                            precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                            precinctsreport = r.find(
                                attrs={"Id": "PR"}).contents[0]
                            reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                            yescount = framer._to_num(r.find_all("Selection")[
                                0].ValidVotes.contents[0])["value"]
                            yespct = framer._to_num(r.find(attrs={"Id": "PYV"}).contents[0])["value"]
                            nocount = framer._to_num(r.find_all("Selection")[
                                1].ValidVotes.contents[0])["value"]
                            nopct = framer._to_num(r.find(attrs={"Id": "PNV"}).contents[0])["value"]
                            framer.office["officename"] = officename
                            framer.office["officeslug"] = framer._slug(officename)
                            framer.office["active"] = True
                            framer.contest["election_id"] = election.id
                            framer.contest["resultsource_id"] = src.id
                            framer.contest["seatnum"] = seatnum
                            framer.contest["is_uncontested"] = False
                            framer.contest["is_national"] = False
                            framer.contest["is_statewide"] = True
                            framer.contest["level"] = "california"
                            framer.contest["is_ballot_measure"] = True
                            framer.contest["is_judicial"] = True
                            framer.contest["is_runoff"] = False
                            framer.contest["reporttype"] = None
                            if framer._to_num(precinctstotal)["convert"] == True:
                                pt = framer._to_num(precinctstotal)["value"]
                                framer.contest["precinctstotal"] = pt
                            else:
                                framer.contest["precinctstotal"] = None
                                raise Exception("precinctstotal is not a number")
                            if framer._to_num(precinctsreport)["convert"] == True:
                                pr = framer._to_num(precinctsreport)["value"]
                                framer.contest["precinctsreporting"] = pr
                            else:
                                framer.contest["precinctsreporting"] = None
                                raise Exception(
                                    "precinctsreporting is not a number")
                            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                                framer.contest["precinctsreporting"],
                                framer.contest["precinctstotal"]
                            )
                            framer.contest["votersregistered"] = framer._to_num(None)["value"]
                            framer.contest["votersturnout"] = framer._to_num(None)["value"]
                            framer.contest["contestname"] = framer.office[
                                "officename"]
                            framer.contest["contestdescription"] = None
                            framer.contest["contestid"] = framer._concat(
                                election.electionid,
                                src.source_short,
                                framer.contest["level"],
                                framer.office["officeslug"],
                                framer.contest["seatnum"],
                                delimiter="-"
                            )
                            framer.measure["ballotorder"] = None
                            framer.measure["fullname"] = fullname
                            framer.measure["measureslug"] = framer._slug(fullname)
                            framer.measure["description"] = None
                            framer.measure["yescount"] = yescount
                            framer.measure["yespct"] = yespct
                            framer.measure["nocount"] = nocount
                            framer.measure["nopct"] = nopct
                            framer.measure["measureid"] = framer._concat(
                                framer.measure["measureslug"],
                                framer.contest["contestid"],
                                delimiter="-"
                            )
                            saver.make_office(framer.office)
                            saver.make_contest(framer.office, framer.contest)
                            saver.make_measure(framer.contest, framer.measure)
                        else:
                            """
                            this is a non-judicial candidate
                            """
                            this_type = "candidate"
                            contestname = unicode(" ".join(race.ContestName.stripped_strings))
                            officename_idx = framer._find_nth(contestname, " - ", 1)
                            officename = unicode(contestname[:officename_idx])
                            level_idx = framer._find_nth(contestname, " - ", 1) + 3
                            level = unicode(contestname[level_idx:].replace(
                                " Results", "").lower())
                            seatnum = None
                            precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                            precinctsreport = r.find(
                                attrs={"Id": "PR"}).contents[0]
                            reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                            framer.office["officename"] = officename
                            framer.office["officeslug"] = framer._slug(officename)
                            framer.office["active"] = True
                            framer.contest["election_id"] = election.id
                            framer.contest["resultsource_id"] = src.id
                            framer.contest["seatnum"] = seatnum
                            framer.contest["is_uncontested"] = False
                            framer.contest["is_national"] = False
                            framer.contest["is_statewide"] = True
                            framer.contest["level"] = level
                            framer.contest["is_ballot_measure"] = False
                            framer.contest["is_judicial"] = True
                            framer.contest["is_runoff"] = False
                            framer.contest["reporttype"] = None
                            if framer._to_num(precinctstotal)["convert"] == True:
                                pt = framer._to_num(precinctstotal)["value"]
                                framer.contest["precinctstotal"] = pt
                            else:
                                framer.contest["precinctstotal"] = None
                                raise Exception("precinctstotal is not a number")

                            if framer._to_num(precinctsreport)["convert"] == True:
                                pr = framer._to_num(precinctsreport)["value"]
                                framer.contest["precinctsreporting"] = pr
                            else:
                                framer.contest["precinctsreporting"] = None
                                raise Exception(
                                    "precinctsreporting is not a number")
                            framer.contest["precinctsreportingpct"] = framer._calc_pct(
                                framer.contest["precinctsreporting"],
                                framer.contest["precinctstotal"]
                            )
                            framer.contest["votersregistered"] = framer._to_num(None)["value"]
                            framer.contest["votersturnout"] = framer._to_num(None)["value"]
                            framer.contest["contestname"] = framer.office[
                                "officename"]
                            framer.contest["contestdescription"] = None
                            framer.contest["contestid"] = framer._concat(
                                election.electionid,
                                src.source_short,
                                framer.contest["level"],
                                framer.office["officeslug"],
                                framer.contest["seatnum"],
                                delimiter="-"
                            )
                            saver.make_office(framer.office)
                            saver.make_contest(framer.office, framer.contest)
                            for candidate in r.find_all("Selection"):
                                fullname = unicode(
                                    candidate.Candidate.CandidateFullName.PersonFullName.contents[0])
                                party = unicode(
                                    candidate.AffiliationIdentifier.RegisteredName.contents[0])
                                if party == "Democratic":
                                    party = "Democrat"
                                votecount = framer._to_num(candidate.ValidVotes.contents[0])["value"]
                                votepct = framer._to_num(candidate.CountMetric.contents[0])["value"]
                                framer.candidate["ballotorder"] = None
                                framer.candidate["firstname"] = None
                                framer.candidate["lastname"] = None
                                framer.candidate["fullname"] = fullname
                                framer.candidate[
                                    "candidateslug"] = framer._slug(fullname)
                                framer.candidate["party"] = party
                                framer.candidate["incumbent"] = False
                                framer.candidate[
                                    "votecount"] = votecount
                                framer.candidate[
                                    "votepct"] = votepct
                                framer.candidate["candidateid"] = framer._concat(
                                    framer.candidate["candidateslug"],
                                    framer.contest["contestid"],
                                    delimiter="-"
                                )
                                saver.make_candidate(
                                    framer.contest, framer.candidate)
                    os.remove(latest_path)
                    logger.info("@chrislkeller we've finished processing sos results")
            else:
                logger.error("XML file to parse is not at expected location")

if __name__ == '__main__':
    task_run = BuildSosResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
