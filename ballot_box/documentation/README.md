Ballot Box
==========

* [About](#about)
* [Modeling The Data](#modeling-the-data)
* [Data Sources](#data-sources)

About
======

Let's share a little bit about this project...

Data Sources
============

* [California Secretary of State Election Night Data-Feed Information](calif_secretary_of_state)
* [Los Angeles County Election Night Data-Feed Information](la_county)

Modeling The Data
=================

Xxxxxxxxx xxx xxxxx

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
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

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
* **source_files**: When applicable, comma-separated list of the target files
    - Example: "X14GG510v7.xml"
* **source_created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **source_modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

Contest
-------

Describes the contests that make up an election ballot

* **election**: ForeignKey to an Election
    - Example: primary-2016-06-07
* **resultsource**: ForeignKey to a ResultSource
    - Example: secretary-of-state
* **office**: ForeignKey to an Office
    - Example: Attorney General
* **contestid**: election id, data source, office name & seat number
    - Example: primary-2016-06-07-sos-statewide-attorney-general-0000
* **contestname**:
    - Example: U.S. House of Representatives District 8
* **seatnum**: Number of district or seat up for grabs
    - Example: 8
* **contestdescription**: Provides space for user-facing description
    - Example: Currently None
* **is_uncontested**: Is this an uncontested race?
    - Example: True/False
* **is_national**: Is this a National Race?
    - Example: True/False
* **is_statewide**: Is this a Statewide Race?
    - Example: True/False
* **is_ballot_measure**: Is this a ballot measure, proposition or initiative?
    - Example: True/False
* **is_judicial**: Is this a ballot measure?
    - Example: True/False
* **is_runoff**: Is this a runoff race?
    - Example: True/False
* **precinctstotal**: Total Number Of Precincts
    - Example: 5800
* **precinctsreporting**: Number Of Precincts Reporting Votes
    - Example: 500
* **precinctsreportingpct**: Percent Of Precincts Reporting
    - Example: 0.0862
* **votersregistered**: Number of Registered Voters
    - Example: 100
* **votersturnout**: Percent Voters Who Cast Ballots
    - Example: 0.43
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

----

Candidate
---------

* **contest**: ForeignKey to an Contest
* **candidateid**: candidate name, election id, data source, office name & seat number
- Example: kamala-d-harris-primary-2016-06-07-sos-statewide-attorney-general-0000
* **ballotorder**: Numerical Position On The Ballot
    - Example: Currently None
* **first**: Candidate's First Name
    - Example: Kamala
* **last**: Candidate's Last Name
    - Example: Harris
* **fullname**: Candidate's Full Name
    - Example: Kamala Harris
* **party**: Candidate's Political Party
    - Example: Democrat
* **incumbent**: Is Candidate An Incumbent?
    - Example: True/False
* **votecount**: Votes Received
    - Example: 100
* **votepct**: Percent Of Total Votes
    - Example:  0.43
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

BallotMeasure
-------------

* **contest**: ForeignKey to an Contest
    - Example: Criminal Sentences, Misdemeanor Penalties
* **measureid**:
    - Example: criminal-sentences,-misdemeanor-penalties-primary-2016-06-07-sos-california-measure-criminal-sentences,-misdemeanor-penalties-0047
* **ballotorder**: Numerical Position On The Ballot
    - Example: Currently None
* **fullname**: Name of Ballot Measure
    - Example: Criminal Sentences, Misdemeanor Penalties
* **description**: Provides space for user-facing description of ballot measure
    - Example: Currently None
* **yescount**: Number Of Yes Votes Received
    - Example: 118
* **yespct**: Percent Of Yes Votes Received
    - Example: 0.7375
* **nocount**: Number Of Yes Votes Received
    - Example: 42
* **nopct**: Percent Of Yes Votes Received
    - Example: 0.2625
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000

JudicialCandidate
-------------

* **contest**: ForeignKey to an Contest
    - Example: Supreme Court Justice
* **judgeid**: fullname, contestid
    - Example: goodwin-liu-primary-2016-06-07-sos-california-supreme-court-justice-0002
* **ballotorder**: Numerical Position On The Ballot
    - Example: Currently None
* **first**: Candidate's First Name
    - Example: Kamala
* **last**: Candidate's Last Name
    - Example: Harris
* **fullname**: Candidate's Full Name
    - Example: Kamala Kamala
* **yescount**: Number Of Yes Votes Received
    - Example: 118
* **yespct**: Percent Of Yes Votes Received
    - Example: 0.7375
* **nocount**: Number Of Yes Votes Received
    - Example: 42
* **nopct**: Percent Of Yes Votes Received
    - Example: 0.2625
* **created**: Date and time a record was created
    - Example: 2016-06-08 03:00:00.000000
* **modified**: Date and time a record was modified
    - Example: 2016-06-08 03:00:00.000000
