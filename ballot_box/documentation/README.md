Modeling The Data
=================

Election
---------

For our purposes the macro unit of data.

* **type**: The type of election
    - Example: "Primary", "General", "Special"
* **electionid**: Created from type of election & the date of election
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

----

ResultSource
-------------

Describes a source of election results data

* **election**: ForeignKey to an Election
    - Example: primary-2016-06-07
* **source_name**: Name of data source
    - Example: Secretary of State
* **source_short**: Shortname of data source
    - Example: sos
* **source_slug**: Slugged data source
    - Example: secretary-of-state
* **source_url**: URL to data source
    - Example: http://cms.cdn.sos.ca.gov/media/14GG/X14GGv7.zip
* **source_active**: Active data source
    - Example: True/False
* **source_type**: Ext of file or type of source
    - Example: .zip
* **source_files**: Results Files We Want
    - Example: When applicable, comma-separated list of the target files
* **source_created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **source_modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

----

Race
-----

Xxxxxxxxxxxxxxxx

* **Office vs. Seat?**

----

* **election**: ForeignKey to an Election
    - Example: primary-2016-06-07
* **resultsource**: ForeignKey to a ResultSource
* **raceid**:
* **racetype**:
* **party**:
* **officeid**:
    - Example: us_house_dist_8
* **officename**:
    - Example: U.S. House of Representatives District 8
* ~~**seatname**:~~
* ~~**seatnum**:~~
* **description**:
* **uncontested**:
    - Example: True/False
* **national**:
    - Example: True/False
* **statewide**:
    - Example: True/False
* **is_ballot_measure**:
    - Example: True/False
* **is_judicial**:
    - Example: True/False
* **is_runoff**:
    - Example: True/False

* **candidates**:

* **reportingunits**:

* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000













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
