##     Overview of records:

All records start with `page sequence` and `record type`. The `page sequence` separates individual contests and other election metadata. `record type` will indicate how to parse.

__page sequence 000:__

* contains Election Title (ET) and Time and Date (TD) records

__page sequence 001:__

* contains Election Statistics (ST) and Party Statistics (PS)

__page sequence ###:__

Most other page sequences should represent individual contests.

__page sequence 999:__

* end of file marker

__CSV Schema: Universal__
```
column,start,length
page_sequence,0,3
record_type,3,2
```

##     Election Title record:

_Record code: "ET"_

* First record in file
* Multiple records (approximately 5)
* Each record contains different text/info: name of election, county/department titles, type of results, election date, etc.

**Format:**

                  1          2         3         4         5         6          7         8         9
      123 45 6789 012345 67890123456789012345678901234567890123456789012345678 901234567890123456789012345
     |---|--|----|------|-----------------------------------------------------|---------------------------|
      ^   ^  ^    ^      ^                                                     ^
      |   |  |    |      |                                                     filler: 27 characters
      |   |  |    |      election text: 53 characters
      |   |  |    filler: 6 characters
      |   |  election Id: 4 characters
      |   record type: 2 characters "ET"
      page sequence:  3 digits "000"

**Example:**

```
000ET1215      County of Los Angeles
000ET1215      Department of Registrar-Recorder/County Clerk
000ET1215      Semi-Official Election Returns
000ET1215      June 4, 1996 - Test Election
```

__CSV schema: ET__

```
column,start,length
page_sequence,0,3
record_type,3,2
election_Id,5,4
election_text,15,53
```

##     Time & Date record:

_Record code: "TD"_

* One per election
* This is the time stamp for last update
* Vote counts and percentages on specific contests will be valid as of the value in this record

__Format:__

                  1          2           3          4         5         6         7         8         9
      123 45 6789 012345 67890 1 2345678901 2345678901234567890123456789012345678901234567890123456789012345
     |---|--|----|------|-----|-|----------|----------------------------------------------------------------|
      ^   ^  ^    ^      ^     ^ ^          ^
      |   |  |    |      |     | |          filler: 64 characters
      |   |  |    |      |     | date 10 characters "mm/dd/yyyy"
      |   |  |    |      |     filler: 1 digit
      |   |  |    |      time 5 characters "hh:mm"
      |   |  |    filler: 6 characters
      |   |  election Id: 4 characters
      |   record type: 2 characters "TD"
      page sequence:  3 digits "000"

__Example:__

```
000TD1215      AS OF 17:15 04/07/1998
```

__CSV Schema: TD__

```
column,start,length
page sequence,0,3
record type,3,2
election Id,5,4
time,15,5
date,21,10
```

##     Election Statistics record:

_Record code: "ST"_

* Statistical overview of the entire election
* It will have related records for precinct reporting, absentee ballots cast, etc., which reflect election-wide stats, rather than contest-specific stats. They should be linked to this record by contest ID. Example contest ID: "STAT"

__Format:__

                  1          2         3         4           5         6         7          8         9
      123 45 6789 012345 67890123456789012345678901 234 56789012345678901234567890 1234567890123456789012345
     |---|--|----|------|--------------------------|---|--------------------------|-------------------------|
      ^   ^  ^    ^      ^                          ^   ^                          ^
      |   |  |    |      |                          |   |                          filler: 25 characters
      |   |  |    |      |                          |   statistical text continued: 26 characters
      |   |  |    |      |                          filler: 3 character
      |   |  |    |      statistical text: 26 characters
      |   |  |    filler: 6 characters
      |   |  election Id: 4 characters
      |   record type: 2 characters "ST"
      page sequence: 3 digits

__Example:__

```
001STSTAT      COUNTYWIDE STATISTICS        PRIMARY ELECTION
```

__CSV Schema: ST__

```
column,start,length
page sequence,0,3
record type,3,2
election Id,5,4
statistical text,15,26
statistical text continued,44,26
```

##     Candidate Contest record:

_Record code: "CC"_

* One per contest
* text describes the contest

