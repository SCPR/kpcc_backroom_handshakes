from __future__ import division
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
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
            soup = BeautifulSoup(open(latest_path), "xml")
            file_timestring = unicode(soup.find("IssueDate").contents[0])
            file_timestamp = parse(file_timestring, dayfirst=False).datetime
            update_this = saver._eval_timestamps(
                file_timestamp, src.source_latest)
            if update_this == False:
                logger.debug(
                    "we have newer data in the database so let's delete these files")
                os.remove(latest_path)
            else:
                logger.debug("Updating timestamps in the database")
                saver._update_result_timestamps(src, file_timestamp)
                races = soup.find_all("Contest")
                for race in races:
                    frame = Framer()
                    r = race.find("TotalVotes")
                    if race.ContestIdentifier.attrs["IdNumber"][0:3] == "140":
                        """
                        this is a judicial candidate
                        """
                        this_type = "judicial"
                        contestname = unicode(" ".join(race.ContestName.stripped_strings))
                        officename_idx = frame._find_nth(contestname, " - ", 1)
                        officename = unicode(contestname[:officename_idx])
                        fullname_idx = frame._find_nth(
                            contestname, " - ", 1) + 3
                        fullname = unicode(contestname[fullname_idx:])
                        level = None
                        seatnum = unicode(
                            race.ContestIdentifier.attrs["IdNumber"][-4:])
                        precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                        precinctsreport = r.find(
                            attrs={"Id": "PR"}).contents[0]
                        reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                        yescount = r.find_all("Selection")[
                            0].ValidVotes.contents[0]
                        yespct = r.find(attrs={"Id": "PYV"}).contents[0]
                        nocount = r.find_all("Selection")[
                            1].ValidVotes.contents[0]
                        nopct = r.find(attrs={"Id": "PNV"}).contents[0]
                        frame.office["officename"] = officename
                        frame.office["officeslug"] = frame._slug(officename)
                        frame.office["active"] = True
                        frame.contest["election_id"] = election.id
                        frame.contest["resultsource_id"] = src.id
                        frame.contest["seatnum"] = seatnum
                        frame.contest["is_uncontested"] = False
                        frame.contest["is_national"] = False
                        frame.contest["is_statewide"] = True
                        frame.contest["level"] = "california"
                        frame.contest["is_ballot_measure"] = False
                        frame.contest["is_judicial"] = True
                        frame.contest["is_runoff"] = False
                        frame.contest["reporttype"] = reporttype
                        if frame._to_num(precinctstotal)["change"] == True:
                            pt = frame._to_num(precinctstotal)["value"]
                            frame.contest["precinctstotal"] = pt
                        else:
                            frame.contest["precinctstotal"] = None
                            raise Exception("precinctstotal is not a number")
                        if frame._to_num(precinctsreport)["change"] == True:
                            pr = frame._to_num(precinctsreport)["value"]
                            frame.contest["precinctsreporting"] = pr
                        else:
                            frame.contest["precinctsreporting"] = None
                            raise Exception(
                                "precinctsreporting is not a number")
                        frame.contest["precinctsreportingpct"] = frame._calc_pct(
                            frame.contest["precinctsreporting"],
                            frame.contest["precinctstotal"]
                        )
                        frame.contest["votersregistered"] = None
                        frame.contest["votersturnout"] = None
                        frame.contest["contestname"] = frame.office[
                            "officename"]
                        frame.contest["contestdescription"] = None
                        frame.contest["contestid"] = frame._concat(
                            election.electionid,
                            src.source_short,
                            frame.contest["level"],
                            frame.office["officeslug"],
                            frame.contest["seatnum"],
                            delimiter="-"
                        )
                        frame.judicial["ballotorder"] = None
                        frame.judicial["firstname"] = None
                        frame.judicial["lastname"] = None
                        frame.judicial["fullname"] = fullname
                        frame.judicial["judicialslug"] = frame._slug(fullname)
                        frame.judicial["yescount"] = yescount
                        frame.judicial["yespct"] = yespct
                        frame.judicial["nocount"] = nocount
                        frame.judicial["nopct"] = nopct
                        frame.judicial["judgeid"] = frame._concat(
                            frame.judicial["judicialslug"],
                            frame.contest["contestid"],
                            delimiter="-"
                        )
                        saver.make_office(frame.office)
                        saver.make_contest(frame.office, frame.contest)
                        saver.make_judicial(frame.contest, frame.judicial)

                    elif race.ContestIdentifier.attrs["IdNumber"][0:3] == "150":
                        """
                        this is a judicial candidate
                        """
                        this_type = "judicial"
                        contestname = unicode(" ".join(race.ContestName.stripped_strings))
                        officename_idx = frame._find_nth(contestname, " - ", 2)
                        officename = unicode(
                            contestname[:officename_idx].replace(" - ", " "))
                        fullname_idx = frame._find_nth(
                            contestname, " - ", 2) + 3
                        fullname = unicode(contestname[fullname_idx:])
                        level = None
                        seatnum = unicode(
                            race.ContestIdentifier.attrs["IdNumber"][-4:])
                        precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                        precinctsreport = r.find(
                            attrs={"Id": "PR"}).contents[0]
                        reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                        yescount = r.find_all("Selection")[
                            0].ValidVotes.contents[0]
                        yespct = r.find(attrs={"Id": "PYV"}).contents[0]
                        nocount = r.find_all("Selection")[
                            1].ValidVotes.contents[0]
                        nopct = r.find(attrs={"Id": "PNV"}).contents[0]
                        frame.office["officename"] = officename
                        frame.office["officeslug"] = frame._slug(officename)
                        frame.office["active"] = True
                        frame.contest["election_id"] = election.id
                        frame.contest["resultsource_id"] = src.id
                        frame.contest["seatnum"] = seatnum
                        frame.contest["is_uncontested"] = False
                        frame.contest["is_national"] = False
                        frame.contest["is_statewide"] = True
                        frame.contest["level"] = "california"
                        frame.contest["is_ballot_measure"] = False
                        frame.contest["is_judicial"] = True
                        frame.contest["is_runoff"] = False
                        frame.contest["reporttype"] = reporttype
                        if frame._to_num(precinctstotal)["change"] == True:
                            pt = frame._to_num(precinctstotal)["value"]
                            frame.contest["precinctstotal"] = pt
                        else:
                            frame.contest["precinctstotal"] = None
                            raise Exception("precinctstotal is not a number")
                        if frame._to_num(precinctsreport)["change"] == True:
                            pr = frame._to_num(precinctsreport)["value"]
                            frame.contest["precinctsreporting"] = pr
                        else:
                            frame.contest["precinctsreporting"] = None
                            raise Exception(
                                "precinctsreporting is not a number")
                        frame.contest["precinctsreportingpct"] = frame._calc_pct(
                            frame.contest["precinctsreporting"],
                            frame.contest["precinctstotal"]
                        )
                        frame.contest["votersregistered"] = None
                        frame.contest["votersturnout"] = None
                        frame.contest["contestname"] = frame.office[
                            "officename"]
                        frame.contest["contestdescription"] = None
                        frame.contest["contestid"] = frame._concat(
                            election.electionid,
                            src.source_short,
                            frame.contest["level"],
                            frame.office["officeslug"],
                            frame.contest["seatnum"],
                            delimiter="-"
                        )
                        frame.judicial["ballotorder"] = None
                        frame.judicial["firstname"] = None
                        frame.judicial["lastname"] = None
                        frame.judicial["fullname"] = fullname
                        frame.judicial["judicialslug"] = frame._slug(fullname)
                        frame.judicial["yescount"] = yescount
                        frame.judicial["yespct"] = yespct
                        frame.judicial["nocount"] = nocount
                        frame.judicial["nopct"] = nopct
                        frame.judicial["judgeid"] = frame._concat(
                            frame.judicial["judicialslug"],
                            frame.contest["contestid"],
                            delimiter="-"
                        )
                        saver.make_office(frame.office)
                        saver.make_contest(frame.office, frame.contest)
                        saver.make_judicial(frame.contest, frame.judicial)

                    elif race.ContestIdentifier.attrs["IdNumber"][0:3] == "190":
                        """
                        this is a measure
                        """
                        this_type = "measure"
                        contestname = unicode(" ".join(race.ContestName.stripped_strings))
                        officename = frame._concat(
                            "Measure",
                            contestname,
                            delimiter="-",
                        )
                        fullname = unicode(race.ContestName.contents[0])
                        level = None
                        seatnum = unicode(
                            race.ContestIdentifier.attrs["IdNumber"][-4:])
                        precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                        precinctsreport = r.find(
                            attrs={"Id": "PR"}).contents[0]
                        reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                        yescount = r.find_all("Selection")[
                            0].ValidVotes.contents[0]
                        yespct = r.find(attrs={"Id": "PYV"}).contents[0]
                        nocount = r.find_all("Selection")[
                            1].ValidVotes.contents[0]
                        nopct = r.find(attrs={"Id": "PNV"}).contents[0]
                        frame.office["officename"] = officename
                        frame.office["officeslug"] = frame._slug(officename)
                        frame.office["active"] = True
                        frame.contest["election_id"] = election.id
                        frame.contest["resultsource_id"] = src.id
                        frame.contest["seatnum"] = seatnum
                        frame.contest["is_uncontested"] = False
                        frame.contest["is_national"] = False
                        frame.contest["is_statewide"] = True
                        frame.contest["level"] = "california"
                        frame.contest["is_ballot_measure"] = False
                        frame.contest["is_judicial"] = True
                        frame.contest["is_runoff"] = False
                        frame.contest["reporttype"] = reporttype
                        if frame._to_num(precinctstotal)["change"] == True:
                            pt = frame._to_num(precinctstotal)["value"]
                            frame.contest["precinctstotal"] = pt
                        else:
                            frame.contest["precinctstotal"] = None
                            raise Exception("precinctstotal is not a number")
                        if frame._to_num(precinctsreport)["change"] == True:
                            pr = frame._to_num(precinctsreport)["value"]
                            frame.contest["precinctsreporting"] = pr
                        else:
                            frame.contest["precinctsreporting"] = None
                            raise Exception(
                                "precinctsreporting is not a number")
                        frame.contest["precinctsreportingpct"] = frame._calc_pct(
                            frame.contest["precinctsreporting"],
                            frame.contest["precinctstotal"]
                        )
                        frame.contest["votersregistered"] = None
                        frame.contest["votersturnout"] = None
                        frame.contest["contestname"] = frame.office[
                            "officename"]
                        frame.contest["contestdescription"] = None
                        frame.contest["contestid"] = frame._concat(
                            election.electionid,
                            src.source_short,
                            frame.contest["level"],
                            frame.office["officeslug"],
                            frame.contest["seatnum"],
                            delimiter="-"
                        )
                        frame.measure["ballotorder"] = None
                        frame.measure["fullname"] = fullname
                        frame.measure["measureslug"] = frame._slug(fullname)
                        frame.measure["description"] = None
                        frame.measure["yescount"] = yescount
                        frame.measure["yespct"] = yespct
                        frame.measure["nocount"] = nocount
                        frame.measure["nopct"] = nopct
                        frame.measure["measureid"] = frame._concat(
                            frame.measure["measureslug"],
                            frame.contest["contestid"],
                            delimiter="-"
                        )
                        saver.make_office(frame.office)
                        saver.make_contest(frame.office, frame.contest)
                        saver.make_measure(frame.contest, frame.measure)

                    else:
                        """
                        this is a non-judicial candidate
                        """
                        this_type = "candidate"
                        contestname = unicode(" ".join(race.ContestName.stripped_strings))
                        officename_idx = frame._find_nth(contestname, " - ", 1)
                        officename = unicode(contestname[:officename_idx])
                        level_idx = frame._find_nth(contestname, " - ", 1) + 3
                        level = unicode(contestname[level_idx:].replace(
                            " Results", "").lower())
                        seatnum = unicode(
                            race.ContestIdentifier.attrs["IdNumber"][-4:])
                        precinctstotal = r.find(attrs={"Id": "TP"}).contents[0]
                        precinctsreport = r.find(
                            attrs={"Id": "PR"}).contents[0]
                        reporttype = r.find(attrs={"Id": "RT"}).contents[0]
                        frame.office["officename"] = officename
                        frame.office["officeslug"] = frame._slug(officename)
                        frame.office["active"] = True
                        frame.contest["election_id"] = election.id
                        frame.contest["resultsource_id"] = src.id
                        frame.contest["seatnum"] = seatnum
                        frame.contest["is_uncontested"] = False
                        frame.contest["is_national"] = False
                        frame.contest["is_statewide"] = True
                        frame.contest["level"] = level
                        frame.contest["is_ballot_measure"] = False
                        frame.contest["is_judicial"] = True
                        frame.contest["is_runoff"] = False
                        frame.contest["reporttype"] = reporttype
                        if frame._to_num(precinctstotal)["change"] == True:
                            pt = frame._to_num(precinctstotal)["value"]
                            frame.contest["precinctstotal"] = pt
                        else:
                            frame.contest["precinctstotal"] = None
                            raise Exception("precinctstotal is not a number")
                        if frame._to_num(precinctsreport)["change"] == True:
                            pr = frame._to_num(precinctsreport)["value"]
                            frame.contest["precinctsreporting"] = pr
                        else:
                            frame.contest["precinctsreporting"] = None
                            raise Exception(
                                "precinctsreporting is not a number")
                        frame.contest["precinctsreportingpct"] = frame._calc_pct(
                            frame.contest["precinctsreporting"],
                            frame.contest["precinctstotal"]
                        )
                        frame.contest["votersregistered"] = None
                        frame.contest["votersturnout"] = None
                        frame.contest["contestname"] = frame.office[
                            "officename"]
                        frame.contest["contestdescription"] = None
                        frame.contest["contestid"] = frame._concat(
                            election.electionid,
                            src.source_short,
                            frame.contest["level"],
                            frame.office["officeslug"],
                            frame.contest["seatnum"],
                            delimiter="-"
                        )
                        saver.make_office(frame.office)
                        saver.make_contest(frame.office, frame.contest)
                        for candidate in r.find_all("Selection"):
                            fullname = unicode(
                                candidate.Candidate.CandidateFullName.PersonFullName.contents[0])
                            party = unicode(
                                candidate.AffiliationIdentifier.RegisteredName.contents[0])
                            if party == "Democratic":
                                party = "Democrat"
                            votecount = candidate.ValidVotes.contents[0]
                            votepct = candidate.CountMetric.contents[0]
                            frame.candidate["ballotorder"] = None
                            frame.candidate["firstname"] = None
                            frame.candidate["lastname"] = None
                            frame.candidate["fullname"] = fullname
                            frame.candidate[
                                "candidateslug"] = frame._slug(fullname)
                            frame.candidate["party"] = party
                            frame.candidate["incumbent"] = False
                            frame.candidate[
                                "votecount"] = candidate.ValidVotes.contents[0]
                            frame.candidate[
                                "votepct"] = candidate.CountMetric.contents[0]
                            frame.candidate["candidateid"] = frame._concat(
                                frame.candidate["candidateslug"],
                                frame.contest["contestid"],
                                delimiter="-"
                            )
                            saver.make_candidate(
                                frame.contest, frame.candidate)
                os.remove(latest_path)


if __name__ == '__main__':
    task_run = BuildSosResults()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
