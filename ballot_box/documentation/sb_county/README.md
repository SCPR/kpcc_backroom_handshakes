San Bernardino County Election Night Data-Feed Information
==================================================================

* [Contact](#contact)
* [Raw data results page](#raw-data-results-page)
* [What's covered?](#whats-covered)
* [Documentation](#documentation)

Contact
-------

**Technical questions**

NA

**General media questions**

Melissa Eickman
[Melissa.Eickman@rov.sbcounty.gov](mailto:Melissa.Eickman@rov.sbcounty.gov)
909-387-2002

Raw data results page
---------------------

[http://www.sbcounty.gov/rov/elections/Results/](http://www.sbcounty.gov/rov/elections/Results/)

What's covered?
---------------

* The county often oversees elections for cities, but cities can opt out. Need to confirm whether any cities have opted out in a given election.

Overview of records
-------------------

### Field Names

*The data will come as tab-separated values with the following column headers (field names):*

__CONTEST_ID__

__CONTEST_ORDER:__ Order the contest appears in results.

__CANDIDATE_ORDER:__ Order the candidate/measure appears on the ballot

__TOTAL:__ Votes cast for this candidate or measure. _Note: Vote percent must be calculated by dividing "TOTAL" by "CONTEST_TOTAL"_

__CANDIDATE_PARTY_ID__

__CANDIDATE_ID__

__VOTE_FOR:__ Total number of candidates to be selected in multiple-winner contest.

__CONTEST_TYPE:__ 0 = candidate. 4 = ballot measure. -# = voter registration & turnout.

__CANDIDATE_TYPE:__ 0 = regular candidate (or voter turnout/registration?). 4 = ballot measure. Almost identical to "CONTEST_TYPE"

__TOTAL_PRECINCTS:__ Total # of precincts for this contest

__PROCESSED_DONE:__ # of precincts that have been counted. Note: Percent precincts reporting must be calculated by dividing "PROCESSED_DONE" by "TOTAL_PRECINCTS"

__PROCESSED_STARTED:__ Unclear still how this is different from "PROCESSED_DONE"

__IS_WRITEIN_CANDIDATE__

__CONTEST_FULL_NAME__

__CANDIDATE_FULL_NAME:__ For ballot measures, this will be used to designate a "yes" vote record vs. a "no" vote record.

__CONTEST_TOTAL:__ Total votes cast in this particular contest. _Note: Vote percent must be calculated by dividing "TOTAL" by "CONTEST_TOTAL"_

__undervote:__ Probably won't use (I believe this is when a voter doesn't make a choice in a contest or selects fewer than the number of candidates allowed in a multi-winner contest (i.e. "Vote for 3 city council members"))

__overvote:__ Probably won't use (I believe this is when a voter picks more than the number of acceptable candidates in an election — i.e. voting for two presidential candidates when only one choice is allowed. It would be a spoiled vote and not counted)

__IS_WINNER:__ Values are "0" or "1" (no or yes)

__cf_cand_class:__ Values are "candidate" or "winner"

__IS_PRECINCT_LEVEL:__ Not sure yet how this one is used

__PRECINCT_NAME__

__is_visible:__ Not sure how this one is used

### Example record

```
12	11	6	381	1	59	1	0	0	1772	1772	1772	0	AI - Presidential Preference	ARTHUR HARRIS	2282	2415	9	0	candidate	0		0
```

### Candidates vs. Measures

Candidates come in a single record.

Measures will be split across two records — one for "yes" votes and one for "no" votes, as indicated by "YES" or "NO" in the "CANDIDATE_FULL_NAME" field.