__Format:__

                  1            2         3         4           5         6         7          8         9
      123 45 6789 01 234 5 67890123456789012345678901 234 56789012345678901234567890 1234567890123456789012345
     |---|--|----|--|---|-|--------------------------|---|--------------------------|-------------------------|
      ^   ^  ^    ^  ^   ^ ^                          ^   ^                          ^
      |   |  |    |  |   | |                          |   |                          filler: 25 characters
      |   |  |    |  |   | |                          |   contest title continued: 26 characters
      |   |  |    |  |   | |                          filler: 3 character
      |   |  |    |  |   | contest title: 26 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "CC"
      page sequence: 3 digits

__Example:__

```
010CCCD  29    U.S. REPRESENTATIVE          29TH DISTRICT
```

__CSV Schema: CC__

```
column,start,length
page sequence,0,3
record type,3,2
contest Id,5,4
district,9,2
division,11,3
party code,14,1
contest title,15,26
contest title continued,44,26
```

##     Measure Contest record:

_Record code: "MC"_

* One per contest
* text describes the contest

__Format:__

                  1            2         3         4           5         6         7          8         9
      123 45 6789 01 234 5 67890123456789012345678901 234 56789012345678901234567890 1234567890123456789012345
     |---|--|----|--|---|-|--------------------------|---|--------------------------|-------------------------|
      ^   ^  ^    ^  ^   ^ ^                          ^   ^                          ^
      |   |  |    |  |   | |                          |   |                          filler: 25 characters
      |   |  |    |  |   | |                          |   contest title continued: 26 characters
      |   |  |    |  |   | |                          filler: 3 character
      |   |  |    |  |   | contest title: 26 characters
      |   |  |    |  |   filler: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "MC"
      page sequence: 3 digits

__Example:__

```
032MCCM        COUNTY MEASURE
```

__CSV Schema: MC__

```
column,start,length
page sequence,0,3
record type,3,2
contest Id,5,4
district,9,2
division,11,3
contest title,15,26
contest title continued,44,26
```

##     Judicial Contest record:

_Record code: "JC"_

* One per contest
* text describes the contest

__Format:__

                  1            2         3         4           5         6         7          8         9
      123 45 6789 01 234 5 67890123456789012345678901 234 56789012345678901234567890 1234567890123456789012345
     |---|--|----|--|---|-|--------------------------|---|--------------------------|-------------------------|
      ^   ^  ^    ^  ^   ^ ^                          ^   ^                          ^
      |   |  |    |  |   | |                          |   |                          filler: 25 characters
      |   |  |    |  |   | |                          |   contest title continued: 26 characters
      |   |  |    |  |   | |                          filler: 3 character
      |   |  |    |  |   | contest title: 26 characters
      |   |  |    |  |   filler: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "JC"
      page sequence: 3 digits

__Example:__

```
030JCAC        APPELLATE COURT JUSTICES
```

__CSV Schema: JC__
```
column,start,length
page sequence,0,3
record type,3,2
contest Id,5,4
district,9,2
division,11,3
contest title,15,26
contest title continued,44,26
```

##     Party record:

_Record code: "PT"_

* text is party name
* optional
* up to 8 per partisan candidate contest

__Format:__

                  1            2         3         4          5         6         7         8         9
      123 45 6789 01 234 5 67890123456789012345678901 234567890123456789012345678901234567890123456789012345
     |---|--|----|--|---|-|--------------------------|------------------------------------------------------|
      ^   ^  ^    ^  ^   ^ ^                          ^
      |   |  |    |  |   | |                          filler: 54 character
      |   |  |    |  |   | party name: 26 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "PT"
      page sequence: 3 digits

__Example:__

```
022PTSD  17   3REPUBLICAN
```

__CSV Schema: PT__
```
column,start,length
page sequence,0,3
record type,3,2
contest Id,5,4
district,9,2
division,11,3
party code,14,1
party name,15,26
```

##     Vote For record:

_Record code: "VF"_

* This is the number of votes allowed for this contest
* optional: when present, only one per contest

__Format:__

                  1            2         3          4         5         6         7         8         9
      123 45 6789 01 234 5 6789012345678901234567 890 1234567890123456789012345678901234567890123456789012345
     |---|--|----|--|---|-|----------------------|---|--------------------------------------------------------|
      ^   ^  ^    ^  ^   ^ ^                      ^   ^
      |   |  |    |  |   | |                      |   filler: 55 character
      |   |  |    |  |   | |                      vote for number: 3 character "ZZ9"
      |   |  |    |  |   | vote for text: 22 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "VF"
      page sequence: 3 digits

