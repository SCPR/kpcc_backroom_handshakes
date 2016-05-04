Modeling The Data
=================

Election
---------

For our purposes the macro unit of data.

Schema:
    * id: Xxxxx
        - Example Value: Xxxxx
    * unique_id: Xxxxx
        - Example Value: Xxxxx
    * type: Xxxxx
        - Example Value: primary, general, special
    * testresults: Xxxxx
        - Example Value: Xxxxx
    * liveresults: Xxxxx
        - Example Value: Xxxxx
    * electiondate: Xxxxx
        - Example Value: Xxxxx
    * national: Xxxxx
        - Example Value: Xxxxx
    * parsed_json: Xxxxx
        - Example Value: Xxxxx
    * next_request: Xxxxx
        - Example Value: Xxxxx
    * datafile: Xxxxx
        - Example Value: Xxxxx
    * resultslevel: Xxxxx
        - Example Value: Xxxxx

Race
-----

Xxxxxxxxxxxxxxxx

Schema:
    * id: Xxxxx
        - Example Value: Xxxxx
    * unique_id: Xxxxx
        - Example Value: Xxxxx
    * type: Xxxxx
        - Example Value: office, initiative
    * electiondate: Xxxxx
        - Example Value: Xxxxx
    * statepostal: Xxxxx
        - Example Value: Xxxxx
    * statename: Xxxxx
        - Example Value: Xxxxx
    * test: Xxxxx
        - Example Value: Xxxxx
    * raceid: Xxxxx
        - Example Value: Xxxxx
    * racetype: Xxxxx
        - Example Value: Xxxxx
    * racetypeid: Xxxxx
        - Example Value: Xxxxx
    * officeid: Xxxxx
        - Example Value: Xxxxx
    * officename: Xxxxx
        - Example Value: Xxxxx
    * party: Xxxxx
        - Example Value: Xxxxx
    * seatname: Xxxxx
        - Example Value: Xxxxx
    * description: Xxxxx
        - Example Value: Xxxxx
    * seatnum: Xxxxx
        - Example Value: Xxxxx
    * uncontested: Xxxxx
        - Example Value: Xxxxx
    * lastupdated: Xxxxx
        - Example Value: Xxxxx
    * initialization_data: Xxxxx
        - Example Value: Xxxxx
    * national: Xxxxx
        - Example Value: Xxxxx
    * candidates: Xxxxx
        - Example Value: Xxxxx
    * reportingunits: Xxxxx
        - Example Value: Xxxxx
    * is_ballot_measure: Xxxxx
        - Example Value: Xxxxx

Candidate
---------

Based on the [thoughts of some very smart people](https://github.com/newsdev/elex/blob/master/elex/api/models.py#L272), we're going to follow along and say a candidate can be a person OR a ballot measure

Schema:
    * id: Xxxxx
        - Example Value: Xxxxx
    * unique_id: Xxxxx
        - Example Value: Xxxxx
    * candidateid: Xxxxx
        - Example Value: Xxxxx
    * polid: Xxxxx
        - Example Value: Xxxxx
    * electiondate: Xxxxx
        - Example Value: Xxxxx
    * first: Xxxxx
        - Example Value: Xxxxx
    * last: Xxxxx
        - Example Value: Xxxxx
    * party: Xxxxx
        - Example Value: Xxxxx
    * votecount: Xxxxx
        - Example Value: Xxxxx
    * votepct: Xxxxx
        - Example Value: Xxxxx
    * delegatecount: Xxxxx
        - Example Value: Xxxxx
    * winner: Xxxxx
        - Example Value: Xxxxx
    * runoff: Xxxxx
        - Example Value: Xxxxx
    * is_ballot_measure: Xxxxx
        - Example Value: Xxxxx
    * level: Xxxxx
        - Example Value: Xxxxx
    * reportingunitname: Xxxxx
        - Example Value: Xxxxx
    * reportingunitid: Xxxxx
        - Example Value: Xxxxx
    * fipscode: Xxxxx
        - Example Value: Xxxxx
    * lastupdated: Xxxxx
        - Example Value: Xxxxx
    * precinctsreporting: Xxxxx
        - Example Value: Xxxxx
    * precinctstotal: Xxxxx
        - Example Value: Xxxxx
    * precinctsreportingpct: Xxxxx
        - Example Value: Xxxxx
    * uncontested: Xxxxx
        - Example Value: Xxxxx
    * test: Xxxxx
        - Example Value: Xxxxx
    * raceid: Xxxxx
        - Example Value: Xxxxx
    * statepostal: Xxxxx
        - Example Value: Xxxxx
    * statename: Xxxxx
        - Example Value: Xxxxx
    * racetype: Xxxxx
        - Example Value: Xxxxx
    * racetypeid: Xxxxx
        - Example Value: Xxxxx
    * officeid: Xxxxx
        - Example Value: Xxxxx
    * officename: Xxxxx
        - Example Value: Xxxxx
    * seatname: Xxxxx
        - Example Value: Xxxxx
    * description: Xxxxx
        - Example Value: Xxxxx
    * seatnum: Xxxxx
        - Example Value: Xxxxx
    * national: Xxxxx
        - Example Value: Xxxxx
    * incumbent: Xxxxx
        - Example Value: Xxxxx

ReportingUnit
-------------

Xxxxxxxxxxxxxxxxxx

Schema:
    * id: Xxxxx
        - Example Value: Xxxxx
    * electiondate: Xxxxx
        - Example Value: Xxxxx
    * statepostal: Xxxxx
        - Example Value: Xxxxx
    * statename: Xxxxx
        - Example Value: Xxxxx
    * level: Xxxxx
        - Example Value: Xxxxx
    * reportingunitname: Xxxxx
        - Example Value: Xxxxx
    * reportingunitid: Xxxxx
        - Example Value: Xxxxx
    * fipscode: Xxxxx
        - Example Value: Xxxxx
    * lastupdated: Xxxxx
        - Example Value: Xxxxx
    * precinctsreporting: Xxxxx
        - Example Value: Xxxxx
    * precinctstotal: Xxxxx
        - Example Value: Xxxxx
    * precinctsreportingpct: Xxxxx
        - Example Value: Xxxxx
    * uncontested: Xxxxx
        - Example Value: Xxxxx
    * test: Xxxxx
        - Example Value: Xxxxx
    * raceid: Xxxxx
        - Example Value: Xxxxx
    * racetype: Xxxxx
        - Example Value: Xxxxx
    * racetypeid: Xxxxx
        - Example Value: Xxxxx
    * officeid: Xxxxx
        - Example Value: Xxxxx
    * officename: Xxxxx
        - Example Value: Xxxxx
    * seatname: Xxxxx
        - Example Value: Xxxxx
    * description: Xxxxx
        - Example Value: Xxxxx
    * seatnum: Xxxxx
        - Example Value: Xxxxx
    * national: Xxxxx
        - Example Value: Xxxxx
    * candidates: Xxxxx
        - Example Value: Xxxxx
    * votecount: Xxxxx
        - Example Value: Xxxxx
