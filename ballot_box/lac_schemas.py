class FixedWidthField(object):
    def __init__(self, index, length, transform=None):
        self.index = index
        self.length = length
        self.transform = transform
        self.name = None

    def parse(self, s):
        try:
            s_decoded = s.decode('utf-8')
        except UnicodeEncodeError:
            s_decoded = s

        val = s_decoded[self.index:self.index + self.length]
        val = val.strip()
        if self.transform is None:
            return val
        else:
            try:
                return self.transform(val)
            except ValueError:
                return None

class FixedWidthParserMeta(type):
    def __new__(cls, name, parents, dct):
        dct['_fields'] = []
        for k, v in dct.items():
            if isinstance(v, FixedWidthField):
                v.name = k
                dct['_fields'].append(v)
                del dct[k]

        new_cls = super(FixedWidthParserMeta, cls).__new__(cls, name, parents, dct)
        return new_cls

class FixedWidthParser(object):
    __metaclass__ = FixedWidthParserMeta

    def parse_line(self, line):
        attrs = {}
        for field in self._fields:
            attrs[field.name] = field.parse(line)

        return attrs 

# RECORD SCHEMAS
# ==============
# format is (index, length, opt:transform=int)

class ET_record(FixedWidthParser):
    # Election Title record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    election_id = FixedWidthField(5, 4)
    election_text = FixedWidthField(15, 53)

class TD_record(FixedWidthParser):
    # Time and Date record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    election_id = FixedWidthField(5, 4)
    time = FixedWidthField(15, 5)
    date = FixedWidthField(21, 10)

class ST_record(FixedWidthParser):
    # Election Statistics record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    election_id = FixedWidthField(5, 4)
    statistical_text = FixedWidthField(15, 26)
    statistical_text_cont = FixedWidthField(44, 26)

class CC_record(FixedWidthParser):
    # Candidate Contest record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    contest_title = FixedWidthField(15, 26)
    contest_title_cont = FixedWidthField(44, 26)

class MC_record(FixedWidthParser):
    # Measure Contest record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    contest_title = FixedWidthField(15, 26)
    contest_title_cont = FixedWidthField(44, 26)

class JC_record(FixedWidthParser):
    # Judicial Contest record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    contest_title = FixedWidthField(15, 26)
    contest_title_cont = FixedWidthField(44, 26)
    page_sequence = FixedWidthField(0, 3)

class PT_record(FixedWidthParser):
    # Party Title record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    party_name = FixedWidthField(15, 26)

class VF_record(FixedWidthParser):
    # Vote For record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    vote_for_text = FixedWidthField(15, 22)
    vote_for_number = FixedWidthField(37, 3)

class CN_record(FixedWidthParser):
    # Candidate Name record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    candidate_name = FixedWidthField(18, 18)
    party_short = FixedWidthField(41, 3)
    votes = FixedWidthField(73, 9)
    percent_of_vote = FixedWidthField(85, 6)

class MT_record(FixedWidthParser):
    # Measure Text record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    measure_id = FixedWidthField(18, 4)
    measure_text = FixedWidthField(25, 32)
    votes = FixedWidthField(73, 9)
    percent_of_vote = FixedWidthField(85, 6)

class JN_record(FixedWidthParser):
    # Judge Name record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    judicial_text = FixedWidthField(18, 26)
    judicial_name = FixedWidthField(45, 18)
    voting_rule = FixedWidthField(66, 3)
    votes = FixedWidthField(73, 9)
    percent_of_vote = FixedWidthField(85, 6)

class PR_record(FixedWidthParser):
    # Precinct Reporting record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    total_precinct_text = FixedWidthField(15, 20)
    total_precincts = FixedWidthField(36, 5)
    precincts_reporting_text = FixedWidthField(53, 20)
    precincts_reporting = FixedWidthField(77, 5)
    percent_precincts_reporting = FixedWidthField(85, 6)

class DR_record(FixedWidthParser):
    # District Registration record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    registration_text = FixedWidthField(15, 16)
    registration = FixedWidthField(32, 9)

class PS_record(FixedWidthParser):
    # Party Statistical record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    registration = FixedWidthField(32, 9)
    party_name = FixedWidthField(44, 26)
    ballots_cast = FixedWidthField(72, 9)
    percent_turnout = FixedWidthField(84, 6)

class AB_record(FixedWidthParser):
    # Absentee Ballots Cast record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    absentee_total_text = FixedWidthField(58, 14)
    absentee_total = FixedWidthField(73, 9)

class BC_record(FixedWidthParser):
    # Ballots Cast record
    page_sequence = FixedWidthField(0, 3)
    record_type = FixedWidthField(3, 2)
    contest_id = FixedWidthField(5, 4)
    district = FixedWidthField(9, 2)
    division = FixedWidthField(11, 3)
    party_code = FixedWidthField(14, 1)
    ballots_cast_text = FixedWidthField(52, 20)
    ballots_cast = FixedWidthField(73, 9)
    percent_turnout = FixedWidthField(85, 6)