__Example: N/A__

__CSV Schema: VF__
```
column,start,length
page sequence,0,3
record type,3,2
contest Id,5,4
district,9,2
division,11,3
party code,14,1
vote for text,15,22
vote for number,37,3
```

##     Candidate Name record:

_Record code: "CN"_

* Vote % = votes received / cast

__Format:__

                  1             2         3          4           5         6         7   
      123 45 6789 01 234 5 678 901234567890123456 78901 234 56789012345678901234567890123
     |---|--|----|--|---|-|---|------------------|-----|---|-----------------------------|
      ^   ^  ^    ^  ^   ^     ^                  ^     ^   ^
      |   |  |    |  |   |     |                  |     |   filler: 29 character
      |   |  |    |  |   |     |                  |     party short: 3 character
      |   |  |    |  |   |     |                  filler: 5 characters
      |   |  |    |  |   |     candidate name: 18 characters
      |   |  |    |  |   | filler: 3 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "CN"
      page sequence: 3 digits

            8           9
      456789012 345 678901 2345
     |---------|---|------|----|
      ^         ^   ^      ^
      |         |   |      filler: 4 characters
      |         |   percent of the vote 6 characters "ZZ9.99"
      |         filler: 3 characters
      votes: 9 characters "Z,ZZZ,ZZ9"

__Example:__

```
033CNDA           GIL GARCETTI                                           Z,ZZZ,ZZ9   ZZ9.99
```

__CSV Schema: CN__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
party_code,14,1
candidate_name,18,18
party_short,41,3
votes,73,9
percent_of_vote,85,6
```

##     Measure text record:

_Record code: "MT"_

* measure ID = individual measure
* Each measure has a pair of records (1 for yes, 1 for no)

__Format:__

                  1             2           3         4         5          6         7
      123 45 6789 01 234 5 678 9012 345 67890123456789012345678901234567 8901234567890123
     |---|--|----|--|---|-|---|----|---|--------------------------------|----------------|
      ^   ^  ^    ^  ^   ^ ^   ^    ^   ^                                ^
      |   |  |    |  |   | |   |    |   |                                filler: 16 character
      |   |  |    |  |   | |   |    |   measure text: 32 characters
      |   |  |    |  |   | |   |    filler: 3 characters " - "
      |   |  |    |  |   | |   measure Id: 4 characters
      |   |  |    |  |   | filler: 3 characters
      |   |  |    |  |   filler: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "MT"
      page sequence: 3 digits

            8           9
      456789012 345 678901 2345
     |---------|---|------|----|
      ^         ^   ^      ^
      |         |   |      filler: 4 characters
      |         |   percent of vote 6 characters "ZZ9.99"
      |         filler: 3 characters
      votes: 9 characters "Z,ZZZ,ZZ9"

__Example:__

```
054MTCITYAL          A - CHARTER-SCH DIST REORG    - YES                 Z,ZZZ,ZZ9   ZZ9.99
054MTCITYAL                                        - NO                  Z,ZZZ,ZZ9   ZZ9.99
```

__CSV Schema: MT__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
measure_Id,18,4
measure_text,25,32
votes,73,9
percent_of_vote,85,6
```

##     Judicial Name record:

_Record code: "JN"_

* Each judge has a pair of records (1 for yes, 1 for no)
* Vote %: vote value / votes cast per judge

__Format:__

                  1             2         3         4           5         6            7
      123 45 6789 01 234 5 678 90123456789012345678901234 5 678901234567890123 456 789 0123
     |---|--|----|--|---|-|---|--------------------------|-|------------------|---|---|----|
      ^   ^  ^    ^  ^   ^     ^                          ^ ^                  ^   ^   ^
      |   |  |    |  |   |     |                          | |                  |   |   filler: 4 characters
      |   |  |    |  |   |     |                          | |                  |   voting rule: 3 characters
      |   |  |    |  |   |     |                          | |                  filler: 3 characters " - "
      |   |  |    |  |   |     |                          | judicial name: 18 character
      |   |  |    |  |   |     |                          filler: 1 characters
      |   |  |    |  |   |     judicial text: 26 characters
      |   |  |    |  |   | filler: 3 characters
      |   |  |    |  |   filler: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "JN"
      page sequence: 3 digits

            8           9
      456789012 345 678901 2345
     |---------|---|------|----|
      ^         ^   ^      ^
      |         |   |      filler: 4 characters
      |         |   percent of the vote 6 characters "ZZ9.99"
      |         filler: 3 characters
      votes: 9 characters "Z,ZZZ,ZZ9"

