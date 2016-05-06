Modeling The Data
=================

Election
---------

For our purposes the macro unit of data.

* **type**: The type of election
    - Example: "Primary", "General", "Special"
* **unique_id**: Created from the type of election and the date of the election
    - Example: primary-2016-06-07
* **test_results**: Are These Test Results
    - Example: True/False
* **live_results**: Are These Live Results
    - Example: True/False
* **election_date**: Date of the Election
    - Example: 2016-06-07
* **poll_close_at**: Date and time time the polls close
    - Example: 2016-06-08 03:00:00.000000
* **national**: Is this a National Election?
    - Example: True/False
* ~~parsed_json~~
* ~~next_request~~
* ~~datafile~~
* ~~results_level~~
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

Race
-----

Xxxxxxxxxxxxxxxx

Schema:
    * election - foreign key
    * source - foreign key
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
