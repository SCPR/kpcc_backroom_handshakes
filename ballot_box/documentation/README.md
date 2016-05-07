Modeling The Data
=================

Election
---------

Describes the macro unit of data for a single election

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

Contest
-------

Describes the contests that make up an election ballot

* **election**: ForeignKey to an Election
    - Example: primary-2016-06-07
* **resultsource**: ForeignKey to a ResultSource
    - Example: secretary-of-state
* **contesttype**: Level of race
    - Example: statewide, congressional district, city council district,

* **contestid**: Created from type of race & the electionid
    - Example: congressional-primary-2016-06-07
* **officeid**:
    - Example: us_house_dist_8

* **contestname**:
    - Example: U.S. House of Representatives District 8
* **seatnum**: Number of district or seat up for grabs
    - Example: 8
* **uncontested**: Is this an uncontested race?
    - Example: True/False
* **national**: Is this a National Race?
    - Example: True/False
* **statewide**: Is this a Statewide Race?
    - Example: True/False
* **is_ballot_measure**: Is this a ballot measure, proposition or initiative?
    - Example: True/False
* **is_judicial**: Is this a ballot measure?
    - Example: True/False
* **is_runoff**: Is this a runoff race?
    - Example: True/False
* ~~**candidates**:~~
* ~~**reportingunits**:~~
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

----

Candidate
---------

* **contest**: ForeignKey to an Contest
* **candidateid**:
* **ballotorder**:
* **first**:
* **last**:
* **party**:
* **incumbent**:
* **votecount**:
* **votepct**:
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

----

BallotMeasure
-------------

* **contest**: ForeignKey to an Contest
* **measureid**:
* **ballotorder**:
* **description**:
* **yescount**:
* **yespct**:
* **nocount**:
* **nopct**:
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

----

ReportingUnit
-------------

* **election**: ForeignKey to an Election
    - Example: primary-2016-06-07
* **contest**: ForeignKey to a Contest
    - Example: primary-2016-06-07
* **reportingunitid**:
* **reportingunitname**:
* **delegatecount**:
* **winner**:
* **fipscode**:
* **precinctstotal**:
* **precinctsreporting**:
* **precinctsreportingpct**:
* **votersregistered**:
* **votersturnout**:
* **statepostal**:
* **statename**:
* **description**:
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000