__Example:__

```
029JNSC           ASSOCIATE JUSTICE          JOYCE L KENNARD    - YES    Z,ZZZ,ZZ9   ZZ9.99
029JNSC                                                         - NO     Z,ZZZ,ZZ9   ZZ9.99
```

__CSV Schema: JN__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
judicial_text,18,26
judicial_name,45,18
voting_rule,66,3
votes,73,9
percent_of_vote,85,6
```

##     Precinct Reporting record:

_Record code: "PR"_

* One per CC, MC or JC contest

__Format:__

                  1            2         3           4          5   
      123 45 6789 01 234 5 67890123456789012345 6 78901 234567890123
     |---|--|----|--|---|-|--------------------|-|-----|------------|
      ^   ^  ^    ^  ^   ^ ^                   ^  ^     ^           
      |   |  |    |  |   | |                   |  |     filler: 12 characters
      |   |  |    |  |   | |                   |  total precincts: 5 characters "Z,ZZ9"
      |   |  |    |  |   | |                   filler: 1 characters
      |   |  |    |  |   | total precinct text: 20 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "PR"
      page sequence: 3 digits

            6         7           8           9
      45678901234567890123 4567 89012 345 678901 2345
     |--------------------|----|-----|---|------|----|
      ^                    ^    ^     ^   ^      ^
      |                    |    |     |   |      filler: 4 characters
      |                    |    |     |   percent of precincts reporting 6 characters "ZZ9.99"
      |                    |    |     filler: 3 characters
      |                    |    precincts reporting: 5 digits "Z,ZZ9"
      |                    filler 4 characters
      precincts reporting text: 20 characters

__Example:__

```
030PRAC        TOTAL PRECINCTS      Z,ZZ9            PRECINCTS REPORTING     Z,ZZ9   ZZ9.99
```

__CSV Schema: PR__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
party_code,14,1
total_precinct_text,15,20
total_precincts,36,5
precincts_reporting_text,53,20
precincts_reporting,77,5
percent_precincts_reporting,85,6
```

##     District Registration record:

_Record code: "DR"_

* One per CC, MC or JC contest

__Format:__

                  1            2         3           4          5         6         7         8         9
      123 45 6789 01 234 5 6789012345678901 2 345678901 234567890123456789012345678901234567890123456789012345
     |---|--|----|--|---|-|----------------|-|---------|------------------------------------------------------|
      ^   ^  ^    ^  ^   ^ ^                ^ ^         ^
      |   |  |    |  |   | |                | |         filler: 54 characters
      |   |  |    |  |   | |                | registration: 9 characters "Z,ZZZ,ZZ9"
      |   |  |    |  |   | |                filler: 1 character
      |   |  |    |  |   | registration text: 16 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "DR"
      page sequence: 3 digits

__Example:__

```
032DRCM        REGISTRATION     Z,ZZZ,ZZ9
```

__CSV Schema: DR__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
party code,14,1
registration text,15,16
registration,32,9
```

##     Party Statistics record:

_Record code: "PS"_

* Supports Election Statistics record
* primary elections only
* Percent voter turnout = votes cast / registration

__Format:__

                  1            2         3          4           5         6         7
      123 45 6789 01 234 5 67890123456789012 345678901 234 56789012345678901234567890
     |---|--|----|--|---|-|-----------------|---------|---|--------------------------|
      ^   ^  ^    ^  ^   ^ ^                 ^         ^   ^
      |   |  |    |  |   | |                 |         |   party name: 26 characters
      |   |  |    |  |   | |                 |         filler: 3 characters
      |   |  |    |  |   | |                 registration: 9 characters "Z,ZZZ,ZZ9"
      |   |  |    |  |   | filler: 17 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "PS"
      page sequence: 3 digits

                 8           9
      12 3 456789012 345 678901 2345
     |--|-|---------|---|------|----|
      ^  ^ ^         ^   ^      ^
      |  | |         |   |      filler: 4 characters
      |  | |         |   percent of turnout 6 characters "ZZ9.99"
      |  | |         filler: 3 characters
      |  | ballots cast: 9 characters "Z,ZZZ,ZZ9"
      filler: 2 character

__Example:__

```
001PSSTAT                       Z,ZZZ,ZZ9   REPUBLICAN                   Z,ZZZ,ZZ9   ZZ9.99
```

__CSV Schema: PS__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
party_code,14,1
registration,32,9
party_name,44,26
ballots_cast,72,9
percent_turnout,84,6
```

