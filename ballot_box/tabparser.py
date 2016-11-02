import csv

class ParseTabDelimited(object):
    """ Converts tab-delimited rows into dictionaries and adds them to a list """
    dictionaries = []
    def __init__(self, file):

        with open(file) as tsvfile:
            records = csv.DictReader(tsvfile,dialect="excel-tab")
            for row in records:
                self.dictionaries.append(row)

class DelimitedObject(object):
    """ Not currently being used """
    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)