##     Absentee Ballots Cast record:

_Record code: "AB"_

* Supports Election Statistics record

__Format:__

                  1            2         3         4         5
      123 45 6789 01 234 5 6789012345678901234567890123456789012345678 
     |---|--|----|--|---|-|-------------------------------------------|
      ^   ^  ^    ^  ^   ^ ^                                           
      |   |  |    |  |   | filler: 43 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "AB"
      page sequence: 3 digits

       6         7              8          9
      90123456789012 3 456789012 3456789012345
     |--------------|-|---------|-------------|
      ^              ^ ^         ^
      |              | |         filler: 13 characters
      |              | absentee total: 9 characters "Z,ZZZ,ZZ9"
      |              filler: 1 character
      absentee total text: 14 characters

__Example:__

```
001ABSTAT                                                 ABSENTEE TOTAL Z,ZZZ,ZZ9
```

__CSV Schema: AB__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
party_code,14,1
absentee_total_text,58,14
absentee_total,73,9
```

##     Ballots Cast record:

_Record code: "BC"_

* Supports Election Statistics record
* percentage voter turnout = votes cast / registration

__Format:__

                  1            2         3         4         5  
      123 45 6789 01 234 5 6789012345678901234567890123456789012
     |---|--|----|--|---|-|-------------------------------------|
      ^   ^  ^    ^  ^   ^ ^                                    
      |   |  |    |  |   | filler: 37 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "BC"
      page sequence: 3 digits

             6         7           8           9
      34567890123456789012 3 456789012 345 678901 2345
     |--------------------|-|---------|---|------|----|
      ^                    ^ ^         ^   ^      ^
      |                    | |         |   |      filler: 4 characters
      |                    | |         |   percent of turnout 6 characters "ZZ9.99"
      |                    | |         filler: 3 characters
      |                    | ballots cast: 9 characters "Z,ZZZ,ZZ9"
      |filler: 1 character
      ballots cast text: 20 characters

__Example:__

```
001BCSTAT                                           BALLOTS CAST/TURNOUT Z,ZZZ,ZZ9   ZZ9.99
```

__CSV Schema: BC__
```
column,start,length
page_sequence,0,3
record_type,3,2
contest_Id,5,4
district,9,2
division,11,3
party_code,14,1
ballots_cast_text,52,20
ballots_cast,73,9
percent_turnout,85,6
```

##     Blank record:

_Record code: "BK"_

* contain no data, used for readability

__Format:__

                  1            2         3         4         5         6         7         8         9
      123 45 6789 01 234 5 67890123456789012345678901234567890123456789012345678901234567890123456789012345
     |---|--|----|--|---|-|--------------------------------------------------------------------------------|
      ^   ^  ^    ^  ^   ^ ^
      |   |  |    |  |   | filler: 80 characters
      |   |  |    |  |   party code: 1 character
      |   |  |    |  division: 3 characters
      |   |  |    district: 2 characters
      |   |  contest Id: 4 characters
      |   record type: 2 characters "BK"
      page sequence: 3 digits

__Example:__

```
007BKCD  26
```

##     End of File record:

_Record code: "EF"_

* total number of records in file, including itself

__Format:__

                  1           2         3         4          5         6         7        8         9
      123 45 6789 012345 6789 0123456789012345678901234567890123456789012345678901234567890123456789012345
     |---|--|----|------|----|----------------------------------------------------------------------------|
      ^   ^  ^    ^      ^    ^
      |   |  |    |      |    filler: 76 characters
      |   |  |    |      total records: 4 characters
      |   |  |    filler: 6 characters
      |   |  election Id: 4 characters
      |   record type: 2 characters "EF"
      page sequence: 3 digits "999"

__Example:__

```
999EF1215       716
```
